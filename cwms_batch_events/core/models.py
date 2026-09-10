from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel
from uuid import UUID
from cwms_batch_events.core.schedules import validate_cron


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, validate_by_name=True, validate_by_alias=True
    )

    def model_dump(self, **kwargs):
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)


class JobStatus(str, Enum):
    FAILED = "Failed"
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"


class CdaUserProfile(BaseModel):
    user_name: str = Field(alias="user-name")
    principal: str | None = None
    cac_auth: bool = Field(alias="cac-auth")
    roles: dict[str, list[str]]


class JobLogs(CamelModel):
    logs: str


class JobRecord(CamelModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    script_id: UUID | None
    script_name: str
    script_slug: str | None
    job_status: JobStatus
    username: str
    office: str
    repo_path: str
    execution_type: str | None
    created_time: datetime
    run_time: datetime | None = None
    end_time: datetime | None = None
    job_runner_id: UUID
    external_job_id: str | None = None


class JobRunner(CamelModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    label: str
    description: str
    active: bool
    created_time: datetime


class DefaultJobRunner(CamelModel):
    id: UUID
    slug: str


class OfficeCatalog(CamelModel):
    scripts: list[str]


class OfficeCatalogs(CamelModel):
    catalogs: dict[str, OfficeCatalog]


class ScriptRunRequest(CamelModel):
    script_id: UUID


class ScriptRunOptions(CamelModel):
    office: str
    repo_path: str
    script_slug: str | None


class JobSource(str, Enum):
    API = "api"


class JobRequestedBy(BaseModel):
    username: str
    source: JobSource


class JobMessage(BaseModel):
    version: str
    job_id: UUID
    runner_type: str
    requested_by: JobRequestedBy
    created_at: datetime
    payload: ScriptRunOptions


class BatchJobStatusUpdateRequest(BaseModel):
    status: JobStatus
    event_time: datetime


class BindExternalJobIdRequest(BaseModel):
    external_job_id: str


def _validate_schedule_timezone(value: str | None) -> str:
    timezone_name = (value or "UTC").strip()
    if not timezone_name:
        raise ValueError("scheduleTimezone is required")
    try:
        ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f"scheduleTimezone is not a valid timezone: {timezone_name}"
        ) from exc
    return timezone_name


class ScriptBase(CamelModel):
    name: str
    description: str
    repo_path: str
    execution_type: str
    active: bool = True
    roles: list[str] = []
    job_runners: list[UUID] = []
    schedule_enabled: bool = False
    schedule_type: str = "manual"
    schedule_minute: int | None = None
    schedule_cron: str | None = None
    schedule_timezone: str = "UTC"

    @field_validator("schedule_type")
    def validate_schedule_type(cls, value: str) -> str:
        if value not in {"manual", "hourly", "cron"}:
            raise ValueError("scheduleType must be one of: manual, hourly, cron")
        return value

    @field_validator("schedule_minute")
    def validate_schedule_minute(cls, value: int | None) -> int | None:
        if value is not None and not 0 <= value <= 59:
            raise ValueError("scheduleMinute must be between 0 and 59")
        return value

    @field_validator("schedule_cron")
    def validate_schedule_cron(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None

        return validate_cron(value)

    @field_validator("schedule_timezone")
    def validate_schedule_timezone(cls, value: str | None) -> str:
        return _validate_schedule_timezone(value)

    @model_validator(mode="after")
    def validate_enabled_schedule(self):
        if not self.schedule_enabled:
            return self

        if self.schedule_type == "manual":
            raise ValueError(
                "scheduleType must be hourly or cron when scheduleEnabled is true"
            )

        if self.schedule_type == "hourly" and self.schedule_minute is None:
            raise ValueError(
                "scheduleMinute is required when scheduleEnabled is true and scheduleType is hourly"
            )

        if self.schedule_type == "cron" and not self.schedule_cron:
            raise ValueError(
                "scheduleCron is required when scheduleEnabled is true and scheduleType is cron"
            )

        return self


class ScriptCreate(ScriptBase):
    office: str


class ScriptRead(ScriptBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    office: str
    created_time: datetime
    updated_time: datetime
    job_runners: list[UUID] = []

    @field_validator("job_runners", mode="before")
    def extract_job_runner_ids(cls, v):
        return [jr.id if hasattr(jr, "id") else jr for jr in v]


class ScriptUpdate(ScriptBase):
    pass
