from fastapi import APIRouter, Depends

from cwms_batch_events.api.dependencies import get_current_user
from cwms_batch_events.core.auth.user.models import User
from cwms_batch_events.core.catalog import get_scripts_catalog
from cwms_batch_events.core.models import OfficeCatalogs


router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.get("/catalog")
def get_user_scripts_catalog(
    user: User = Depends(get_current_user),
) -> OfficeCatalogs:
    all_scripts = OfficeCatalogs(catalogs={})
    for office in user.offices:
        office_scripts = get_scripts_catalog(office)
        if office_scripts:
            all_scripts.catalogs[office] = office_scripts
    return all_scripts
