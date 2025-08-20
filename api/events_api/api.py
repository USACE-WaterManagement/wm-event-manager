from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from .auth.user import User
from .catalog import get_scripts_catalog
from .dependencies import get_current_user, get_job_database
from .job_database.base import JobDatabase
from .job_runner.base import JobRunner
from .job_runner.local import LocalJobRunner
from .schemas import ScriptRunRequest

router = APIRouter()
runner: JobRunner = LocalJobRunner()


@router.get("/jobs")
def get_jobs_for_user(
    user: User = Depends(get_current_user),
    job_db: JobDatabase = Depends(get_job_database),
):
    job_list = job_db.get_jobs_for_user(user.username)
    return job_list


@router.get("/jobs/{job_id}")
def get_job_by_id(
    job_id: str,
    user: User = Depends(get_current_user),
    job_db: JobDatabase = Depends(get_job_database),
):
    job = job_db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=404, detail=f"No job found for jobId '{job_id}'"
        )
    return job


@router.post("/scripts/execute")
def execute_script(
    payload: ScriptRunRequest,
    background_tasks: BackgroundTasks,
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

    background_tasks.add_task(
        runner.run_job, payload.office_name, payload.script_name, job.job_id
    )

    return job


@router.get("/scripts/catalog")
def get_user_scripts_catalog(user: User = Depends(get_current_user)):
    all_scripts = {}
    for office in user.offices:
        office_scripts = get_scripts_catalog(office)
        if office_scripts:
            all_scripts[office] = office_scripts
    return all_scripts
