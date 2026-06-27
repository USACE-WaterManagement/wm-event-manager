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
