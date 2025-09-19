import boto3
import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
WM_EVENT_BUCKET = os.getenv("WM_EVENT_MANAGER_S3_BUCKET")


class S3JobLogger:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

    def get_logs_for_job(self, job_id: str) -> str:
        key = f"logs/{job_id}.log"
        response = self.s3.get_object(Bucket=WM_EVENT_BUCKET, Key=key)
        body: str = response["Body"].read().decode("utf-8")
        return body

    def push_logs_for_job(self, job_id: str, logs: str) -> None:
        key = f"logs/{job_id}.log"
        self.s3.put_object(Bucket=WM_EVENT_BUCKET, Key=key, Body=logs.encode("utf-8"))
