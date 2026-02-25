from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from cwms_batch_events.core.auth.user.jwt import verify_jwt
from cwms_batch_events.core.auth.user.models import User
from cwms_batch_events.core.auth.user.roles import (
    get_user_admin_offices,
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )

    cda_user = get_user_profile(token)
    allowed_offices = get_user_allowed_offices(cda_user)
    admin_offices = get_user_admin_offices(cda_user)
    return User(
        username=cda_user.user_name,
        offices=allowed_offices,
        admin_offices=admin_offices,
    )


async def get_current_user_mock() -> User:
    return User(
        username="dev-user", offices=ALL_OFFICES_LOWER, admin_offices=ALL_OFFICES_LOWER
    )
