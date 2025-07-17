from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class CdaUserProfile(BaseModel):
    user_name: str = Field(alias="user-name")
    principal: str
    cac_auth: bool = Field(alias="cac-auth")
    roles: dict[str, list[str]]


class ScriptCatalog(BaseModel):
    scripts: list[str]


class ScriptRunRequest(BaseModel):
    office_name: str
    script_name: str

    class Config:
        alias_generator = to_camel
