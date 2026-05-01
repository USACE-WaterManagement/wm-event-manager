import boto3

from cwms_batch_events.core.models import NotificationMessage
from cwms_batch_events.core.settings import settings

MESSAGE_VERSION = "1.0"
JOB_FAILURE_TEMPLATE = "job_failure_v1"


class NotificationQueue:
    def __init__(self):
        self.sqs = boto3.resource(
            "sqs",
            endpoint_url=settings.sqs_endpoint_url,
            region_name=settings.aws_default_region,
        )
        self.queue = self.sqs.get_queue_by_name(
            QueueName=settings.notification_queue_name
        )

    def send_notification(self, message: NotificationMessage) -> str:
        response = self.queue.send_message(MessageBody=message.model_dump_json())
        return response["MessageId"]
