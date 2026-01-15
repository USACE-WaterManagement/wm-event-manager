from fastapi import Depends

from cwms_batch_events.api.auth.user import (
    get_current_user_keycloak,
    get_current_user_mock,
)
from cwms_batch_events.api.job_database.base import JobDatabase
from cwms_batch_events.api.job_database.postgres.postgres import PostgresJobDatabase
from cwms_batch_events.api.job_database.postgres.session import get_db_session
from cwms_batch_events.api.job_logger.base import JobLogger
from cwms_batch_events.api.job_logger.s3 import S3JobLogger
from cwms_batch_events.api.job_runner.base import JobRunner
from cwms_batch_events.api.job_runner.local import LocalJobRunner
from cwms_batch_events.api.settings import settings

MOCK_USER = settings.mock_user
if MOCK_USER:
    get_current_user = get_current_user_mock
else:
    get_current_user = get_current_user_keycloak


def get_job_database(db_session=Depends(get_db_session)) -> JobDatabase:
    return PostgresJobDatabase(db=db_session)


def get_job_logger() -> JobLogger:
    return S3JobLogger()


def get_job_runner(
    db: JobDatabase = Depends(get_job_database),
    logger: JobLogger = Depends(get_job_logger),
) -> JobRunner:
    return LocalJobRunner(db=db, logger=logger)
