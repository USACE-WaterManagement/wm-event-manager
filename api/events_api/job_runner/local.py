from docker import DockerClient
from docker.client import from_env

from ..job_database.base import JobDatabase
from ..job_logger.base import JobLogger
from ..schemas import JobStatus
from ..settings import settings

CDA_HOST = settings.cda_host


class LocalJobRunner:
    def __init__(self, db: JobDatabase, logger: JobLogger):
        self.db = db
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

            self.db.update_job_status(job_id, JobStatus.RUNNING)

            result = container.wait()
            status_code = result["StatusCode"]

            logs = container.logs().decode("utf-8")
            self.logger.push_logs_for_job(job_id, logs)

            if status_code == 0:
                self.db.update_job_status(job_id, JobStatus.COMPLETED)
            else:
                self.db.update_job_status(job_id, JobStatus.FAILED)

        except Exception:
            self.db.update_job_status(job_id, JobStatus.FAILED)

        finally:
            if container:
                try:
                    container.remove()
                except Exception:
                    pass
