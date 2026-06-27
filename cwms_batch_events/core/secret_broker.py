import json
import os
import base64
import hashlib
import hmac
import time
from functools import lru_cache
from uuid import UUID

import boto3
from botocore.exceptions import ClientError

from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.models import (
    RuntimeEnvResponse,
    _reject_aws_batch_reserved_env_names,
    _reject_batch_events_reserved_env_names,
)
from cwms_batch_events.core.settings import settings
from cwms_batch_events.lambdas.dispatch_job.utils import OFFICES


class SecretBrokerError(Exception):
    pass


class MissingJobError(SecretBrokerError):
    pass


class MissingSecretError(SecretBrokerError):
    pass


class InvalidRuntimeEnvError(SecretBrokerError):
    pass


def _reject_reserved_runtime_env_names(names: list[str]) -> None:
    try:
        _reject_aws_batch_reserved_env_names(names)
        _reject_batch_events_reserved_env_names(names)
    except ValueError as e:
        raise InvalidRuntimeEnvError(str(e)) from e


def _secret_name_for_office(office: str) -> str:
    office_lower = office.lower()
    office_group = OFFICES[office_lower]["division"]
    template = os.getenv(
        "BATCH_JOB_SECRET_NAME_TEMPLATE",
        "cwms-batch-jobs-{office_group}-secrets",
    )
    return template.format(office=office_lower, office_group=office_group)


@lru_cache
def _secrets_client():
    return boto3.client("secretsmanager")


def _read_secret_json(secret_id: str) -> dict[str, str]:
    local_secrets_file = os.getenv("BATCH_JOB_SECRETS_FILE", "")
    if local_secrets_file:
        try:
            with open(local_secrets_file, encoding="utf-8") as file:
                all_secrets = json.load(file)
        except OSError as e:
            raise MissingSecretError(
                f"Unable to read local secrets file '{local_secrets_file}'"
            ) from e
        except json.JSONDecodeError as e:
            raise MissingSecretError(
                f"Local secrets file '{local_secrets_file}' is not valid JSON"
            ) from e

        value = all_secrets.get(secret_id, all_secrets)
        if not isinstance(value, dict):
            raise MissingSecretError(
                f"Local secret '{secret_id}' must contain a JSON object"
            )
        return value

    try:
        response = _secrets_client().get_secret_value(SecretId=secret_id)
    except ClientError as e:
        raise MissingSecretError(f"Unable to read secret '{secret_id}'") from e

    secret_string = response.get("SecretString")
    if not secret_string:
        raise MissingSecretError(f"Secret '{secret_id}' has no SecretString")

    try:
        value = json.loads(secret_string)
    except json.JSONDecodeError as e:
        raise MissingSecretError(f"Secret '{secret_id}' is not valid JSON") from e

    if not isinstance(value, dict):
        raise MissingSecretError(f"Secret '{secret_id}' must contain a JSON object")

    return value


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _sign_job_context(job) -> str | None:
    secret = settings.batch_job_context_secret
    if not secret:
        return None
    if len(secret) < 32:
        raise SecretBrokerError("BATCH_JOB_CONTEXT_SECRET must be at least 32 characters")

    now = int(time.time())
    payload = {
        "iss": settings.batch_job_context_issuer,
        "aud": settings.batch_job_context_audience,
        "sub": job.username,
        "requested_by": job.username,
        "dispatch_source": "batch-events",
        "iat": now,
        "exp": now + settings.batch_job_context_ttl_seconds,
        "job_id": str(job.id),
        "script_id": str(job.script_id) if job.script_id else None,
        "script_slug": job.script_slug,
        "run_as_office": job.office.upper(),
        "script_office": job.office.upper(),
        "office": job.office.upper(),
        "runtime": job.runtime,
        "resource_profile": job.resource_profile,
        "command_args": job.command_args,
        "timeout_minutes": job.timeout_minutes,
    }
    header = {"alg": "HS256", "typ": "JWT", "kid": settings.batch_job_context_key_id}
    signing_input = ".".join(
        [
            _base64url(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _base64url(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(
        secret.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_base64url(signature)}"


def resolve_runtime_env(job_id: UUID, job_db: JobDatabase) -> RuntimeEnvResponse:
    job = job_db.get_job_by_id(job_id)
    if not job:
        raise MissingJobError(f"Job {job_id} does not exist")

    env_vars = dict(job.env_vars)
    _reject_reserved_runtime_env_names(list(env_vars))

    job_context_token = _sign_job_context(job)
    if job_context_token:
        env_vars["BATCH_JOB_CONTEXT_TOKEN"] = job_context_token

    requested_secret_names = list(dict.fromkeys(job.secret_env_names))
    _reject_reserved_runtime_env_names(requested_secret_names)
    if not requested_secret_names:
        return RuntimeEnvResponse(env_vars=env_vars)

    secret_values = _read_secret_json(_secret_name_for_office(job.office))
    secret_key_by_env_name = {}
    office_prefix = job.office.upper()
    for name in requested_secret_names:
        if name in secret_values:
            secret_key_by_env_name[name] = name
            continue

        prefixed_name = f"{office_prefix}_{name}"
        if prefixed_name in secret_values:
            secret_key_by_env_name[name] = prefixed_name

    missing = [
        name for name in requested_secret_names if name not in secret_key_by_env_name
    ]
    if missing:
        raise MissingSecretError(
            f"Missing secret keys for job {job_id}: {', '.join(missing)}"
        )

    for name in requested_secret_names:
        value = secret_values[secret_key_by_env_name[name]]
        if not isinstance(value, str):
            value = json.dumps(value)
        env_vars[name] = value

    return RuntimeEnvResponse(env_vars=env_vars)
