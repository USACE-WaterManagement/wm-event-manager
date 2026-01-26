from datetime import datetime
from typing import Callable
from cwms_batch_events.core.dispatcher import JobDispatcher
from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.job_database.postgres.postgres import PostgresJobDatabase
from cwms_batch_events.core.job_logger.base import JobLogger
from cwms_batch_events.core.models import JobMessage, JobStatus


STATUS_PRIORITY = {
    JobStatus.PENDING: 1,
    JobStatus.RUNNING: 2,
    JobStatus.FAILED: 3,
    JobStatus.COMPLETED: 4,
}


def process_job_message(
    message: JobMessage,
    session_factory: Callable,
    job_logger: JobLogger,
) -> None:
    db_session = session_factory()

    try:
        db = PostgresJobDatabase(db=db_session)
        dispatcher = JobDispatcher(db, job_logger)
        dispatcher.dispatch_job(message)

    finally:
        db_session.close()


def update_batch_job_status(
    batch_job_id: str, status: JobStatus, time_iso: datetime, db: JobDatabase
):
    job = db.get_job_by_external_id(batch_job_id)

    if not job:
        raise ValueError(f"No job found with batch_job_id={batch_job_id}")

    # Idempotency guard
    if STATUS_PRIORITY[status] <= STATUS_PRIORITY[job.job_status]:
        return

    job_id = job.id

    print(f"Updating wm-event job `{job_id}` status to `{status}` at {time_iso}")

    if status == JobStatus.RUNNING:
        time_field = "run_time"
    elif status == JobStatus.COMPLETED or status == JobStatus.FAILED:
        time_field = "end_time"
    else:
        time_field = None

    db.update_job_field(job_id, "job_status", status)
    if time_field:
        db.update_job_field(job_id, time_field, time_iso)
