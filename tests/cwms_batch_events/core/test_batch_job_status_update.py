from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from cwms_batch_events.core.models import JobStatus
from cwms_batch_events.core.processing import update_batch_job_status


def test_update_running_status():
    mock_db = MagicMock()
    job = MagicMock()
    job.id = 123
    job.job_status = JobStatus.PENDING
    mock_db.get_job_by_external_id.return_value = job

    update_batch_job_status(
        batch_job_id="abc",
        status=JobStatus.RUNNING,
        time_iso=datetime.now(timezone.utc),
        db=mock_db,
    )

    mock_db.update_job_status.assert_any_call(123, JobStatus.RUNNING)


def test_update_completed_status():
    mock_db = MagicMock()
    job = MagicMock()
    job.id = 123
    job.job_status = JobStatus.RUNNING
    mock_db.get_job_by_external_id.return_value = job

    update_batch_job_status(
        batch_job_id="abc",
        status=JobStatus.COMPLETED,
        time_iso=datetime.now(timezone.utc),
        db=mock_db,
    )

    mock_db.update_job_status.assert_any_call(123, JobStatus.COMPLETED)


def test_update_failed_status():
    mock_db = MagicMock()
    job = MagicMock()
    job.id = 123
    job.job_status = JobStatus.RUNNING
    mock_db.get_job_by_external_id.return_value = job

    update_batch_job_status(
        batch_job_id="abc",
        status=JobStatus.FAILED,
        time_iso=datetime.now(timezone.utc),
        db=mock_db,
    )

    mock_db.update_job_status.assert_any_call(123, JobStatus.FAILED)


def test_update_duplicate_status():
    mock_db = MagicMock()
    job = MagicMock()
    job.id = 123
    job.job_status = JobStatus.RUNNING
    mock_db.get_job_by_external_id.return_value = job

    update_batch_job_status(
        batch_job_id="abc",
        status=JobStatus.RUNNING,
        time_iso=datetime.now(timezone.utc),
        db=mock_db,
    )

    mock_db.update_job_status.assert_not_called()


def test_update_lower_priority_status():
    mock_db = MagicMock()
    job = MagicMock()
    job.id = 123
    job.job_status = JobStatus.COMPLETED
    mock_db.get_job_by_external_id.return_value = job

    update_batch_job_status(
        batch_job_id="abc",
        status=JobStatus.RUNNING,
        time_iso=datetime.now(timezone.utc),
        db=mock_db,
    )

    mock_db.update_job_status.assert_not_called()


def test_update_status_missing_batch_job():
    mock_db = MagicMock()
    job = MagicMock()
    job.id = 123
    job.job_status = JobStatus.COMPLETED
    mock_db.get_job_by_external_id.return_value = None

    with pytest.raises(ValueError):
        update_batch_job_status(
            batch_job_id="abc",
            status=JobStatus.RUNNING,
            time_iso=datetime.now(timezone.utc),
            db=mock_db,
        )


def test_update_invalid_status():
    mock_db = MagicMock()
    job = MagicMock()
    job.id = 123
    job.job_status = JobStatus.PENDING
    mock_db.get_job_by_external_id.return_value = None

    with pytest.raises(ValueError):
        update_batch_job_status(
            batch_job_id="abc",
            status="bad_status",  # pyright: ignore[reportArgumentType]
            time_iso=datetime.now(timezone.utc),
            db=mock_db,
        )
