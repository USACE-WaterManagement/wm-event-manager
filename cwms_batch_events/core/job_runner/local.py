from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.job_logger.base import JobLogger
from cwms_batch_events.core.models import JobMessage, JobStatus
from cwms_batch_events.core.settings import settings

CDA_API_ROOT = settings.cda_api_root


class LocalJobRunner:
    def __init__(self, db: JobDatabase, logger: JobLogger):
        self.db = db
        self.logger = logger

    def run_job(self, message: JobMessage):
        from docker import DockerClient
        from docker.client import from_env

        client: DockerClient = from_env()
        container = None

        try:
            container = client.containers.run(
                image=f"{message.payload.office_name}-jobs",
                command=f"python /jobs/python/{message.payload.script_name}",
                detach=True,
                stderr=True,
                environment=[
                    f"OFFICE={message.payload.office_name}",
                    "GITHUB_BRANCH=cwbi-dev",
                    f"CDA_API_ROOT={CDA_API_ROOT}",
                ],
            )

            self.db.update_job_status(message.job_id, JobStatus.RUNNING)

            result = container.wait()
            status_code = result["StatusCode"]

            logs = container.logs().decode("utf-8")
            self.logger.push_logs_for_job(message.job_id, logs)

            if status_code == 0:
                self.db.update_job_status(message.job_id, JobStatus.COMPLETED)
            else:
                self.db.update_job_status(message.job_id, JobStatus.FAILED)

        except Exception:
            self.db.update_job_status(message.job_id, JobStatus.FAILED)

        finally:
            if container:
                try:
                    container.remove()
                except Exception:
                    pass
