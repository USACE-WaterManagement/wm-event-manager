import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    CheckConstraint,
    UniqueConstraint,
    func,
    Table,
    UUID,
    VARCHAR,
)
from sqlalchemy.dialects.postgresql import ARRAY
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


class NotificationTemplateModel(Base):
    __tablename__ = "notification_templates"
    __table_args__ = (
        UniqueConstraint("office", "slug", name="notification_templates_office_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    office: Mapped[str]
    slug: Mapped[str]
    subject_template: Mapped[str]
    body_template: Mapped[str]
    active: Mapped[bool]
    created_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    updated_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )


class NotificationGroupModel(Base):
    __tablename__ = "notification_groups"
    __table_args__ = (
        UniqueConstraint("office", "slug", name="notification_groups_office_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    office: Mapped[str]
    slug: Mapped[str]
    name: Mapped[str]
    active: Mapped[bool]
    created_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    updated_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )

    members: Mapped[list["NotificationGroupMemberModel"]] = relationship(
        back_populates="group", cascade="all, delete-orphan", lazy="selectin"
    )


class NotificationGroupMemberModel(Base):
    __tablename__ = "notification_group_members"
    __table_args__ = (
        UniqueConstraint(
            "group_id", "email", name="notification_group_members_group_email"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notification_groups.id", ondelete="CASCADE")
    )
    email: Mapped[str]
    active: Mapped[bool]
    created_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    updated_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )

    group: Mapped["NotificationGroupModel"] = relationship(back_populates="members")


class ScriptNotificationRuleModel(Base):
    __tablename__ = "script_notification_rules"
    __table_args__ = (
        CheckConstraint("event_type = 'job_failed'", name="script_notification_rules_event_type"),
        UniqueConstraint(
            "script_id",
            "event_type",
            "template_id",
            "group_id",
            name="script_notification_rules_unique_rule",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    script_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scripts.id", ondelete="CASCADE")
    )
    event_type: Mapped[str]
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notification_templates.id", ondelete="CASCADE")
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notification_groups.id", ondelete="CASCADE")
    )
    active: Mapped[bool]
    created_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    updated_time: Mapped[datetime.datetime] = mapped_column(
        server_default=func.current_timestamp()
    )

    script: Mapped["ScriptModel"] = relationship(lazy="selectin")
    template: Mapped["NotificationTemplateModel"] = relationship(lazy="selectin")
    group: Mapped["NotificationGroupModel"] = relationship(lazy="selectin")
