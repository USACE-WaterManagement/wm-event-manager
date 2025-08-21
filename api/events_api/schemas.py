from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel, to_pascal


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


class JobLogs(BaseModel):
    logs: str


class JobRecord(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal, validate_by_name=True, validate_by_alias=True
    )

    job_id: str
    script: str
    user: str
    office: str
    created_time: str
    status: JobStatus


class ScriptCatalog(BaseModel):
    scripts: list[str]


class ScriptRunRequest(BaseModel):
    office_name: str
    script_name: str

    class Config:
        alias_generator = to_camel
