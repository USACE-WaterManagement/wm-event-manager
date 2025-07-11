import boto3
import json
import os

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def get_scripts_catalog(office: str):
    s3 = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    response = s3.get_object(
        Bucket="wm-web-internal-dev", Key=f"{office}/scripts_catalog.json"
    )
    body = response["Body"].read().decode("utf-8")
    json_data = json.loads(body)
    return json_data
