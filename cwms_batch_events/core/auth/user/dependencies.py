from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from cwms_batch_events.core.auth.user.jwt import verify_jwt
from cwms_batch_events.core.auth.user.models import User
from cwms_batch_events.core.auth.user.roles import (
    get_user_admin_offices,
    get_user_allowed_offices,
    get_user_profile_apikey,
    get_user_profile_jwt,
)
from cwms_batch_events.core.utils import ALL_OFFICES, ALL_OFFICE_ROLES


async def get_auth_credentials(request: Request) -> HTTPAuthorizationCredentials:
    header = request.headers.get("Authorization")
    if not header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = header.split()
    if len(parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    return HTTPAuthorizationCredentials(scheme=parts[0], credentials=parts[1])


async def get_current_user_cwms(
    credentials: HTTPAuthorizationCredentials = Depends(get_auth_credentials),
) -> User:
    if credentials.scheme.lower() == "bearer":
        token = credentials.credentials
        try:
            claims = verify_jwt(token)
            azp = claims.get("azp", "")
            if claims["azp"] != "cwms":
                raise Exception(f"Client '{azp}' is not authorized for this API")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )
        cda_user = get_user_profile_jwt(token)
    elif credentials.scheme.lower() == "apikey":
        apikey = credentials.credentials
        cda_user = get_user_profile_apikey(apikey)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unsupported auth scheme: {credentials.scheme}",
        )

    allowed_offices = get_user_allowed_offices(cda_user)
    admin_offices = get_user_admin_offices(cda_user)
    return User(
        username=cda_user.user_name,
        offices=allowed_offices,
        admin_offices=admin_offices,
        roles=cda_user.roles,
    )


async def get_current_user_mock() -> User:
    return User(
        username="dev-user",
        offices=ALL_OFFICES,
        admin_offices=ALL_OFFICES,
        roles=ALL_OFFICE_ROLES,
    )
