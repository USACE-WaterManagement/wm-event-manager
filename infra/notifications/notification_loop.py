import json
import logging
import os

import boto3

from cwms_batch_events.core.models import NotificationMessage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger()

logger.info("Starting the local notification worker (email lambda mock)...")

sqs = boto3.client(
    "sqs",
    endpoint_url="http://elasticmq:9324",
    region_name="us-gov-west-1",
    aws_access_key_id="x",
    aws_secret_access_key="x",
)

QUEUE_URL = os.environ.get("QUEUE_URL", "")

while True:
    logger.info("Waiting for notification messages...")
    resp = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20,
    )

    for msg in resp.get("Messages", []):
        body_raw = msg["Body"]

        try:
            notification = NotificationMessage.model_validate_json(body_raw)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in notification message body: %s", body_raw)
            raise

        logger.info(
            "Mock email send: template=%s office=%s severity=%s recipients=%s subject=%s body=%s data=%s",
            notification.template,
            notification.office,
            notification.severity,
            notification.recipients,
            notification.subject,
            notification.body,
            notification.data,
        )

        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=msg["ReceiptHandle"],
        )
