from fastapi import APIRouter
from .job_runner.local import LocalJobRunner

runner = LocalJobRunner()

router = APIRouter()


@router.get("/")
async def test():
    return runner.run_job("lrh", "test.py")
