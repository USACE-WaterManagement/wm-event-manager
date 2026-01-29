from datetime import datetime
from uuid import UUID
import boto3

from cwms_batch_events.core.models import (
    JobMessage,
    JobRequestedBy,
    JobSource,
    ScriptRunRequest,
)
from cwms_batch_events.core.settings import settings

MESSAGE_VERSION = "1.0"


class JobQueue:
    def __init__(self):
        self.sqs = boto3.resource(
            "sqs",
            endpoint_url=settings.sqs_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_default_region,
        )
        self.queue = self.sqs.get_queue_by_name(QueueName="cwms-batch-events")
        self.runner_type = settings.default_job_runner

    def create_job_message(
        self, job_id: UUID, username: str, source: JobSource, payload: ScriptRunRequest
    ):
        requested_by = JobRequestedBy(username=username, source=source)
        return JobMessage(
            version=MESSAGE_VERSION,
            job_id=job_id,
            runner_type=self.runner_type,
            requested_by=requested_by,
            created_at=datetime.now(),
            payload=payload,
        )

    def send_job_message(self, message: JobMessage) -> str:
        response = self.queue.send_message(MessageBody=message.model_dump_json())
        return response["MessageId"]
