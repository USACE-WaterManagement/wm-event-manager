from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class ScriptCatalog(BaseModel):
    scripts: list[str]


class ScriptRunRequest(BaseModel):
    office_name: str
    script_name: str

    class Config:
        alias_generator = to_camel
