import pytest
from uuid import uuid4

from sqlalchemy.exc import NoResultFound

from cwms_batch_events.core.job_database.postgres.postgres import SlugError
from tests.factories import make_script_create_payload, make_script_payload, make_script_read


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
    ("side_effect", "expected_status", "expected_detail"),
    [
        (ValueError("bad payload"), 422, "bad payload"),
        (SlugError("slug in use"), 409, "slug in use"),
    ],
)
def test_post_script_maps_errors(client, job_db, side_effect, expected_status, expected_detail):
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
def test_put_script_maps_other_errors(client, job_db, side_effect, expected_status, expected_detail):
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
