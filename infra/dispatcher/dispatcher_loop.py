import boto3
import json
import logging
from cwms_batch_events.core.dispatcher import JobDispatcher
from cwms_batch_events.core.job_database.postgres import postgres, session
from cwms_batch_events.core.job_logger.s3 import S3JobLogger
from cwms_batch_events.core.models import JobMessage

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
        db_session = session.create_session()

        try:
            db = postgres.PostgresJobDatabase(db=db_session)
            dispatcher = JobDispatcher(db, job_logger)

            body = json.loads(msg["Body"])
            message = JobMessage(**body)

            dispatcher.dispatch_job(message)

            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=msg["ReceiptHandle"],
            )

        finally:
            db_session.close()
