"""Read-only file catalogs for configured district job repositories."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException

from cwms_batch_events.api.dependencies import get_current_user
from cwms_batch_events.api.routers.scripts import check_user_office_admin
from cwms_batch_events.core.auth.user.models import User
from cwms_batch_events.core.settings import settings

router = APIRouter(tags=["repositories"])


@router.get("/repository-files")
def repository_files(office: str, user: User = Depends(get_current_user)):
    office = office.upper()
    check_user_office_admin(user, office)
    config = settings.office_repositories.get(office)
    if config is None:
        raise HTTPException(404, "No job repository configured for this office")
    url = f"https://api.github.com/repos/{config.repository}/git/trees/{quote(config.ref, safe='')}?recursive=1"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "cwms-batch-events"}
    token = settings.github_token.get_secret_value()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urlopen(Request(url, headers=headers), timeout=15) as response:
            catalog = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        raise HTTPException(502, "Repository files are unavailable; check repository configuration and access") from error
    if catalog.get("truncated"):
        raise HTTPException(502, "Repository file list is too large to browse; enter the path manually")
    return {
        "repository": config.repository,
        "ref": config.ref,
        "paths": [item["path"] for item in catalog.get("tree", []) if item.get("type") == "blob"],
    }
