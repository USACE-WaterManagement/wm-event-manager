from types import SimpleNamespace
from uuid import uuid4

import pytest

from cwms_batch_events.core.job_database.postgres.postgres import PostgresJobDatabase
from cwms_batch_events.core.models import ScriptRunRequest
from tests.factories import make_user


def test_create_job_rejects_inactive_script():
    script_id = uuid4()
    db_session = SimpleNamespace(
        get_one=lambda model, id_: SimpleNamespace(
            id=script_id,
            active=False,
            roles=["CWMS Users"],
            office="SWT",
        )
    )
    job_db = PostgresJobDatabase(db_session)

    with pytest.raises(PermissionError, match="Requested script is not active"):
        job_db.create_job(ScriptRunRequest(script_id=script_id), make_user())


def test_create_job_rejects_script_not_configured_for_current_runner(monkeypatch):
    script_id = uuid4()
    configured_runner_id = uuid4()
    other_runner_id = uuid4()
    db_session = SimpleNamespace(
        get_one=lambda model, id_: SimpleNamespace(
            id=script_id,
            active=True,
            roles=["CWMS Users"],
            office="SWT",
            job_runners=[SimpleNamespace(id=other_runner_id)],
        )
    )
    job_db = PostgresJobDatabase(db_session)
    monkeypatch.setattr(
        "cwms_batch_events.core.job_database.postgres.postgres.get_runner_id",
        lambda: configured_runner_id,
    )

    with pytest.raises(
        PermissionError,
        match="Requested script is not configured for the current job runner",
    ):
        job_db.create_job(ScriptRunRequest(script_id=script_id), make_user())
