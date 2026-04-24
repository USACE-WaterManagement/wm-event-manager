from types import SimpleNamespace
from unittest import mock

import pytest

from cwms_batch_events.core.auth.user.roles import (
    get_user_admin_offices,
    get_user_allowed_offices,
    get_user_profile_apikey,
    get_user_profile_jwt,
)


def test_get_user_profile_apikey_calls_cda_with_apikey_header():
    response = mock.Mock()
    response.json.return_value = {
        "user-name": "tester",
        "cac-auth": False,
        "roles": {"SWT": ["CWMS Users"]},
    }

    with mock.patch(
        "cwms_batch_events.core.auth.user.roles.requests.get",
        return_value=response,
    ) as requests_get, mock.patch(
        "cwms_batch_events.core.auth.user.roles.CDA_API_ROOT",
        "http://example/",
    ):
        profile = get_user_profile_apikey("secret")

    assert profile.user_name == "tester"
    requests_get.assert_called_once_with(
        "http://example/user/profile",
        headers={"accept": "application/json", "Authorization": "apikey secret"},
    )


def test_get_user_profile_jwt_calls_cda_with_bearer_header():
    response = mock.Mock()
    response.json.return_value = {
        "user-name": "tester",
        "cac-auth": False,
        "roles": {"SWT": ["CWMS Users"]},
    }

    with mock.patch(
        "cwms_batch_events.core.auth.user.roles.requests.get",
        return_value=response,
    ) as requests_get, mock.patch(
        "cwms_batch_events.core.auth.user.roles.CDA_API_ROOT",
        "http://example/",
    ):
        profile = get_user_profile_jwt("token")

    assert profile.user_name == "tester"
    requests_get.assert_called_once_with(
        "http://example/user/profile",
        headers={"accept": "application/json", "Authorization": "Bearer token"},
    )


def test_get_user_profile_requires_cda_api_root():
    with mock.patch("cwms_batch_events.core.auth.user.roles.CDA_API_ROOT", ""):
        with pytest.raises(ValueError, match="No CDA_API_ROOT"):
            get_user_profile_apikey("secret")


def test_get_user_profile_jwt_requires_cda_api_root():
    with mock.patch("cwms_batch_events.core.auth.user.roles.CDA_API_ROOT", ""):
        with pytest.raises(ValueError, match="No CDA_API_ROOT"):
            get_user_profile_jwt("token")


def test_get_user_allowed_offices_filters_to_cwms_users():
    cda_user = SimpleNamespace(
        roles={
            "SWT": ["CWMS Users", "Viewer Users"],
            "LRH": ["Viewer Users"],
            "MVK": ["CWMS Users"],
        }
    )

    assert get_user_allowed_offices(cda_user) == ["SWT", "MVK"]


def test_get_user_admin_offices_filters_to_admin_roles():
    cda_user = SimpleNamespace(
        roles={
            "SWT": ["Data Exchange Mgr"],
            "LRH": ["Viewer Users"],
            "MVK": ["Data Acquisition Mgr", "CWMS Users"],
        }
    )

    assert get_user_admin_offices(cda_user) == ["SWT", "MVK"]
