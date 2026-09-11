import io
import json
from unittest.mock import patch
from urllib.error import URLError

import pytest

from cwms_batch_events.core.settings import RepositorySettings, settings


@pytest.fixture
def configured_repository(monkeypatch, user):
    office = user.admin_offices[0]
    monkeypatch.setattr(settings, "office_repositories", {
        office: RepositorySettings(repository="example/district-jobs", ref="release/jobs")
    })
    return office


def test_catalog_uses_configured_repository(client, configured_repository):
    payload = {"tree": [{"path": "python/report.py", "type": "blob"}, {"path": "python", "type": "tree"}]}
    with patch("cwms_batch_events.api.routers.repository_files.urlopen", return_value=io.BytesIO(json.dumps(payload).encode())) as request:
        response = client.get("/repository-files", params={"office": configured_repository.lower()})
    assert response.status_code == 200
    assert response.json() == {"repository": "example/district-jobs", "ref": "release/jobs", "paths": ["python/report.py"]}
    assert "release%2Fjobs?recursive=1" in request.call_args.args[0].full_url


def test_catalog_requires_office_admin(client):
    with patch("cwms_batch_events.api.routers.repository_files.urlopen") as request:
        response = client.get("/repository-files?office=UNAUTHORIZED")
    assert response.status_code == 401
    request.assert_not_called()


def test_missing_repository(client, user, monkeypatch):
    monkeypatch.setattr(settings, "office_repositories", {})
    assert client.get("/repository-files", params={"office": user.admin_offices[0]}).status_code == 404


def test_incomplete_catalog_is_not_silently_displayed(client, configured_repository):
    with patch("cwms_batch_events.api.routers.repository_files.urlopen", return_value=io.BytesIO(b'{"truncated":true}')):
        assert client.get("/repository-files", params={"office": configured_repository}).status_code == 502


def test_github_errors_do_not_expose_credentials(client, configured_repository):
    with patch("cwms_batch_events.api.routers.repository_files.urlopen", side_effect=URLError("private error")):
        response = client.get("/repository-files", params={"office": configured_repository})
    assert response.status_code == 502
    assert "private error" not in response.text
