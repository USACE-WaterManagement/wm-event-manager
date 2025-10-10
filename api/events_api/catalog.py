import boto3
import botocore.exceptions
import json

from events_api.schemas import OfficeCatalog
from .settings import settings

AWS_ACCESS_KEY_ID = settings.aws_access_key_id
AWS_SECRET_ACCESS_KEY = settings.aws_secret_access_key
S3_ENDPOINT_URL = settings.s3_endpoint_url
WM_EVENT_BUCKET = settings.wm_event_manager_s3_bucket


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
        return OfficeCatalog(**json_data)
    except botocore.exceptions.ClientError:
        return None
