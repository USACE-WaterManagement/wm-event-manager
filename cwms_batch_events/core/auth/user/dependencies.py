from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from cwms_batch_events.core.auth.user.jwt import verify_jwt
from cwms_batch_events.core.auth.user.models import User
from cwms_batch_events.core.auth.user.roles import get_user_allowed_offices
from cwms_batch_events.core.utils import ALL_OFFICES


ALL_OFFICES_LOWER = [office.lower() for office in ALL_OFFICES]

oauth2_scheme = HTTPBearer()


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

    allowed_offices = get_user_allowed_offices(token)
    return User(username="not-implemented", offices=allowed_offices)


async def get_current_user_mock() -> User:
    return User(username="dev-user", offices=ALL_OFFICES_LOWER)
