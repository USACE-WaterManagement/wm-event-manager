import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone
import os
import uuid

from .schemas import ScriptRunRequest


dynamodb_endpoint = os.getenv("DYNAMODB_HOST", "http://dynamodb:9010")
table_name = "WM-Event-Manager-Jobs"

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=dynamodb_endpoint,
    region_name="us-west-1",
    aws_access_key_id="eventsadmin",
    aws_secret_access_key="eventsadmin",
)

jobs_table = dynamodb.Table(table_name)


def create_job(payload: ScriptRunRequest, user_id: str):
    job_id = str(uuid.uuid4())
    item = {
        "JobId": job_id,
        "Script": payload.script_name,
        "User": user_id,
        "Office": payload.office_name,
        "CreatedTime": datetime.now(timezone.utc).isoformat(),
        "Status": "Pending",
    }
    jobs_table.put_item(Item=item)
    return job_id


def get_jobs_for_user(user_id: str):
    user_jobs = jobs_table.query(
        IndexName="UserIndex",
        Select="ALL_ATTRIBUTES",
        KeyConditionExpression=Key("User").eq(user_id),
        ScanIndexForward=False,
    )
    return user_jobs["Items"]
