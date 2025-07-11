from fastapi import APIRouter, Depends

from .auth import get_current_user, User
from .catalog import get_scripts_catalog
from .job_runner.local import LocalJobRunner

runner = LocalJobRunner()

router = APIRouter()


@router.get("/")
async def test():
    return runner.run_job("lrh", "test.py")


@router.get("/scripts/catalog")
async def get_user_scripts_catalog(user: User = Depends(get_current_user)):
    all_scripts = {}
    for office in user.offices:
        office_scripts = get_scripts_catalog(office)
        if office_scripts:
            all_scripts[office] = office_scripts
    return all_scripts
