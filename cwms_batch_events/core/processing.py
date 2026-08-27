from datetime import datetime
from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.models import JobStatus


STATUS_PRIORITY = {
    JobStatus.PENDING: 1,
    JobStatus.RUNNING: 2,
    JobStatus.FAILED: 3,
    JobStatus.COMPLETED: 4,
}


class MissingBatchJobError(Exception):
    pass


def update_batch_job_status(
    batch_job_id: str, status: JobStatus, time_iso: datetime, db: JobDatabase
):
    if status not in STATUS_PRIORITY:
        raise ValueError(f"Unsupported job status: {status}")

    job = db.get_job_by_external_id(batch_job_id)

    if not job:
        raise MissingBatchJobError(f"No job found with batch_job_id={batch_job_id}")

    # Idempotency guard
    if STATUS_PRIORITY[status] <= STATUS_PRIORITY[job.job_status]:
        return

    job_id = job.id

    print(f"Updating job `{job_id}` status to `{status}` at {time_iso}")

    db.update_job_status(job_id, status)
