"""
Lambda function: update_batch_job_status

This Lambda will receive Batch job state change events through EventBridge and submit
them to the events API status update endpoint.
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

STATUS_MAP = {"FAILED": "Failed", "RUNNING": "Running", "SUCCEEDED": "Completed"}

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
    logger.info("Received Batch job state change event from EventBridge")

    try:
        detail = event["detail"]
        job_name: str = detail["jobName"]
        batch_job_id = detail["jobId"]
        raw_status = detail["status"]
        time_iso = event["time"]
    except KeyError:
        logger.error("Unexpected format -- could not parse job state change event")
        raise

    logger.info(
        "Event details: job_id=%s job_name=%s status=%s time=%s",
        batch_job_id,
        job_name,
        raw_status,
        time_iso,
    )

    try:
        status = STATUS_MAP[raw_status]
    except KeyError:
        logger.info("Ignoring unsupported Batch status: %s", raw_status)
        return

    internal_token = get_internal_token()

    headers = {
        "Content-Type": "application/json",
        "X-Internal-Token": internal_token,
    }

    payload = {"status": status, "event_time": time_iso}
    try:
        r = requests.post(
            f"{API_BASE_URL}/internal/batch-jobs/{batch_job_id}/status",
            headers=headers,
            json=payload,
            timeout=10,
        )
    except requests.RequestException:
        logger.exception("Failed to call events API")
        raise

    if not (200 <= r.status_code < 300):
        if r.status_code == 404:
            logger.info(
                "Events API has no job record for Batch job %s; ignoring status event",
                batch_job_id,
            )
            return
        logger.error(
            "Events API rejected message: %s %s",
            r.status_code,
            r.text,
        )
        raise RuntimeError("Events API rejected message")

    logger.info("Successfully processed Batch job state change event")
