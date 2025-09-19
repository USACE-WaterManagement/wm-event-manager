import boto3
import botocore.exceptions
import json
import os

from events_api.schemas import ScriptCatalog

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
WM_EVENT_BUCKET = os.getenv("WM_EVENT_MANAGER_S3_BUCKET")


def get_scripts_catalog(office: str):
    s3 = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    try:
        response = s3.get_object(
            Bucket=WM_EVENT_BUCKET, Key=f"catalogs/{office}/scripts_catalog.json"
        )
        body = response["Body"].read().decode("utf-8")
        json_data = json.loads(body)
        return ScriptCatalog(**json_data)
    except botocore.exceptions.ClientError:
        return None
