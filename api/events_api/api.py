from fastapi import APIRouter, Depends, HTTPException

from .job_database.job_database import get_job_database, JobDatabase

from .auth.user import get_current_user, User
from .catalog import get_scripts_catalog
from .job_runner.local import LocalJobRunner
from .schemas import ScriptRunRequest

runner = LocalJobRunner()

router = APIRouter()


@router.get("/jobs")
def get_jobs_for_user(
    user: User = Depends(get_current_user),
    job_db: JobDatabase = Depends(get_job_database),
):
    job_list = job_db.get_jobs_for_user(user.username)
    return job_list


@router.post("/scripts/execute")
def execute_script(
    payload: ScriptRunRequest,
    user: User = Depends(get_current_user),
    job_db: JobDatabase = Depends(get_job_database),
):
    if payload.office_name not in user.offices:
        raise HTTPException(
            status_code=403,
            detail=f"Not authorized to run scripts for {payload.office_name}.",
        )

    catalog = get_scripts_catalog(payload.office_name)
    if not catalog:
        raise HTTPException(
            status_code=403,
            detail=f"No script catalog found for {payload.office_name}.",
        )

    scripts = catalog.scripts
    if payload.script_name not in scripts:
        raise HTTPException(
            status_code=403,
            detail=f"Script {payload.script_name} not found for office {payload.office_name}.",
        )

    job = job_db.create_job(payload, user.username)
    runner.run_job(payload.office_name, payload.script_name, job.job_id)

    return job.model_dump_json(by_alias=True)


@router.get("/scripts/catalog")
def get_user_scripts_catalog(user: User = Depends(get_current_user)):
    all_scripts = {}
    for office in user.offices:
        office_scripts = get_scripts_catalog(office)
        if office_scripts:
            all_scripts[office] = office_scripts
    return all_scripts
