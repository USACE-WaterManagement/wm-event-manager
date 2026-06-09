import base64
import hashlib
import hmac
import json
import time
from uuid import UUID

from cwms_batch_events.core.settings import settings

RUNTIME_TOKEN_EXPIRED = "Runtime broker token expired"
RUNTIME_TOKEN_INVALID = "Invalid runtime broker token provided"


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode_base64url(value: str) -> bytes:
    value += "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value.encode("ascii"))


def create_runtime_token(job_id: UUID) -> str:
    if not settings.app_key:
        raise RuntimeError("APP_KEY is required to sign runtime broker tokens")

    now = int(time.time())
    payload = {
        "iss": "cwms-batch-events",
        "aud": "cwms-batch-runtime-env",
        "purpose": "runtime-env",
        "job_id": str(job_id),
        "iat": now,
        "exp": now + settings.batch_runtime_token_ttl_seconds,
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _base64url(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _base64url(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(
        settings.app_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_base64url(signature)}"


def validate_runtime_token(token: str, job_id: UUID) -> tuple[bool, str | None]:
    if not settings.app_key or not token:
        return False, RUNTIME_TOKEN_INVALID

    parts = token.split(".")
    if len(parts) != 3:
        return False, RUNTIME_TOKEN_INVALID

    signing_input = ".".join(parts[:2])
    expected = hmac.new(
        settings.app_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    try:
        provided = _decode_base64url(parts[2])
        payload = json.loads(_decode_base64url(parts[1]))
    except Exception:
        return False, RUNTIME_TOKEN_INVALID

    if not hmac.compare_digest(provided, expected):
        return False, RUNTIME_TOKEN_INVALID

    now = int(time.time())
    exp = payload.get("exp")
    if not isinstance(exp, int):
        return False, RUNTIME_TOKEN_INVALID
    if exp < now:
        return False, RUNTIME_TOKEN_EXPIRED

    valid = (
        payload.get("iss") == "cwms-batch-events"
        and payload.get("aud") == "cwms-batch-runtime-env"
        and payload.get("purpose") == "runtime-env"
        and payload.get("job_id") == str(job_id)
    )
    return (True, None) if valid else (False, RUNTIME_TOKEN_INVALID)


def verify_runtime_token(token: str, job_id: UUID) -> bool:
    valid, _ = validate_runtime_token(token, job_id)
    return valid
