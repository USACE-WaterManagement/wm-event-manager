from unittest import mock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from cwms_batch_events.core.auth.user.dependencies import get_current_user_keycloak


class Credentials:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_missing_cda_profile_returns_401():
    with (
        mock.patch(
            "cwms_batch_events.core.auth.user.dependencies.verify_jwt",
            return_value={"azp": "cwms"},
        ),
        mock.patch(
            "cwms_batch_events.core.auth.user.dependencies.get_user_profile",
            side_effect=ValueError("No CDA account/profile found for user"),
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            await get_current_user_keycloak(Credentials("token"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token: No CDA account/profile found for user"


@pytest.mark.asyncio
async def test_invalid_cda_profile_payload_returns_401():
    with (
        mock.patch(
            "cwms_batch_events.core.auth.user.dependencies.verify_jwt",
            return_value={"azp": "cwms"},
        ),
        mock.patch(
            "cwms_batch_events.core.auth.user.dependencies.get_user_profile",
            side_effect=ValidationError.from_exception_data(
                "CdaUserProfile",
                [
                    {
                        "type": "missing",
                        "loc": ("user-name",),
                        "input": {},
                        "msg": "Field required",
                    }
                ],
            ),
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            await get_current_user_keycloak(Credentials("token"))

    assert exc.value.status_code == 401
    assert exc.value.detail.startswith("Invalid token:")
