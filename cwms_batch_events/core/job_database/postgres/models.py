import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    func,
    Table,
    UUID,
    VARCHAR,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
import uuid

from cwms_batch_events.core.models import JobStatus


class Base(DeclarativeBase):
    type_annotation_map = {datetime.datetime: DateTime(timezone=True), str: VARCHAR}


scripts_job_runners = Table(
    "scripts_job_runners",
    Base.metadata,
    Column("script_id", ForeignKey("scripts.id"), primary_key=True),
    Column("job_runner_id", ForeignKey("job_runners.id"), primary_key=True),
)


class JobModel(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    script_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scripts.id", ondelete="SET NULL"), nullable=True
    )
    script_name: Mapped[str]
    script_slug: Mapped[str | None]
    job_status: Mapped[JobStatus] = mapped_column(VARCHAR)
    username: Mapped[str]
    office: Mapped[str]
    repo_path: Mapped[str]
    execution_type: Mapped[str | None]
    runtime: Mapped[str] = mapped_column(default="python")
    resource_profile: Mapped[str] = mapped_column(default="small")
    command_args: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    timeout_minutes: Mapped[int] = mapped_column(default=30)
    schedule_enabled: Mapped[bool] = mapped_column(default=False)
    schedule_type: Mapped[str] = mapped_column(default="manual")
    schedule_minute: Mapped[int | None]
    schedule_cron: Mapped[str | None]
    schedule_timezone: Mapped[str] = mapped_column(default="UTC")
    env_vars: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict)
    secret_env_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    created_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    run_time: Mapped[Optional[datetime.datetime]]
    end_time: Mapped[Optional[datetime.datetime]]
    job_runner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_runners.id")
    )
    external_job_id: Mapped[Optional[str]]

    script: Mapped["ScriptModel | None"] = relationship("ScriptModel", lazy="selectin")


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

    scripts: Mapped[list["ScriptModel"]] = relationship(
        secondary=scripts_job_runners, back_populates="job_runners"
    )


class ScriptModel(Base):
    __tablename__ = "scripts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    office: Mapped[str]
    name: Mapped[str]
    slug: Mapped[str]
    description: Mapped[str]
    repo_path: Mapped[str]
    execution_type: Mapped[str]
    runtime: Mapped[str] = mapped_column(default="python")
    resource_profile: Mapped[str] = mapped_column(default="small")
    command_args: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    timeout_minutes: Mapped[int] = mapped_column(default=30)
    schedule_enabled: Mapped[bool] = mapped_column(default=False)
    schedule_type: Mapped[str] = mapped_column(default="manual")
    schedule_minute: Mapped[int | None]
    schedule_cron: Mapped[str | None]
    schedule_timezone: Mapped[str] = mapped_column(default="UTC")
    env_vars: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict)
    secret_env_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    active: Mapped[bool]
    roles: Mapped[list[str]] = mapped_column(ARRAY(String))
    created_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    updated_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )

    job_runners: Mapped[list["JobRunnerModel"]] = relationship(
        secondary=scripts_job_runners, lazy="selectin", back_populates="scripts"
    )
