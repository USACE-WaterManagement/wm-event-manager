from fastapi import APIRouter, Depends, HTTPException

from .auth import get_current_user, User
from .catalog import get_scripts_catalog
from .job_runner.local import LocalJobRunner
from .schemas import ScriptRunRequest

runner = LocalJobRunner()

router = APIRouter()


@router.post("/scripts/execute")
async def execute_script(
    payload: ScriptRunRequest, user: User = Depends(get_current_user)
):
    if payload.office_name not in user.offices:
        raise HTTPException(
            status_code=403,
            detail=f"Not authorized to run scripts for {payload.office_name}.",
        )

    scripts = get_scripts_catalog(payload.office_name)["scripts"]
    if payload.script_name not in scripts:
        raise HTTPException(
            status_code=403,
            detail=f"Script {payload.script_name} not found for office {payload.office_name}.",
        )

    return runner.run_job(payload.office_name, payload.script_name)


@router.get("/scripts/catalog")
async def get_user_scripts_catalog(user: User = Depends(get_current_user)):
    all_scripts = {}
    for office in user.offices:
        office_scripts = get_scripts_catalog(office)
        if office_scripts:
            all_scripts[office] = office_scripts
    return all_scripts
