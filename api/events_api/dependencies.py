import os

from .auth.user import get_current_user_keycloak, get_current_user_mock
from .job_database.base import JobDatabase
from .job_database.dynamo_job_database import DynamoJobDatabase

MOCK_USER = os.getenv("MOCK_USER", "false")
if MOCK_USER == "true":
    get_current_user = get_current_user_mock
else:
    get_current_user = get_current_user_keycloak


def get_job_database() -> JobDatabase:
    return DynamoJobDatabase()
