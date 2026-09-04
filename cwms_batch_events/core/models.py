from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
from uuid import UUID


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


class ScriptBase(CamelModel):
    name: str
    description: str
    repo_path: str
    execution_type: str
    active: bool = True
    roles: list[str] = []
    job_runners: list[UUID] = []


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
