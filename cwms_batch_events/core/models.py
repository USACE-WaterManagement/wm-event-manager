from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
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
    principal: str
    cac_auth: bool = Field(alias="cac-auth")
    roles: dict[str, list[str]]


class JobLogs(CamelModel):
    logs: str


class JobRecord(CamelModel):
    id: UUID
    script_name: str
    job_status: JobStatus
    username: str
    office: str
    created_time: datetime
    run_time: datetime | None = None
    end_time: datetime | None = None
    job_runner_id: UUID
    external_job_id: str | None = None


class JobRunner(CamelModel):
    id: UUID
    slug: str
    label: str
    description: str
    active: bool
    created_time: datetime


class OfficeCatalog(CamelModel):
    scripts: list[str]


class OfficeCatalogs(CamelModel):
    catalogs: dict[str, OfficeCatalog]


class ScriptRunRequest(CamelModel):
    office_name: str
    script_name: str


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
    payload: ScriptRunRequest


class BatchJobStatusUpdateRequest(BaseModel):
    status: JobStatus
    event_time: datetime


class BindExternalJobIdRequest(BaseModel):
    external_job_id: str
