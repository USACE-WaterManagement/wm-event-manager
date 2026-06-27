from fastapi import APIRouter

from cwms_batch_events.core.models import DefaultJobRunner
from cwms_batch_events.core.utils import get_runner_id, get_runner_slug

router = APIRouter(prefix="/job-runners", tags=["job-runners"])


@router.get("/default")
def get_default_job_runner() -> DefaultJobRunner:
    return DefaultJobRunner(id=get_runner_id(), slug=get_runner_slug())
