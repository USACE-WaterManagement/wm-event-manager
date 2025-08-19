from typing import Protocol

from .dynamo_job_database import DynamoJobDatabase
from ..schemas import JobRecord, JobStatus, ScriptRunRequest


class JobDatabase(Protocol):
    def create_job(self, payload: ScriptRunRequest, user_id: str) -> JobRecord: ...
    def get_job_by_id(self, job_id: str) -> JobRecord | None: ...
    def get_jobs_for_user(self, user_id: str) -> list[JobRecord]: ...
    def update_job_status(self, job_id: str, status: JobStatus) -> None: ...


def get_job_database() -> JobDatabase:
    return DynamoJobDatabase()
