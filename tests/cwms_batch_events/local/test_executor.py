from unittest import mock

import pytest

from cwms_batch_events.core.models import (
    JobStatus,
)
from cwms_batch_events.core.runtime_auth import validate_runtime_token
from cwms_batch_events.core.settings import settings
from cwms_batch_events.local.executor import LocalExecutor
from tests.factories import make_job_message


@pytest.fixture(autouse=True)
def reset_runtime_settings(monkeypatch):
    monkeypatch.setattr(settings, "app_key", "")
    monkeypatch.setattr(settings, "batch_events_api_root", "")
    monkeypatch.setattr(settings, "batch_events_internal_token", "")


def test_local_executor_marks_completed_job_and_persists_logs():
    db = mock.Mock()
    logger = mock.Mock()
    message = make_job_message(runner_type="docker-local")
    container = mock.Mock()
    container.wait.return_value = {"StatusCode": 0}
    container.logs.return_value = b"hello"
    client = mock.Mock()
    client.containers.run.return_value = container

    with mock.patch("docker.client.from_env", return_value=client):
        executor = LocalExecutor(db, logger)
        executor.run_job(message)

    assert db.update_job_status.call_args_list[0].args[1] == JobStatus.RUNNING
    assert db.update_job_status.call_args_list[-1].args[1] == JobStatus.COMPLETED
    logger.push_logs_for_job.assert_called_once_with(message.job_id, "hello")
    container.remove.assert_called_once_with()


def test_local_executor_marks_failed_job_on_nonzero_status():
    db = mock.Mock()
    logger = mock.Mock()
    message = make_job_message(runner_type="docker-local")
    container = mock.Mock()
    container.wait.return_value = {"StatusCode": 1}
    container.logs.return_value = b"hello"
    client = mock.Mock()
    client.containers.run.return_value = container

    with mock.patch("docker.client.from_env", return_value=client):
        executor = LocalExecutor(db, logger)
        executor.run_job(message)

    assert db.update_job_status.call_args_list[-1].args[1] == JobStatus.FAILED


@pytest.mark.parametrize(
    ("runtime", "repo_path", "expected_command"),
    [
        ("python", "python/run.py", ["python", "/jobs/python/run.py"]),
        ("node", "node/run.js", ["node", "/jobs/node/run.js"]),
        ("java", "java/Run.java", ["java", "/jobs/java/Run.java"]),
        ("shell", "bin/hourly.sh", ["bash", "/jobs/bin/hourly.sh"]),
    ],
)
def test_local_executor_uses_shared_runner_runtime_commands(
    runtime,
    repo_path,
    expected_command,
):
    db = mock.Mock()
    logger = mock.Mock()
    message = make_job_message(
        runner_type="docker-local",
        payload=make_job_message().payload.model_copy(
            update={"runtime": runtime, "repo_path": repo_path}
        ),
    )
    container = mock.Mock()
    container.wait.return_value = {"StatusCode": 0}
    container.logs.return_value = b"hello"
    client = mock.Mock()
    client.containers.run.return_value = container

    with mock.patch("docker.client.from_env", return_value=client):
        executor = LocalExecutor(db, logger)
        executor.run_job(message)

    assert client.containers.run.call_args.kwargs["command"] == expected_command


def test_local_executor_passes_runtime_broker_token_when_configured(monkeypatch):
    db = mock.Mock()
    logger = mock.Mock()
    message = make_job_message(runner_type="docker-local")
    container = mock.Mock()
    container.wait.return_value = {"StatusCode": 0}
    container.logs.return_value = b"hello"
    client = mock.Mock()
    client.containers.run.return_value = container
    monkeypatch.setattr(settings, "app_key", "runtime-secret")
    monkeypatch.setattr(settings, "batch_events_api_root", "http://api:8000")

    with mock.patch("docker.client.from_env", return_value=client):
        executor = LocalExecutor(db, logger)
        executor.run_job(message)

    environment = client.containers.run.call_args.kwargs["environment"]
    token_entry = next(
        item for item in environment if item.startswith("BATCH_EVENTS_RUNTIME_TOKEN=")
    )
    token = token_entry.split("=", 1)[1]

    assert "BATCH_EVENTS_API_ROOT=http://api:8000" in environment
    assert validate_runtime_token(token, message.job_id) == (True, None)


def test_local_executor_marks_failed_and_reraises_on_exception():
    db = mock.Mock()
    logger = mock.Mock()
    message = make_job_message(runner_type="docker-local")
    client = mock.Mock()
    client.containers.run.side_effect = RuntimeError("boom")

    with mock.patch("docker.client.from_env", return_value=client):
        executor = LocalExecutor(db, logger)
        with pytest.raises(RuntimeError, match="boom"):
            executor.run_job(message)

    assert db.update_job_status.call_args_list[-1].args[1] == JobStatus.FAILED
