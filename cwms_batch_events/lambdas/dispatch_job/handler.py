import json
from cwms_batch_events.core.models import JobMessage
from cwms_batch_events.core.processing import process_job_message
from cwms_batch_events.core.job_database.postgres import session
from cwms_batch_events.core.job_logger.s3 import S3JobLogger

job_logger = S3JobLogger()


def lambda_handler(event, context):
    for record in event["Records"]:
        message = JobMessage(**json.loads(record["body"]))

        process_job_message(
            message,
            session_factory=session.create_session,
            job_logger=job_logger,
        )
