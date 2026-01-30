"""
Lambda function: dispatch_job

This Lambda will receive messages from the events SQS queue through an event source
mapping and submit them to the events API's job dispatch endpoint.
"""

import json
import logging
import os

import boto3
from botocore.exceptions import ClientError
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

API_BASE_URL = os.environ["ALB_DNS_NAME"] + "/api"
APP_SECRETS_ARN = os.environ["APP_SECRETS_ARN"]

secrets_client = boto3.client("secretsmanager")
_cached_internal_token: str | None = None


def get_internal_token() -> str:
    global _cached_internal_token

    if _cached_internal_token:
        return _cached_internal_token

    try:
        resp = secrets_client.get_secret_value(SecretId=APP_SECRETS_ARN)
    except ClientError:
        logger.exception("Failed to retrieve app secrets from Secrets Manager")
        raise

    secret_string = resp.get("SecretString")
    if not secret_string:
        raise RuntimeError("App secrets 'SecretString' is empty")

    try:
        secret_obj = json.loads(secret_string)
        _cached_internal_token = secret_obj["APP_KEY"]
    except (json.JSONDecodeError, KeyError):
        logger.exception("App secrets do not contain APP_KEY")
        raise

    if not _cached_internal_token:
        raise RuntimeError("APP_KEY is not set")

    return _cached_internal_token


def lambda_handler(event, context):
    internal_token = get_internal_token()

    headers = {
        "Content-Type": "application/json",
        "X-Internal-Token": internal_token,
    }

    records = event.get("Records", [])
    logger.info("Received %d SQS messages", len(records))

    for record in records:
        body_raw = record["body"]

        try:
            body = json.loads(body_raw)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in SQS message body: %s", body_raw)
            raise

        try:
            r = requests.post(
                f"{API_BASE_URL}/internal/jobs/dispatch",
                headers=headers,
                json=body,
                timeout=10,
            )
        except requests.RequestException:
            logger.exception("Failed to call events API")
            raise

        if not (200 <= r.status_code < 300):
            logger.error(
                "Events API rejected message: %s %s",
                r.status_code,
                r.text,
            )
            raise RuntimeError("Events API rejected message")

    logger.info("Successfully processed all messages")
