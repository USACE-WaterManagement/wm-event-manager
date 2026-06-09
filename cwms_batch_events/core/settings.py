from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_key: str = ""
    auth_environment: str = ""
    auth_audience: str = "cwms"
    auth_client_id: str = "cwms"
    auth_host: str = "http://traefik/auth"
    auth_realm: str = "cwms"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_default_region: str | None = None
    cda_api_root: str = "http://traefik/cwms-data/"
    default_job_runner: str = "batch"
    dynamodb_host: str = "http://dynamodb:9010"
    pguser: str = ""
    pgpassword: str = ""
    pgdatabase: str = "postgres"
    pghost: str = "db"
    pgschema: str = ""
    mock_user: bool = False
    root_path: str = ""
    s3_bucket: str = ""
    s3_endpoint_url: str | None = None
    sqs_endpoint_url: str | None = None
    batch_events_api_root: str = ""
    batch_events_internal_token: str = ""
    batch_job_context_secret: str = ""
    batch_job_context_previous_secret: str = ""
    batch_job_context_key_id: str = "current"
    batch_job_context_issuer: str = "cwms-batch-events"
    batch_job_context_audience: str = "cwms-data-api"
    batch_job_context_ttl_seconds: int = 900
    batch_runtime_token_ttl_seconds: int = 600


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
