import pytest
from uuid import uuid4

from sqlalchemy.exc import NoResultFound

from cwms_batch_events.core.job_database.postgres.postgres import SlugError
from tests.factories import (
    make_script_create_payload,
    make_script_payload,
    make_script_read,
)


def test_get_scripts_for_office_requires_admin_access(client):
    response = client.get("/scripts", params={"office": "LRH"})

    assert response.status_code == 401
    assert response.json() == {
        "detail": "User does not have script admin access for office 'LRH'"
    }


def test_get_scripts_for_office_returns_scripts(client, job_db):
    script = make_script_read()
    job_db.get_scripts_for_office.return_value = [script]

    response = client.get("/scripts", params={"office": "SWT"})

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(script.id)
    job_db.get_scripts_for_office.assert_called_once_with("SWT")


def test_post_script_returns_created_script(client, job_db):
    script = make_script_read()
    job_db.store_script.return_value = script

    response = client.post("/scripts", json=make_script_create_payload())

    assert response.status_code == 200
    assert response.json()["id"] == str(script.id)
    job_db.store_script.assert_called_once()


@pytest.mark.parametrize(
    ("payload", "expected_detail"),
    [
        (
            make_script_create_payload(
                scheduleEnabled=True,
                scheduleType="hourly",
                scheduleMinute=None,
            ),
            "scheduleMinute is required when scheduleEnabled is true and scheduleType is hourly",
        ),
        (
            make_script_create_payload(
                scheduleEnabled=True,
                scheduleType="cron",
                scheduleCron=None,
            ),
            "scheduleCron is required when scheduleEnabled is true and scheduleType is cron",
        ),
        (
            make_script_create_payload(
                scheduleEnabled=True,
                scheduleType="manual",
            ),
            "scheduleType must be hourly or cron when scheduleEnabled is true",
        ),
    ],
)
def test_post_script_rejects_incomplete_enabled_schedules(
    client, job_db, payload, expected_detail
):
    response = client.post("/scripts", json=payload)

    assert response.status_code == 422
    assert expected_detail in response.text
    job_db.store_script.assert_not_called()


@pytest.mark.parametrize(
    ("payload", "expected_detail"),
    [
        (
            make_script_create_payload(runtime="ruby"),
            "runtime must be one of: python, node, java, shell",
        ),
        (
            make_script_create_payload(resourceProfile="huge"),
            "resourceProfile must be one of: small, medium, large",
        ),
        (
            make_script_create_payload(timeoutMinutes=0),
            "timeoutMinutes must be between 1 and 1440",
        ),
        (
            make_script_create_payload(timeoutMinutes=1441),
            "timeoutMinutes must be between 1 and 1440",
        ),
        (
            make_script_create_payload(scheduleMinute=60),
            "scheduleMinute must be between 0 and 59",
        ),
        (
            make_script_create_payload(scheduleCron="0 17 * *"),
            "scheduleCron must be a five-field cron expression",
        ),
        (
            make_script_create_payload(envVars={"AWS_BATCH_FOO": "bad"}),
            "environment variable names cannot start with AWS_BATCH",
        ),
        (
            make_script_create_payload(secretEnvNames=["AWS_BATCH_TOKEN"]),
            "environment variable names cannot start with AWS_BATCH",
        ),
        (
            make_script_create_payload(envVars={"JOB_ID": "bad"}),
            "environment variable names are reserved for Batch Events runtime",
        ),
        (
            make_script_create_payload(secretEnvNames=["BATCH_EVENTS_INTERNAL_TOKEN"]),
            "environment variable names are reserved for Batch Events runtime",
        ),
        (
            make_script_create_payload(commandArgs=["--project", ""]),
            "commandArgs cannot contain empty strings",
        ),
    ],
)
def test_post_script_rejects_invalid_registry_controls(
    client, job_db, payload, expected_detail
):
    response = client.post("/scripts", json=payload)

    assert response.status_code == 422
    assert expected_detail in response.text
    job_db.store_script.assert_not_called()


@pytest.mark.parametrize(
    ("side_effect", "expected_status", "expected_detail"),
    [
        (ValueError("bad payload"), 422, "bad payload"),
        (SlugError("slug in use"), 409, "slug in use"),
    ],
)
def test_post_script_maps_errors(
    client, job_db, side_effect, expected_status, expected_detail
):
    job_db.store_script.side_effect = side_effect

    response = client.post("/scripts", json=make_script_create_payload())

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}


