from pydantic import BaseModel


class User(BaseModel):
    username: str
    offices: list[str]
    admin_offices: list[str]
