from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_key: str = ""
    auth_environment: str = ""
    auth_host: str = "http://traefik/auth"
    auth_realm: str = "cwms"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str | None = None
    cda_api_root: str = "http://traefik/cwms-data/"
    default_job_runner: str = "batch"
    dynamodb_host: str = "http://dynamodb:9010"
    pguser: str = ""
    pgpassword: str = ""
    pgdatabase: str = "postgres"
    pghost: str = "db"
    mock_user: bool = False
    root_path: str = ""
    s3_bucket: str = ""
    s3_endpoint_url: str | None = None
    sqs_endpoint_url: str | None = None


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
