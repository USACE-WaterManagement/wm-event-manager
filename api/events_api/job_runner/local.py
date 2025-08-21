from docker import DockerClient
from docker.client import from_env
import os


from ..job_logger.base import JobLogger
from ..jobs import update_job_status
from ..schemas import JobStatus

CDA_HOST = os.getenv("CDA_HOST")


class LocalJobRunner:
    def __init__(self, logger: JobLogger):
        self.logger = logger

    def run_job(self, office: str, script: str, job_id: str):
        client: DockerClient = from_env()
        container = None

        try:
            container = client.containers.run(
                image=f"{office}-jobs",
                command=f"python /jobs/python/{script}",
                detach=True,
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

            logs = container.logs().decode("utf-8")
            self.logger.push_logs_for_job(job_id, logs)

            if status_code == 0:
                update_job_status(job_id, JobStatus.COMPLETED)
            else:
                update_job_status(job_id, JobStatus.FAILED)

        except Exception:
            update_job_status(job_id, JobStatus.FAILED)

        finally:
            if container:
                try:
                    container.remove()
                except Exception:
                    pass
