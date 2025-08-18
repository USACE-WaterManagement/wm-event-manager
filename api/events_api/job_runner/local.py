from docker import DockerClient
from docker.client import from_env
import os

from ..jobs import update_job_status
from ..schemas import JobStatus

from .base import JobRunner

CDA_HOST = os.getenv("CDA_HOST")


class LocalJobRunner(JobRunner):
    def run_job(self, office: str, script: str, job_id: str):
        client: DockerClient = from_env()

        container = client.containers.run(
            image=f"{office}-jobs",
            command=f"python /jobs/python/{script}",
            detach=True,
            remove=True,
            stderr=True,
            environment=[
                f"OFFICE={office}",
                "GITHUB_BRANCH=cwbi-dev",
                f"CDA_API_ROOT={CDA_HOST}/",
            ],
        )

        update_job_status(job_id, JobStatus.RUNNING)

        result = container.wait()
        status_code = result["StatusCode"]

        if status_code == 0:
            update_job_status(job_id, JobStatus.SUCCESS)
        else:
            update_job_status(job_id, JobStatus.FAILURE)
