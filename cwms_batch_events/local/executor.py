from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.job_logger.base import JobLogger
from cwms_batch_events.core.models import JobMessage, JobStatus
from cwms_batch_events.core.runtime_auth import create_runtime_token
from cwms_batch_events.core.settings import settings

CDA_API_ROOT = settings.cda_api_root


class LocalExecutor:
    def __init__(self, db: JobDatabase, logger: JobLogger):
        self.db = db
        self.logger = logger

    def run_job(self, message: JobMessage):
        from docker import DockerClient
        from docker.client import from_env

        client: DockerClient = from_env()
        container = None

        try:
            command = {
                "python": ["python", f"/jobs/{message.payload.repo_path}"],
                "node": ["node", f"/jobs/{message.payload.repo_path}"],
                "java": ["bash", f"/jobs/{message.payload.repo_path}"],
                "shell": ["bash", f"/jobs/{message.payload.repo_path}"],
            }[message.payload.runtime]
            command = [*command, *message.payload.command_args]

            environment = [
                f"OFFICE={message.payload.office}",
                f"RUNTIME={message.payload.runtime}",
                f"SCRIPT_PATH={message.payload.repo_path}",
                f"JOB_ID={message.job_id}",
                "GITHUB_BRANCH=cwbi-dev",
                "SKIP_GIT_CLONE=true",
                "ENVIRONMENT=local",
                f"CDA_API_ROOT={CDA_API_ROOT}",
            ]
            if settings.batch_events_api_root:
                environment.append(
                    f"BATCH_EVENTS_API_ROOT={settings.batch_events_api_root}"
                )
            if settings.batch_events_internal_token:
                environment.append(
                    f"BATCH_EVENTS_INTERNAL_TOKEN={settings.batch_events_internal_token}"
                )
            if settings.app_key:
                environment.append(
                    f"BATCH_EVENTS_RUNTIME_TOKEN={create_runtime_token(message.job_id)}"
                )
            environment.extend(
                f"{name}={value}" for name, value in message.payload.env_vars.items()
            )

            container = client.containers.run(
                image=f"{message.payload.office}-jobs",
                command=command,
                detach=True,
                stderr=True,
                stdout=True,
                environment=environment,
                network="cwms",
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

        except Exception as exc:
            if container:
                try:
                    logs = container.logs().decode("utf-8")
                    self.logger.push_logs_for_job(
                        message.job_id, f"{logs}\nLocal executor error: {exc}\n"
                    )
                except Exception:
                    pass
            self.db.update_job_status(message.job_id, JobStatus.FAILED)
            raise

        finally:
            if container:
                try:
                    container.remove()
                except Exception:
                    pass
