from uuid import uuid4
from unittest import mock
import pytest


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
