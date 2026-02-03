import logging
from cwms_batch_events.core.models import JobMessage
from cwms_batch_events.core.utils import OFFICES

import boto3
from datetime import datetime

logger = logging.getLogger(__name__)


class BatchJobRunner:
    def __init__(self):
        self.batch = boto3.client("batch")

    def run_job(self, message: JobMessage):
        office = message.payload.office_name
        script = message.payload.script_name

        job_name = (
            f"wm-event-{office}-{script}-{datetime.now().strftime('%Y%m%d-%H%M')}"
        )

        response = self.batch.submit_job(
            jobName=job_name,
            jobQueue=f"cwms-{OFFICES[office]['office-group']}-jq",
            jobDefinition=f"cwms-{office}-jobs-jobdef",
            containerOverrides={
                "environment": [
                    {"name": "OFFICE", "value": office},
                ],
                "command": [f"python /jobs/python/{script}"],
            },
            tags={
                "Office": office,
            },
        )

        batch_job_id: str = response["jobId"]

        logger.info(
            "Succesfully submitted %s to Batch with external job id %s",
            job_name,
            batch_job_id,
        )

        return batch_job_id
