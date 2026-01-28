from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.models import JobMessage, JobStatus
from ..utils import OFFICES

import boto3
from datetime import datetime


class BatchJobRunner:
    def __init__(self, db: JobDatabase):
        self.db = db
        self.batch = boto3.client("batch")

    def run_job(self, message: JobMessage):
        office = message.payload.office_name
        script = message.payload.script_name

        job_name = (
            f"wm-event-{office}-{script}-{datetime.now().strftime('%Y%m%d-%H%M')}"
        )

        try:
            response = self.batch.submit_job(
                jobName=job_name,
                jobQueue=f"wmes-{OFFICES[office]['office-group']}-jq",
                jobDefinition=f"wmes-{office}-jobs-jobdef",
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
            self.db.update_job_field(message.job_id, "external_job_id", batch_job_id)

        except Exception:
            self.db.update_job_status(message.job_id, JobStatus.FAILED)
