import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone
import os
import uuid

from .schemas import JobRecord, JobStatus, ScriptRunRequest


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
    job = JobRecord(
        job_id=job_id,
        script=payload.script_name,
        user=user_id,
        office=payload.office_name,
        created_time=datetime.now(timezone.utc).isoformat(),
        status=JobStatus.PENDING,
    )
    jobs_table.put_item(Item=job.model_dump(by_alias=True))
    return job


def get_jobs_for_user(user_id: str):
    user_jobs = jobs_table.query(
        IndexName="UserIndex",
        Select="ALL_ATTRIBUTES",
        KeyConditionExpression=Key("User").eq(user_id),
        ScanIndexForward=False,
    )
    return user_jobs["Items"]


def update_job_status(job_id: str, status: JobStatus):
    jobs_table.update_item(
        Key={"JobId": job_id},
        UpdateExpression="set #S=:V",
        ExpressionAttributeNames={"#S": "Status"},
        ExpressionAttributeValues={":V": status},
    )
