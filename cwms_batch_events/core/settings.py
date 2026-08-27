from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_key: str
    auth_environment: str | None = None
    auth_host: str | None = None
    auth_realm: str = "cwms"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_default_region: str | None = None
    cda_api_root: str | None = None
    default_job_runner: str = "batch"
    dynamodb_host: str | None = None
    pguser: str | None = None
    pgpassword: str | None = None
    pgdatabase: str | None = None
    pghost: str | None = None
    mock_user: bool = False
    root_path: str | None = None
    s3_bucket: str | None = None
    s3_endpoint_url: str | None = None
    sqs_endpoint_url: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_empty_strings(cls, values):
        if isinstance(values, dict):
            return {
                name: value
                for name, value in values.items()
                if not (isinstance(value, str) and value.strip() == "")
            }
        return values

    @model_validator(mode="after")
    def validate_boundaries(self):
        if not self.mock_user and not self.auth_environment:
            raise ValueError("AUTH_ENVIRONMENT must be configured when MOCK_USER is false")

        if not self.mock_user and not self.cda_api_root:
            raise ValueError("CDA_API_ROOT must be configured when MOCK_USER is false")

        if self.default_job_runner == "docker-local":
            if not self.s3_bucket:
                raise ValueError("S3_BUCKET must be configured when DEFAULT_JOB_RUNNER is docker-local")
            if not self.s3_endpoint_url:
                raise ValueError("S3_ENDPOINT_URL must be configured when DEFAULT_JOB_RUNNER is docker-local")
            if not self.sqs_endpoint_url:
                raise ValueError("SQS_ENDPOINT_URL must be configured when DEFAULT_JOB_RUNNER is docker-local")

        return self

    @property
    def fastapi_root_path(self) -> str:
        return self.root_path or ""


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
