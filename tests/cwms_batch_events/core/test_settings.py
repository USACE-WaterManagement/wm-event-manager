import pytest
from pydantic import ValidationError

from cwms_batch_events.core.settings import Settings


def test_fastapi_root_path_defaults_to_empty_string():
    settings = Settings(root_path=None, app_key="x", auth_environment="TEST")

    assert settings.fastapi_root_path == ""


def test_settings_rejects_blank_strings_as_missing(monkeypatch):
    monkeypatch.delenv("APP_KEY", raising=False)
    monkeypatch.delenv("AUTH_ENVIRONMENT", raising=False)

    with pytest.raises(ValidationError, match="app_key"):
        Settings(app_key="", auth_environment="TEST")


def test_settings_require_auth_environment_when_mock_user_false(monkeypatch):
    monkeypatch.delenv("AUTH_ENVIRONMENT", raising=False)

    with pytest.raises(ValueError, match="AUTH_ENVIRONMENT must be configured"):
        Settings(app_key="secret", mock_user=False)


def test_settings_require_s3_bucket_for_docker_local_runner():
    with pytest.raises(ValueError, match="S3_BUCKET must be configured"):
        Settings(app_key="secret", auth_environment="TEST", default_job_runner="docker-local")


def test_settings_require_docker_local_endpoints():
    with pytest.raises(ValueError, match="S3_ENDPOINT_URL must be configured"):
        Settings(
            app_key="secret",
            auth_environment="TEST",
            default_job_runner="docker-local",
            s3_bucket="bucket",
        )

    with pytest.raises(ValueError, match="SQS_ENDPOINT_URL must be configured"):
        Settings(
            app_key="secret",
            auth_environment="TEST",
            default_job_runner="docker-local",
            s3_bucket="bucket",
            s3_endpoint_url="http://s3",
        )
