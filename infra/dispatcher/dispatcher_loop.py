import os
import boto3
import json
import logging

from cwms_batch_events.core.job_database.postgres import session
from cwms_batch_events.core.job_database.postgres.postgres import PostgresJobDatabase
from cwms_batch_events.core.job_logger.s3 import S3JobLogger
from cwms_batch_events.core.models import JobMessage
from cwms_batch_events.local.dispatcher import LocalJobDispatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger()

logger.info("Starting the local job dispatcher (lambda mock)...")

sqs = boto3.client(
    "sqs",
    endpoint_url=os.environ.get("SQS_ENDPOINT_URL", "http://elasticmq:9324"),
    region_name="us-gov-west-1",
    aws_access_key_id="x",
    aws_secret_access_key="x",
)

QUEUE_URL = os.environ.get("QUEUE_URL", "")

job_logger = S3JobLogger()

while True:
    logger.info("Waiting for messages...")
    resp = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20,
    )

    for msg in resp.get("Messages", []):
        logger.info(f"Handling message: {msg}")
        body_raw = msg["Body"]

        try:
            message = JobMessage.model_validate_json(body_raw)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in SQS message body: %s", body_raw)
            raise

        try:
            db_session = session.create_session()
            db = PostgresJobDatabase(db=db_session)
            dispatcher = LocalJobDispatcher(db, job_logger)
            dispatcher.dispatch_job(message)

            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=msg["ReceiptHandle"],
            )

        finally:
            db_session.close()
