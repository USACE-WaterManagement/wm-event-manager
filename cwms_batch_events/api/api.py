from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from uuid import UUID


from cwms_batch_events.core.auth.user import User
from cwms_batch_events.core.catalog import get_scripts_catalog
from cwms_batch_events.api.dependencies import (
    get_current_user,
    get_job_database,
    get_job_logger,
    get_job_queue,
)
from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.job_logger.base import JobLogger
from cwms_batch_events.core.models import (
    JobLogs,
    JobRecord,
    JobSource,
    ScriptRunRequest,
    OfficeCatalogs,
)
from cwms_batch_events.core.queue import JobQueue

router = APIRouter()


@router.get("/jobs")
def get_jobs_for_user(
    user: User = Depends(get_current_user),
    job_db: JobDatabase = Depends(get_job_database),
) -> list[JobRecord]:
    job_list = job_db.get_jobs_for_user(user.username)
    return job_list


@router.post("/jobs")
def post_job(
    payload: ScriptRunRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    job_db: JobDatabase = Depends(get_job_database),
    queue: JobQueue = Depends(get_job_queue),
) -> JobRecord:
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

    message = queue.create_job_message(job.id, user.username, JobSource.API, payload)
    background_tasks.add_task(queue.send_job_message, message)

    return job


@router.get("/jobs/{job_id}")
def get_job_by_id(
    job_id: UUID,
    user: User = Depends(get_current_user),
    job_db: JobDatabase = Depends(get_job_database),
) -> JobRecord:
    job = job_db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=404, detail=f"No job found for jobId '{job_id}'"
        )
    return job


@router.get("/jobs/{job_id}/logs")
def get_logs_for_job(
    job_id: UUID, job_logger: JobLogger = Depends(get_job_logger)
) -> JobLogs:
    logs = job_logger.get_logs_for_job(job_id)
    return JobLogs(logs=logs)


@router.get("/scripts/catalog")
def get_user_scripts_catalog(
    user: User = Depends(get_current_user),
) -> OfficeCatalogs:
    all_scripts = OfficeCatalogs(catalogs={})
    for office in user.offices:
        office_scripts = get_scripts_catalog(office)
        if office_scripts:
            all_scripts.catalogs[office] = office_scripts
    return all_scripts
