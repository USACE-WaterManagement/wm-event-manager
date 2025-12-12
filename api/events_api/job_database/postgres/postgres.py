from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Any
import uuid

from .converters import to_job_record
from .models import JobModel
from ...schemas import JobRecord, JobStatus, ScriptRunRequest
from ...utils import get_runner_id


class PostgresJobDatabase:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, payload: ScriptRunRequest, user_id: str) -> JobRecord:
        job_id = uuid.uuid4()

        job = JobModel()
        job.id = job_id
        job.script_name = payload.script_name
        job.job_status = JobStatus.PENDING
        job.username = user_id
        job.office = payload.office_name
        job.job_runner_id = get_runner_id()

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return to_job_record(job)

    def get_job_by_id(self, job_id: str) -> JobRecord | None:
        job_model = self.db.get(JobModel, job_id)
        if job_model is None:
            return None
        return to_job_record(job_model)

    def get_jobs_for_user(self, user_id: str) -> list[JobRecord]:
        job_models = self.db.scalars(
            select(JobModel).where(JobModel.username == user_id)
        ).all()
        return [to_job_record(model) for model in job_models]

    def update_job_field(self, job_id: str, key: str, value: Any) -> None:
        job = self.db.get(JobModel, job_id)

        if not job:
            raise ValueError(f"Job {job_id} does not exist")

        if key not in JobModel.__mapper__.columns:
            raise ValueError(f"{key} is not a valid Job column")

        setattr(job, key, value)
        self.db.commit()

    def update_job_status(self, job_id: str, status: JobStatus) -> None:
        job = self.db.get(JobModel, job_id)

        if not job:
            raise ValueError(f"Job {job_id} does not exist")

        now = datetime.now(timezone.utc)
        job.job_status = status
        self.db.commit()

        if status == JobStatus.RUNNING:
            self.update_job_field(job_id, "run_time", now)
        elif status == JobStatus.COMPLETED or status == JobStatus.FAILED:
            self.update_job_field(job_id, "end_time", now)
