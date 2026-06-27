from uuid import uuid4
from unittest import mock
import pytest

from cwms_batch_events.core.models import RuntimeEnvResponse
from cwms_batch_events.core.processing import MissingBatchJobError
from cwms_batch_events.core.runtime_auth import create_runtime_token
from cwms_batch_events.core.settings import settings
from cwms_batch_events.core.secret_broker import (
    InvalidRuntimeEnvError,
    MissingJobError,
    MissingSecretError,
)


def test_update_batch_job_status_returns_no_content(client, job_db):
    with mock.patch("cwms_batch_events.api.routers.internal.update_batch_job_status"):
        response = client.post(
            "/internal/batch-jobs/batch-123/status",
            json={"status": "Running", "event_time": "2026-04-16T12:00:00Z"},
        )

    assert response.status_code == 204
    job_db.update_job_status.assert_not_called()


@pytest.mark.parametrize(
    ("side_effect", "expected_status", "expected_detail"),
    [
        (MissingBatchJobError("missing job"), 404, "missing job"),
        (ValueError("bad status"), 400, "bad status"),
        (RuntimeError("boom"), 500, "boom"),
    ],
)
def test_update_batch_job_status_maps_errors(client, side_effect, expected_status, expected_detail):
    with mock.patch(
        "cwms_batch_events.api.routers.internal.update_batch_job_status",
        side_effect=side_effect,
    ):
        response = client.post(
            "/internal/batch-jobs/batch-123/status",
            json={"status": "Running", "event_time": "2026-04-16T12:00:00Z"},
        )

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}


def test_bind_external_job_id_returns_no_content(client, job_db):
    job_id = str(uuid4())

    response = client.post(
        f"/internal/jobs/{job_id}/external-job-id",
        json={"external_job_id": "batch-123"},
    )

    assert response.status_code == 204
    job_db.bind_external_job_id.assert_called_once()


def test_bind_external_job_id_maps_value_error_to_400(client, job_db):
    job_db.bind_external_job_id.side_effect = ValueError("already bound")
    job_id = str(uuid4())

    response = client.post(
        f"/internal/jobs/{job_id}/external-job-id",
        json={"external_job_id": "batch-123"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "already bound"}


def test_bind_external_job_id_maps_generic_error_to_500(client, job_db):
    job_db.bind_external_job_id.side_effect = RuntimeError("boom")
    job_id = str(uuid4())

    response = client.post(
        f"/internal/jobs/{job_id}/external-job-id",
        json={"external_job_id": "batch-123"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "boom"}


def test_get_runtime_env_returns_brokered_env(client, job_db, monkeypatch):
    job_id = uuid4()

    monkeypatch.setattr(settings, "app_key", "test-runtime-token-secret-with-32-chars")
    with mock.patch(
        "cwms_batch_events.api.routers.internal.resolve_runtime_env",
        return_value=RuntimeEnvResponse(env_vars={"CDA_API_ROOT": "https://cda", "API_KEY": "secret"}),
    ) as resolve_runtime_env:
        response = client.get(
            f"/internal/jobs/{job_id}/runtime-env",
            headers={"X-Runtime-Token": create_runtime_token(job_id)},
        )

    assert response.status_code == 200
    assert response.json() == {
        "envVars": {"CDA_API_ROOT": "https://cda", "API_KEY": "secret"}
    }
    resolve_runtime_env.assert_called_once_with(job_id, job_db)


@pytest.mark.parametrize(
    ("side_effect", "expected_status"),
    [
        (MissingJobError("missing"), 404),
        (MissingSecretError("missing secret"), 422),
        (InvalidRuntimeEnvError("reserved"), 422),
        (RuntimeError("boom"), 500),
    ],
)
def test_get_runtime_env_maps_errors(client, side_effect, expected_status, monkeypatch):
    job_id = uuid4()
    monkeypatch.setattr(settings, "app_key", "test-runtime-token-secret-with-32-chars")
    with mock.patch(
        "cwms_batch_events.api.routers.internal.resolve_runtime_env",
        side_effect=side_effect,
    ):
        response = client.get(
            f"/internal/jobs/{job_id}/runtime-env",
            headers={"X-Runtime-Token": create_runtime_token(job_id)},
        )

    assert response.status_code == expected_status
    assert response.json() == {"detail": str(side_effect)}


def test_get_runtime_env_rejects_missing_runtime_token(client, monkeypatch):
    monkeypatch.setattr(settings, "app_key", "test-runtime-token-secret-with-32-chars")
    response = client.get(f"/internal/jobs/{uuid4()}/runtime-env")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid runtime broker token provided"}


def test_get_runtime_env_rejects_runtime_token_for_other_job(client, monkeypatch):
    monkeypatch.setattr(settings, "app_key", "test-runtime-token-secret-with-32-chars")
    response = client.get(
        f"/internal/jobs/{uuid4()}/runtime-env",
        headers={"X-Runtime-Token": create_runtime_token(uuid4())},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid runtime broker token provided"}


def test_get_runtime_env_rejects_expired_runtime_token(client, monkeypatch):
    job_id = uuid4()
    monkeypatch.setattr(settings, "app_key", "test-runtime-token-secret-with-32-chars")
    monkeypatch.setattr(settings, "batch_runtime_token_ttl_seconds", -1)

    response = client.get(
        f"/internal/jobs/{job_id}/runtime-env",
        headers={"X-Runtime-Token": create_runtime_token(job_id)},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Runtime broker token expired"}
