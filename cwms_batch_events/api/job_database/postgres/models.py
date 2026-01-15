import datetime
from sqlalchemy import DateTime, ForeignKey, func, UUID, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional
import uuid

from cwms_batch_events.api.schemas import JobStatus


class Base(DeclarativeBase):
    type_annotation_map = {datetime.datetime: DateTime(timezone=True), str: VARCHAR}


class JobModel(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    script_name: Mapped[str]
    job_status: Mapped[JobStatus] = mapped_column(VARCHAR)
    username: Mapped[str]
    office: Mapped[str]
    created_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    run_time: Mapped[Optional[datetime.datetime]]
    end_time: Mapped[Optional[datetime.datetime]]
    job_runner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_runners.id")
    )
    external_job_id: Mapped[Optional[str]]


class JobRunnerModel(Base):
    __tablename__ = "job_runners"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str]
    label: Mapped[str]
    description: Mapped[str]
    active: Mapped[bool]
    created_time: Mapped[datetime.datetime]
