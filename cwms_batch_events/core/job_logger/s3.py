import boto3
from uuid import UUID

from cwms_batch_events.core.settings import settings

S3_ENDPOINT_URL = settings.s3_endpoint_url
S3_BUCKET = settings.s3_bucket


class S3JobLogger:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
        )

    def get_logs_for_job(self, job_id: UUID) -> str:
        key = f"logs/{job_id}.log"
        response = self.s3.get_object(Bucket=S3_BUCKET, Key=key)
        body: str = response["Body"].read().decode("utf-8")
        return body

    def push_logs_for_job(self, job_id: UUID, logs: str) -> None:
        key = f"logs/{job_id}.log"
        self.s3.put_object(Bucket=S3_BUCKET, Key=key, Body=logs.encode("utf-8"))
