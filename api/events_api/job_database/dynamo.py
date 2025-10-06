import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone
from decimal import Decimal
import os
from typing import Any
import uuid

from ..schemas import JobRecord, JobStatus, ScriptRunRequest


def dynamodb_item_to_python(item: Any) -> Any:
    if isinstance(item, dict):
        return {k: dynamodb_item_to_python(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [dynamodb_item_to_python(i) for i in item]
    elif isinstance(item, Decimal):
        if item % 1 == 0:
            return int(item)
        else:
            return float(item)
    else:
        return item


dynamodb_endpoint = os.getenv("DYNAMODB_HOST", "http://dynamodb:9010")
table_name = "WM-Event-Manager-Jobs"

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=dynamodb_endpoint,
    region_name="us-west-1",
    aws_access_key_id="eventsadmin",
    aws_secret_access_key="eventsadmin",
)

job_table = dynamodb.Table(table_name)


class DynamoJobDatabase:
    def __init__(self):
        self.table = job_table

    def create_job(self, payload: ScriptRunRequest, user_id: str):
        job_id = str(uuid.uuid4())
        job = JobRecord(
            job_id=job_id,
            script=payload.script_name,
            user=user_id,
            office=payload.office_name,
            created_time=datetime.now(timezone.utc).isoformat(),
            status=JobStatus.PENDING,
        )
        self.table.put_item(Item=job.model_dump(by_alias=False))
        return job

    def get_job_by_id(self, job_id: str) -> JobRecord | None:
        response = self.table.get_item(
            Key={"job_id": job_id},
        )
        job = response.get("Item")
        if not job:
            return None
        return JobRecord(**dynamodb_item_to_python(job))

    def get_jobs_for_user(self, user_id: str):
        user_jobs = self.table.query(
            IndexName="user_index",
            Select="ALL_ATTRIBUTES",
            KeyConditionExpression=Key("user").eq(user_id),
            ScanIndexForward=False,
        )
        job_items = user_jobs.get("Items")
        return [JobRecord(**dynamodb_item_to_python(item)) for item in job_items]

    def update_job_field(self, job_id: str, key: str, value: Any):
        self.table.update_item(
            Key={"job_id": job_id},
            UpdateExpression="set #S=:V",
            ExpressionAttributeNames={"#S": key},
            ExpressionAttributeValues={":V": value},
        )

    def update_job_status(self, job_id: str, status: JobStatus):
        now = datetime.now(timezone.utc).isoformat()

        self.table.update_item(
            Key={"job_id": job_id},
            UpdateExpression="set #S=:V",
            ExpressionAttributeNames={"#S": "status"},
            ExpressionAttributeValues={":V": status},
        )

        if status == JobStatus.RUNNING:
            self.update_job_field(job_id, "run_time", now)
        elif status == JobStatus.COMPLETED or status == JobStatus.FAILED:
            self.update_job_field(job_id, "end_time", now)
