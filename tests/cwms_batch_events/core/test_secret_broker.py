import json
import base64
from uuid import uuid4
from unittest import mock

import pytest

from cwms_batch_events.core.secret_broker import (
    InvalidRuntimeEnvError,
    MissingJobError,
    MissingSecretError,
    resolve_runtime_env,
)
from tests.factories import make_job_record


TEST_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC218vsXdIz+dgs
NDS7l6SI4U37aS5t/t9ig2soZjXV4PABqPZmPRQagutoZjDR4H+0dQMvOWcVQkMb
rwr3L07TaG1Kuwx5aw4YeaPZ4xrcotUARu4CvJIOdObCIP24WatDGRyVY+j1Hgvz
cbTimS3L9P0sp+feCL2lvceefMBxGRvftRMwTALHjrKwKV5CX8a6mSvrsinclXPG
HNxAqsgKhmOz3tjKbRjxLoMm/r57qlI4zLRuXasI3qjuJAuFYggqkM9zmF5wucjx
PZNP0YbYbHuQqOZ54BmFLoPNrueGvWJVMvF8QqrfK+hO9xJWqTze/l0F3an3BD0D
z3Lm74KRAgMBAAECgf8rQUHs2QUxZpnNW0xeVLGH8EUShP+G5hTSqWRgWk3CG0Ss
H9yqsyheXTpzqDlEbWfIuSXXtiy8ysA1fGOLtpVfTgUM+NMqpjjfcWdh1Gg2ag8Z
0a3c1991rBIrOsLLKetqJDau4MPruP/6x5uTP8mlxn9eYRppXIgA/bSLudeM6Y0c
giEdmnAh4UI730TtLdWHIaDD0PLTXK1y17as+VLAQtkSeELEC84uLwg1Av7/6wT7
jXASljGwMVt6RvwXJ0Q/5BvR9WJJ5t1jvG6nDLv9YyhQu+uUmI5kRZ6P+GoGWPG+
vNxC55ObC/BJpnt4JyuaLexl7I3zhP3aS2jd6eECgYEA6JKs31oVY0QQrhUo52e8
O4kfWiJGNgBMrgGshywR6RuIbAvnv92g9bXK2Z3QbgE+rq3XEOYzsYnY/8i5Y8Sk
EYAT1QucYkdaKp5BxT3RCokdC+ARVm/JhyFafZy/vYAcG5pv+3ztWIzVFNpK4d9e
pVeNaTUgs6BdyBEXv8CO2nECgYEAyUK9vXvvEKXQYJdHQQSZdbY+xlY05DO9RFJ8
2zYmN4sJLGgCXv8M089htRfsM16D3QcWvBnkr66GqClWvGP0ugxdWJ8uHGeSOPbi
I5w/10nGwYZAcNtCHSRbPhtrbrxX9kn5uxZBIrlheHtuBSlP0E6/TuW5ul28GQWW
GHHj+iECgYB6sZZ9pjqOScQ68nLH0ZQeHHLrzBUaPAI38i4giYFRZvMLfSRftf5K
YgOH1pe00PdOk+tXwPoYeU5/cldLaNvdV6IezKdNubK5tQ+hjMERO9CVCTpcTVEV
9uSUS/Njd4hcj5bwJ7HW+0UWYSsMChkWRSAXFq4P1VRkTZAn2uACIQKBgQCWxXDv
KpEFn7JjKfEvPArarBSK8Lne2wPG0yTF8+LdaUMOCTz9fYRWiN1hlPJV6VBPnKfj
cmJnWg92msFnkFodpnWnllgs30ojcpAmrT8GQTasc66C3T7CJiJUfKYW5vHeh7yV
8y4InWfvokfhhflMzDF1IZPpkZ7//7dZyLhJAQKBgQDbzH5WXPc78+m0cyYTWDXQ
FuAQILhy5KDvz5QTycndU5NByXQinEFqXarffQHMDZmlQKAx3qQ1pcMTdrttKqBR
mzLHWkYoY/G8SUUvSSv8Xj5Sd1otE+X8DgtyHCXoqtpuifQlVrDoVtgWuPGRJqIe
WrTwt9EtWQ/rmg/UnGm8ig==
-----END PRIVATE KEY-----"""


def _decode_payload(token: str) -> dict:
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))


def _decode_header(token: str) -> dict:
    header = token.split(".")[0]
    header += "=" * (-len(header) % 4)
    return json.loads(base64.urlsafe_b64decode(header.encode("ascii")))


def test_resolve_runtime_env_merges_nonsecret_and_allowed_secret_values():
    job_id = uuid4()
    job_db = mock.Mock()
    job_db.get_job_by_id.return_value = make_job_record(
        id=job_id,
        office="SWT",
        env_vars={"CDA_API_ROOT": "https://cda"},
        secret_env_names=["CDA_API_KEY", "API_KEYS"],
    )
    secrets_client = mock.Mock()
    secrets_client.get_secret_value.return_value = {
        "SecretString": json.dumps(
            {"SWT_CDA_API_KEY": "abc", "API_KEYS": {"vendor": "token"}}
        )
    }

    with mock.patch(
        "cwms_batch_events.core.secret_broker._secrets_client",
        return_value=secrets_client,
    ):
        response = resolve_runtime_env(job_id, job_db)

    assert response.env_vars == {
        "CDA_API_ROOT": "https://cda",
        "CDA_API_KEY": "abc",
        "API_KEYS": '{"vendor": "token"}',
    }
    secrets_client.get_secret_value.assert_called_once_with(
        SecretId="cwms-batch-jobs-swd-secrets"
    )


def test_resolve_runtime_env_maps_office_prefixed_keycloak_client_credentials():
    job_id = uuid4()
    job_db = mock.Mock()
    job_db.get_job_by_id.return_value = make_job_record(
        id=job_id,
        office="SWT",
        env_vars={
            "CDA_API_ROOT": "https://cda",
            "CDA_TOKEN_URL": "https://keycloak/realms/cwms/protocol/openid-connect/token",
        },
        secret_env_names=["CDA_CLIENT_ID", "CDA_CLIENT_SECRET"],
    )
    secrets_client = mock.Mock()
    secrets_client.get_secret_value.return_value = {
        "SecretString": json.dumps(
            {
                "SWT_CDA_CLIENT_ID": "cwms-batch-runner-swt",
                "SWT_CDA_CLIENT_SECRET": "local-cwms-batch-runner-swt-secret",
            }
        )
    }

    with mock.patch(
        "cwms_batch_events.core.secret_broker._secrets_client",
        return_value=secrets_client,
    ):
        response = resolve_runtime_env(job_id, job_db)

    assert response.env_vars == {
        "CDA_API_ROOT": "https://cda",
        "CDA_TOKEN_URL": "https://keycloak/realms/cwms/protocol/openid-connect/token",
        "CDA_CLIENT_ID": "cwms-batch-runner-swt",
        "CDA_CLIENT_SECRET": "local-cwms-batch-runner-swt-secret",
    }


def test_resolve_runtime_env_skips_secrets_when_script_needs_none():
    job_id = uuid4()
    job_db = mock.Mock()
    job_db.get_job_by_id.return_value = make_job_record(
        id=job_id,
        env_vars={"CDA_API_ROOT": "https://cda"},
        secret_env_names=[],
    )

    response = resolve_runtime_env(job_id, job_db)

    assert response.env_vars == {"CDA_API_ROOT": "https://cda"}


def test_resolve_runtime_env_adds_signed_job_context_when_configured(monkeypatch):
    job_id = uuid4()
    job_db = mock.Mock()
    job_db.get_job_by_id.return_value = make_job_record(
        id=job_id,
        office="SWT",
        env_vars={"CDA_API_ROOT": "https://cda"},
        secret_env_names=[],
        command_args=["--project", "KEYS"],
        timeout_minutes=45,
    )
    monkeypatch.setattr(
        "cwms_batch_events.core.secret_broker.settings.batch_job_context_private_key",
        TEST_PRIVATE_KEY,
    )

    response = resolve_runtime_env(job_id, job_db)

    token = response.env_vars["BATCH_JOB_CONTEXT_TOKEN"]
    payload = _decode_payload(token)
    header = _decode_header(token)
    assert header["kid"] == "current"
    assert header["alg"] == "RS256"
    assert payload["job_id"] == str(job_id)
    assert payload["run_as_office"] == "SWT"
    assert payload["office"] == "SWT"
    assert payload["requested_by"] == "test-user"
    assert payload["script_office"] == "SWT"
    assert payload["command_args"] == ["--project", "KEYS"]
    assert payload["timeout_minutes"] == 45
    assert payload["iss"] == "cwms-batch-events"
    assert payload["aud"] == "cwms-data-api"


def test_resolve_runtime_env_can_use_legacy_hmac_job_context(monkeypatch):
    job_id = uuid4()
    job_db = mock.Mock()
    job_db.get_job_by_id.return_value = make_job_record(id=job_id, office="SWT")
    monkeypatch.setattr(
        "cwms_batch_events.core.secret_broker.settings.batch_job_context_private_key",
        "",
    )
    monkeypatch.setattr(
        "cwms_batch_events.core.secret_broker.settings.batch_job_context_secret",
        "test-batch-job-context-secret-32chars",
    )

    response = resolve_runtime_env(job_id, job_db)

    header = _decode_header(response.env_vars["BATCH_JOB_CONTEXT_TOKEN"])
    assert header["alg"] == "HS256"


def test_resolve_runtime_env_requires_existing_job():
    job_db = mock.Mock()
    job_db.get_job_by_id.return_value = None

    with pytest.raises(MissingJobError):
        resolve_runtime_env(uuid4(), job_db)


def test_resolve_runtime_env_rejects_reserved_public_env_names():
    job_id = uuid4()
    job_db = mock.Mock()
    job_db.get_job_by_id.return_value = make_job_record(
        id=job_id,
        env_vars={"BATCH_EVENTS_INTERNAL_TOKEN": "bad"},
        secret_env_names=[],
    )

    with pytest.raises(InvalidRuntimeEnvError, match="reserved for Batch Events runtime"):
        resolve_runtime_env(job_id, job_db)


def test_resolve_runtime_env_rejects_reserved_secret_env_names_before_reading_secret():
    job_id = uuid4()
    job_db = mock.Mock()
    job_db.get_job_by_id.return_value = make_job_record(
        id=job_id,
        secret_env_names=["BATCH_JOB_CONTEXT_TOKEN"],
    )
    secrets_client = mock.Mock()

    with mock.patch(
        "cwms_batch_events.core.secret_broker._secrets_client",
        return_value=secrets_client,
    ), pytest.raises(InvalidRuntimeEnvError, match="reserved for Batch Events runtime"):
        resolve_runtime_env(job_id, job_db)

    secrets_client.get_secret_value.assert_not_called()


def test_resolve_runtime_env_requires_allowed_secret_key_to_exist():
    job_id = uuid4()
    job_db = mock.Mock()
    job_db.get_job_by_id.return_value = make_job_record(
        id=job_id,
        office="SWT",
        secret_env_names=["MISSING_KEY"],
    )
    secrets_client = mock.Mock()
    secrets_client.get_secret_value.return_value = {"SecretString": "{}"}

    with mock.patch(
        "cwms_batch_events.core.secret_broker._secrets_client",
        return_value=secrets_client,
    ), pytest.raises(MissingSecretError, match="MISSING_KEY"):
        resolve_runtime_env(job_id, job_db)
