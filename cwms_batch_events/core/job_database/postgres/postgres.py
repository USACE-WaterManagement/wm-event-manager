from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
import uuid

from cwms_batch_events.core.job_database.postgres.converters import to_job_record
from cwms_batch_events.core.job_database.postgres.models import JobModel
from cwms_batch_events.core.models import JobRecord, JobStatus, ScriptRunRequest
from cwms_batch_events.core.utils import get_runner_id


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

    def get_job_by_id(self, job_id: uuid.UUID) -> JobRecord | None:
        job_model = self.db.get(JobModel, job_id)
        if job_model is None:
            return None
        return to_job_record(job_model)

    def get_job_by_external_id(self, ext_job_id: str) -> JobRecord | None:
        job_model = self.db.scalars(
            select(JobModel).where(JobModel.external_job_id == ext_job_id)
        ).one_or_none()
        if job_model is None:
            return None
        return to_job_record(job_model)

    def get_jobs_for_user(self, user_id: str) -> list[JobRecord]:
        job_models = self.db.scalars(
            select(JobModel).where(JobModel.username == user_id)
        ).all()
        return [to_job_record(model) for model in job_models]

    def update_job_status(self, job_id: uuid.UUID, status: JobStatus) -> None:
        job = (
            self.db.query(JobModel)
            .filter(JobModel.id == job_id)
            .with_for_update()
            .one_or_none()
        )

        if not job:
            raise ValueError(f"Job {job_id} does not exist")

        now = datetime.now(timezone.utc)

        job.job_status = status
        if status == JobStatus.RUNNING:
            job.run_time = now
        elif status in (JobStatus.COMPLETED, JobStatus.FAILED):
            job.end_time = now
        self.db.commit()