def test_put_script_returns_updated_script(client, job_db):
    script = make_script_read()
    job_db.update_script.return_value = script

    response = client.put(f"/scripts/{script.id}", json=make_script_payload())

    assert response.status_code == 200
    assert response.json()["id"] == str(script.id)
    job_db.update_script.assert_called_once()


def test_put_script_rejects_incomplete_enabled_schedule(client, job_db):
    response = client.put(
        f"/scripts/{uuid4()}",
        json=make_script_payload(
            scheduleEnabled=True,
            scheduleType="hourly",
            scheduleMinute=None,
        ),
    )

    assert response.status_code == 422
    assert (
        "scheduleMinute is required when scheduleEnabled is true and scheduleType is hourly"
        in response.text
    )
    job_db.update_script.assert_not_called()


def test_put_script_returns_404_when_missing(client, job_db):
    job_db.update_script.side_effect = NoResultFound()
    script_id = str(uuid4())

    response = client.put(f"/scripts/{script_id}", json=make_script_payload())

    assert response.status_code == 404
    assert response.json() == {"detail": f"Script {script_id} not found"}


@pytest.mark.parametrize(
    ("side_effect", "expected_status", "expected_detail"),
    [
        (PermissionError("no access"), 401, "no access"),
        (ValueError("bad payload"), 422, "bad payload"),
    ],
)
def test_put_script_maps_other_errors(
    client, job_db, side_effect, expected_status, expected_detail
):
    job_db.update_script.side_effect = side_effect

    response = client.put(f"/scripts/{uuid4()}", json=make_script_payload())

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}


def test_delete_script_returns_no_content(client, job_db):
    script_id = str(uuid4())

    response = client.delete(f"/scripts/{script_id}")

    assert response.status_code == 204
    job_db.remove_script_if_allowed.assert_called_once()


def test_delete_script_returns_404_when_missing(client, job_db):
    job_db.remove_script_if_allowed.side_effect = NoResultFound()
    script_id = str(uuid4())

    response = client.delete(f"/scripts/{script_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Script {script_id} not found"}


def test_delete_script_returns_401_for_permission_error(client, job_db):
    script_id = str(uuid4())
    job_db.remove_script_if_allowed.side_effect = PermissionError("no access")

    response = client.delete(f"/scripts/{script_id}")

    assert response.status_code == 401
    assert response.json() == {"detail": "no access"}


def test_get_scripts_catalog_returns_role_filtered_catalog(client, job_db):
    script = make_script_read()
    job_db.retrieve_script_catalog.return_value = [script]

    response = client.get("/scripts/catalog")

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(script.id)
    job_db.retrieve_script_catalog.assert_called_once_with(
        {"SWT": ["CWMS Users"], "LRH": ["CWMS Users"]}
    )


def test_get_scheduled_scripts_catalog_returns_role_filtered_schedules(client, job_db):
    script = make_script_read(
        schedule_enabled=True,
        schedule_type="hourly",
        schedule_minute=15,
    )
    job_db.retrieve_scheduled_script_catalog.return_value = [script]

    response = client.get("/scripts/scheduled")

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(script.id)
    assert response.json()[0]["scheduleEnabled"] is True
    assert response.json()[0]["scheduleType"] == "hourly"
    assert response.json()[0]["scheduleMinute"] == 15
    job_db.retrieve_scheduled_script_catalog.assert_called_once_with(
        {"SWT": ["CWMS Users"], "LRH": ["CWMS Users"]}
    )


def test_get_scheduled_scripts_catalog_returns_cron_schedules(client, job_db):
    script = make_script_read(
        schedule_enabled=True,
        schedule_type="cron",
        schedule_cron="0 17 * * *",
    )
    job_db.retrieve_scheduled_script_catalog.return_value = [script]

    response = client.get("/scripts/scheduled")

    assert response.status_code == 200
    assert response.json()[0]["scheduleEnabled"] is True
    assert response.json()[0]["scheduleType"] == "cron"
    assert response.json()[0]["scheduleCron"] == "0 17 * * *"
