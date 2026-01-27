import os
import boto3
import json
import logging
import requests

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

API_URL = os.environ.get("API_URL", "")
INTERNAL_TOKEN = os.environ.get("APP_KEY", "")
QUEUE_URL = os.environ.get("QUEUE_URL", "")

headers = {
    "Content-Type": "application/json",
    "X-Internal-Token": INTERNAL_TOKEN,
}

while True:
    logger.info("Waiting for messages...")
    resp = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20,
    )

    for msg in resp.get("Messages", []):
        try:
            logger.info(f"Handling message: {msg}")
            body = json.loads(msg["Body"])

            r = requests.post(
                f"{API_URL}/internal/jobs/dispatch",
                headers=headers,
                json=body,
                timeout=10,
            )

            if 200 <= r.status_code < 300:
                logger.info("Message accepted by API, deleting from SQS")
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=msg["ReceiptHandle"],
                )
            else:
                logger.error(
                    "Jobs API rejected message: %s %s",
                    r.status_code,
                    r.text,
                )

        except Exception as e:
            logger.exception("Failed to forward message to Jobs API")
            logger.exception(str(e))
