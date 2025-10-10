from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth_host: str = "http://traefik/auth"
    auth_realm: str = "cwms"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    cda_host: str = "http://traefik/cwms-data"
    dynamodb_host: str = "http://dynamodb:9010"
    mock_user: bool = False
    s3_endpoint_url: str = "http://minio:9000"
    wm_event_manager_s3_bucket: str = "wm-event-manager-local"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
