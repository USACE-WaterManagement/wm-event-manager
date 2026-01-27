from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = ""
    app_key: str = ""
    auth_host: str = "http://traefik/auth"
    auth_realm: str = "cwms"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-gov-west-1"
    cda_host: str = "http://traefik/cwms-data"
    default_job_runner: str = "batch"
    dynamodb_host: str = "http://dynamodb:9010"
    pguser: str = ""
    pgpassword: str = ""
    pgdatabase: str = "postgres"
    pghost: str = "db"
    mock_user: bool = False
    s3_endpoint_url: str = "http://minio:9000"
    sqs_endpoint_url: str = "http://elasticmq:9324"
    wm_event_manager_s3_bucket: str = "wm-event-manager-local"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
