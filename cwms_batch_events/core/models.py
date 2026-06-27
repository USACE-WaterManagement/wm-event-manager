from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel
from uuid import UUID


AWS_BATCH_RESERVED_PREFIX = "AWS_BATCH"


def _reject_aws_batch_reserved_env_names(names: list[str]) -> None:
    reserved_names = [
        name for name in names if name.upper().startswith(AWS_BATCH_RESERVED_PREFIX)
    ]
    if reserved_names:
        raise ValueError(
            "environment variable names cannot start with AWS_BATCH: "
            + ", ".join(reserved_names)
        )


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
    runtime: str = "python"
    resource_profile: str = "small"
    command_args: list[str] = Field(default_factory=list)
    timeout_minutes: int = 30
    schedule_enabled: bool = False
    schedule_type: str = "manual"
    schedule_minute: int | None = None
    schedule_cron: str | None = None
    env_vars: dict[str, str] = Field(default_factory=dict)
    secret_env_names: list[str] = Field(default_factory=list)
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


class ScriptRunRequest(CamelModel):
    script_id: UUID


class ScriptRunOptions(CamelModel):
    office: str
    repo_path: str
    script_slug: str | None
    runtime: str = "python"
    resource_profile: str = "small"
    command_args: list[str] = Field(default_factory=list)
    timeout_minutes: int = 30
    env_vars: dict[str, str] = Field(default_factory=dict)

    @field_validator("env_vars")
    def validate_env_vars(cls, value: dict[str, str]) -> dict[str, str]:
        _reject_aws_batch_reserved_env_names(list(value))
        return value


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


class RuntimeEnvResponse(CamelModel):
    env_vars: dict[str, str]


class ScriptBase(CamelModel):
    name: str
    description: str
    repo_path: str
    execution_type: str
    runtime: str = "python"
    resource_profile: str = "small"
    command_args: list[str] = Field(default_factory=list)
    timeout_minutes: int = 30
    schedule_enabled: bool = False
    schedule_type: str = "manual"
    schedule_minute: int | None = None
    schedule_cron: str | None = None
    env_vars: dict[str, str] = Field(default_factory=dict)
    secret_env_names: list[str] = Field(default_factory=list)
    active: bool = True
    roles: list[str] = Field(default_factory=list)
    job_runners: list[UUID] = Field(default_factory=list)

    @field_validator("env_vars")
    def validate_env_vars(cls, value: dict[str, str]) -> dict[str, str]:
        _reject_aws_batch_reserved_env_names(list(value))
        return value

    @field_validator("secret_env_names")
    def validate_secret_env_names(cls, value: list[str]) -> list[str]:
        _reject_aws_batch_reserved_env_names(value)
        return value

    @field_validator("runtime")
    def validate_runtime(cls, value: str) -> str:
        if value not in {"python", "node", "java", "shell"}:
            raise ValueError("runtime must be one of: python, node, java, shell")
        return value

    @field_validator("resource_profile")
    def validate_resource_profile(cls, value: str) -> str:
        if value not in {"small", "medium", "large"}:
            raise ValueError("resourceProfile must be one of: small, medium, large")
        return value

    @field_validator("timeout_minutes")
    def validate_timeout_minutes(cls, value: int) -> int:
        if not 1 <= value <= 1440:
            raise ValueError("timeoutMinutes must be between 1 and 1440")
        return value

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

        fields = value.strip().split()
        if len(fields) != 5:
            raise ValueError("scheduleCron must be a five-field cron expression")

        return " ".join(fields)

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
    job_runners: list[UUID] = Field(default_factory=list)

    @field_validator("job_runners", mode="before")
    def extract_job_runner_ids(cls, v):
        return [jr.id if hasattr(jr, "id") else jr for jr in v]


class ScriptUpdate(ScriptBase):
    pass
