from typing import Callable
from cwms_batch_events.core.dispatcher import JobDispatcher
from cwms_batch_events.core.job_database.postgres.postgres import PostgresJobDatabase
from cwms_batch_events.core.job_logger.base import JobLogger
from cwms_batch_events.core.models import JobMessage


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
