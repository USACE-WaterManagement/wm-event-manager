from typing import Callable
from cwms_batch_events.core.dispatcher import JobDispatcher
from cwms_batch_events.core.job_database.postgres.postgres import PostgresJobDatabase
from cwms_batch_events.core.job_logger.base import JobLogger
from cwms_batch_events.core.models import JobMessage, JobStatus

BATCH_STATUS_MAP = {
    "PENDING": JobStatus.PENDING,
    "RUNNING": JobStatus.RUNNING,
    "SUCCEEDED": JobStatus.COMPLETED,
    "FAILED": JobStatus.FAILED,
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
    batch_job_id: str,
    status: str,
    time_iso: str,
    session_factory: Callable,
):
    event_status = BATCH_STATUS_MAP.get(status)
    if not event_status:
        raise ValueError(f"Status `{status}` is not handled by this function")

    db_session = session_factory()

    try:
        db = PostgresJobDatabase(db=db_session)
        job = db.get_job_by_external_id(batch_job_id)

        if not job:
            raise ValueError(f"No job found with batch_job_id={batch_job_id}")

        job_id = job.id

        print(
            f"Updating wm-event job `{job_id}` status to `{event_status}` at {time_iso}"
        )

        if event_status == "Running":
            time_field = "run_time"
        elif event_status == "Completed" or event_status == "Failed":
            time_field = "end_time"

        db.update_job_field(job_id, "job_status", event_status)
        db.update_job_field(job_id, time_field, time_iso)

    finally:
        db_session.close()
