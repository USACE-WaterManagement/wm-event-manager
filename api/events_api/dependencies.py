from fastapi import Depends

from .auth.user import get_current_user_keycloak, get_current_user_mock
from .job_database.base import JobDatabase
from .job_database.dynamo import DynamoJobDatabase
from .job_logger.base import JobLogger
from .job_logger.s3 import S3JobLogger
from .job_runner.base import JobRunner
from .job_runner.local import LocalJobRunner
from .settings import settings

MOCK_USER = settings.mock_user
if MOCK_USER:
    get_current_user = get_current_user_mock
else:
    get_current_user = get_current_user_keycloak


def get_job_database() -> JobDatabase:
    return DynamoJobDatabase()


def get_job_logger() -> JobLogger:
    return S3JobLogger()


def get_job_runner(
    db: JobDatabase = Depends(get_job_database),
    logger: JobLogger = Depends(get_job_logger),
) -> JobRunner:
    return LocalJobRunner(db=db, logger=logger)
