from .models import JobModel, JobRunnerModel
from ...schemas import JobRecord, JobRunner


def to_job_record(model: JobModel):
    return JobRecord(
        id=model.id,
        script_name=model.script_name,
        job_status=model.job_status,
        username=model.username,
        office=model.office,
        created_time=model.created_time,
        run_time=model.run_time,
        end_time=model.end_time,
        external_job_id=model.external_job_id,
        job_runner_id=model.job_runner_id,
    )


def to_job_runner(model: JobRunnerModel):
    return JobRunner(
        id=model.id,
        slug=model.slug,
        label=model.label,
        description=model.description,
        active=model.active,
        created_time=model.created_time,
    )
