import boto3
import botocore.exceptions
import json

from cwms_batch_events.core.models import OfficeCatalog
from cwms_batch_events.core.settings import settings

S3_ENDPOINT_URL = settings.s3_endpoint_url
S3_BUCKET = settings.s3_bucket


def get_scripts_catalog(office: str):
    s3 = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
    )

    try:
        response = s3.get_object(
            Bucket=S3_BUCKET, Key=f"catalogs/{office}/scripts_catalog.json"
        )
        body = response["Body"].read().decode("utf-8")
        json_data = json.loads(body)
        return OfficeCatalog(**json_data)
    except botocore.exceptions.ClientError:
        return None
