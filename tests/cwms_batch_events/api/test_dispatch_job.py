from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

import pytest

from cwms_batch_events.api.dependencies import get_job_database, get_job_logger
from cwms_batch_events.api.main import app
from cwms_batch_events.core.auth.service.dependencies import require_internal_auth
from cwms_batch_events.core.dispatcher import JobDispatcher, MissingJobRunner

client = TestClient(app)

mock_db = MagicMock()
mock_logger = MagicMock()

app.dependency_overrides[get_job_database] = lambda: mock_db
app.dependency_overrides[get_job_logger] = lambda: mock_logger
app.dependency_overrides[require_internal_auth] = lambda: True


def test_dispatcher_fires_local_runner():
    message = MagicMock()
    message.runner_type = "docker-local"

    mock_db = MagicMock()
    mock_logger = MagicMock()

    with patch("cwms_batch_events.core.dispatcher.LocalJobRunner") as MockLocalRunner:
        instance = MockLocalRunner.return_value
        instance.run_job.return_value = None

        dispatcher = JobDispatcher(mock_db, mock_logger)
        dispatcher.dispatch_job(message)

        MockLocalRunner.assert_called_once_with(mock_db, mock_logger)
        instance.run_job.assert_called_once_with(message)


def test_dispatcher_fires_batch_runner():
    message = MagicMock()
    message.runner_type = "batch"

    mock_db = MagicMock()
    mock_logger = MagicMock()

    with patch("cwms_batch_events.core.dispatcher.BatchJobRunner") as MockBatchRunner:
        instance = MockBatchRunner.return_value
        instance.run_job.return_value = None

        dispatcher = JobDispatcher(mock_db, mock_logger)
        dispatcher.dispatch_job(message)

        MockBatchRunner.assert_called_once_with(mock_db)
        instance.run_job.assert_called_once_with(message)


def test_dispatcher_missing_runner():
    message = MagicMock()
    message.runner_type = "unknown"

    dispatcher = JobDispatcher(MagicMock(), MagicMock())

    with pytest.raises(MissingJobRunner):
        dispatcher.dispatch_job(message)
