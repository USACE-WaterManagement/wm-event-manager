from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from pydantic import BaseModel

from .jwt import verify_jwt


oauth2_scheme = HTTPBearer()


class User(BaseModel):
    username: str
    offices: list[str]


async def get_current_user_keycloak(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
) -> User:
    token = credentials.credentials
    try:
        verify_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )

    return User(username="not-implemented", offices=["lrh"])


async def get_current_user_mock() -> User:
    return User(username="dev-user", offices=["lrh", "lrl"])


MOCK_USER = os.getenv("MOCK_USER", "false")

if MOCK_USER == "true":
    get_current_user = get_current_user_mock
else:
    get_current_user = get_current_user_keycloak
