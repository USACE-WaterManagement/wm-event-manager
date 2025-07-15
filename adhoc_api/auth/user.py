import os
from pydantic import BaseModel


class User(BaseModel):
    username: str
    offices: list[str]


async def get_current_user_aws() -> User:
    return User(username="not-implemented", offices=[])


async def get_current_user_local() -> User:
    return User(username="dev-user", offices=["lrh"])


DEPLOY_MODE = os.getenv("DEPLOY_MODE", "aws")

if DEPLOY_MODE == "local":
    get_current_user = get_current_user_local
else:
    get_current_user = get_current_user_aws
