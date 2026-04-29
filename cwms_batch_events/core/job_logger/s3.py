import boto3
from uuid import UUID

from cwms_batch_events.core.settings import settings


class S3JobLogger:
    def __init__(self):
        self.s3_bucket = settings.s3_bucket
        self.s3_endpoint_url = settings.s3_endpoint_url

        if not self.s3_bucket:
            raise ValueError("S3_BUCKET must be configured for S3 logging")

        self.s3 = boto3.client(
            "s3",
            endpoint_url=self.s3_endpoint_url,
        )

    def get_logs_for_job(self, job_id: UUID) -> str:
        key = f"logs/{job_id}.log"
        response = self.s3.get_object(Bucket=self.s3_bucket, Key=key)
        body: str = response["Body"].read().decode("utf-8")
        return body

    def push_logs_for_job(self, job_id: UUID, logs: str) -> None:
        key = f"logs/{job_id}.log"
        self.s3.put_object(Bucket=self.s3_bucket, Key=key, Body=logs.encode("utf-8"))
