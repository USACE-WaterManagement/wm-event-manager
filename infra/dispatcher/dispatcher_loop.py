import boto3
import json
import logging
from cwms_batch_events.core.job_database.postgres import session
from cwms_batch_events.core.job_logger.s3 import S3JobLogger
from cwms_batch_events.core.models import JobMessage
from cwms_batch_events.core.processing import process_job_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger()

logger.info("Starting the local job dispatcher (lambda mock)...")

sqs = boto3.client(
    "sqs",
    endpoint_url="http://elasticmq:9324",
    region_name="us-gov-west-1",
    aws_access_key_id="x",
    aws_secret_access_key="x",
)

QUEUE_URL = "http://elasticmq:9324/000000000000/cwms-batch-events"


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
        body = json.loads(msg["Body"])
        message = JobMessage(**body)

        process_job_message(message, session.create_session, job_logger)

        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=msg["ReceiptHandle"],
        )
