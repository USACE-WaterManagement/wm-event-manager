from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from cwms_batch_events.core.job_database.postgres.postgres import PostgresJobDatabase
from cwms_batch_events.core.models import JobStatus, ScriptRunRequest
from tests.factories import make_user


class FakeScalars:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


def make_script_model(**overrides):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=overrides.pop("id", uuid4()),
        slug=overrides.pop("slug", "test-script"),
        office=overrides.pop("office", "SWT"),
        name=overrides.pop("name", "Test Script"),
        description=overrides.pop("description", "desc"),
        repo_path=overrides.pop("repo_path", "run.py"),
        execution_type=overrides.pop("execution_type", "python"),
        runtime=overrides.pop("runtime", "python"),
        resource_profile=overrides.pop("resource_profile", "small"),
        command_args=overrides.pop("command_args", []),
        timeout_minutes=overrides.pop("timeout_minutes", 30),
        schedule_enabled=overrides.pop("schedule_enabled", False),
        schedule_type=overrides.pop("schedule_type", "manual"),
        schedule_minute=overrides.pop("schedule_minute", None),
        schedule_cron=overrides.pop("schedule_cron", None),
        schedule_timezone=overrides.pop("schedule_timezone", "UTC"),
        env_vars=overrides.pop("env_vars", {}),
        secret_env_names=overrides.pop("secret_env_names", []),
        active=overrides.pop("active", True),
        roles=overrides.pop("roles", ["CWMS Users"]),
        job_runners=overrides.pop("job_runners", []),
        created_time=overrides.pop("created_time", now),
        updated_time=overrides.pop("updated_time", now),
        **overrides,
    )


def test_create_job_copies_registry_fields_to_job_record(monkeypatch):
    script_id = uuid4()
    runner_id = uuid4()
    added_jobs = []
    script = SimpleNamespace(
        id=script_id,
        name="Hourly Guard",
        slug="hourly-guard",
        active=True,
        roles=["CWMS Users"],
        office="SWT",
        repo_path="bin/hourly.sh",
        execution_type="python",
        runtime="shell",
        resource_profile="large",
        command_args=["--project", "KEYS"],
        timeout_minutes=45,
        schedule_enabled=True,
        schedule_type="hourly",
        schedule_minute=17,
        schedule_cron=None,
        schedule_timezone="America/Chicago",
        env_vars={"CDA_API_ROOT": "https://cda"},
        secret_env_names=["CDA_CLIENT_ID", "CDA_CLIENT_SECRET"],
        job_runners=[],
    )

    def refresh(job):
        job.created_time = datetime.now(timezone.utc)
        job.run_time = None
        job.end_time = None
        job.external_job_id = None

    db_session = SimpleNamespace(
        get_one=lambda model, id_: script,
        add=lambda job: added_jobs.append(job),
        commit=lambda: None,
        refresh=refresh,
    )
    job_db = PostgresJobDatabase(db_session)
    monkeypatch.setattr(
        "cwms_batch_events.core.job_database.postgres.postgres.get_runner_id",
        lambda: runner_id,
    )

    job = job_db.create_job(ScriptRunRequest(script_id=script_id), make_user())

    assert added_jobs
    assert job.job_status == JobStatus.PENDING
    assert job.script_id == script_id
    assert job.script_name == "Hourly Guard"
    assert job.script_slug == "hourly-guard"
    assert job.office == "SWT"
    assert job.repo_path == "bin/hourly.sh"
    assert job.runtime == "shell"
    assert job.resource_profile == "large"
    assert job.command_args == ["--project", "KEYS"]
    assert job.timeout_minutes == 45
    assert job.schedule_enabled is True
    assert job.schedule_type == "hourly"
    assert job.schedule_minute == 17
    assert job.schedule_timezone == "America/Chicago"
    assert job.env_vars == {"CDA_API_ROOT": "https://cda"}
    assert job.secret_env_names == ["CDA_CLIENT_ID", "CDA_CLIENT_SECRET"]
    assert job.job_runner_id == runner_id


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


def test_retrieve_scheduled_script_catalog_filters_to_active_authorized_schedules():
    due_script = make_script_model(
        id=uuid4(),
        slug="swt-hourly",
        office="SWT",
        schedule_enabled=True,
        schedule_type="hourly",
        schedule_minute=15,
    )
    db_session = SimpleNamespace(
        scalars=lambda _statement: FakeScalars(
            [
                due_script,
                make_script_model(
                    slug="inactive",
                    active=False,
                    schedule_enabled=True,
                    schedule_type="hourly",
                    schedule_minute=15,
                ),
                make_script_model(
                    slug="manual",
                    schedule_enabled=True,
                    schedule_type="manual",
                ),
                make_script_model(
                    slug="wrong-role",
                    schedule_enabled=True,
                    schedule_type="hourly",
                    schedule_minute=15,
                    roles=["Data Acquisition Mgr"],
                ),
                make_script_model(
                    slug="wrong-office",
                    office="LRL",
                    schedule_enabled=True,
                    schedule_type="hourly",
                    schedule_minute=15,
                ),
            ]
        )
    )
    job_db = PostgresJobDatabase(db_session)

    scripts = job_db.retrieve_scheduled_script_catalog({"SWT": ["CWMS Users"]})

    assert [script.slug for script in scripts] == ["swt-hourly"]
    assert scripts[0].schedule_enabled is True
    assert scripts[0].schedule_type == "hourly"
    assert scripts[0].schedule_minute == 15
    assert scripts[0].schedule_timezone == "UTC"


def test_retrieve_scheduled_script_catalog_includes_authorized_cron_schedules():
    cron_script = make_script_model(
        slug="swt-cron",
        office="SWT",
        schedule_enabled=True,
        schedule_type="cron",
        schedule_cron="5 17 * * *",
    )
    db_session = SimpleNamespace(
        scalars=lambda _statement: FakeScalars([cron_script])
    )
    job_db = PostgresJobDatabase(db_session)

    scripts = job_db.retrieve_scheduled_script_catalog({"SWT": ["CWMS Users"]})

    assert [script.slug for script in scripts] == ["swt-cron"]
    assert scripts[0].schedule_type == "cron"
    assert scripts[0].schedule_cron == "5 17 * * *"
