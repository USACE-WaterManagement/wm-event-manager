import time
from uuid import uuid4

from cwms_batch_events.core.runtime_auth import create_runtime_token, verify_runtime_token
from cwms_batch_events.core.settings import settings


def test_runtime_token_verifies_for_matching_job(monkeypatch):
    job_id = uuid4()
    monkeypatch.setattr(settings, "app_key", "test-runtime-token-secret-with-32-chars")

    token = create_runtime_token(job_id)

    assert verify_runtime_token(token, job_id) is True


def test_runtime_token_rejects_wrong_job(monkeypatch):
    monkeypatch.setattr(settings, "app_key", "test-runtime-token-secret-with-32-chars")

    token = create_runtime_token(uuid4())

    assert verify_runtime_token(token, uuid4()) is False


def test_runtime_token_rejects_expired_token(monkeypatch):
    job_id = uuid4()
    monkeypatch.setattr(settings, "app_key", "test-runtime-token-secret-with-32-chars")
    monkeypatch.setattr(settings, "batch_runtime_token_ttl_seconds", -1)

    token = create_runtime_token(job_id)
    time.sleep(1)

    assert verify_runtime_token(token, job_id) is False
