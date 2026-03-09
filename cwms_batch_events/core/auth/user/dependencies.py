from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError

from cwms_batch_events.core.auth.user.jwt import verify_jwt
from cwms_batch_events.core.auth.user.models import User
from cwms_batch_events.core.auth.user.roles import (
    get_user_allowed_offices,
    get_user_profile,
)
from cwms_batch_events.core.utils import ALL_OFFICES


ALL_OFFICES_LOWER = [office.lower() for office in ALL_OFFICES]

oauth2_scheme = HTTPBearer()


async def get_current_user_keycloak(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
) -> User:
    token = credentials.credentials
    try:
        claims = verify_jwt(token)
        azp = claims.get("azp", "")
        if claims["azp"] != "cwms":
            raise Exception(f"Client '{azp}' is not authorized for this API")

        cda_user = get_user_profile(token)
        allowed_offices = get_user_allowed_offices(cda_user)
    except (ValidationError, ValueError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )

    return User(username=cda_user.user_name, offices=allowed_offices)


async def get_current_user_mock() -> User:
    return User(username="dev-user", offices=ALL_OFFICES_LOWER)
