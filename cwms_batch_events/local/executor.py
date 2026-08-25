import traceback

from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.job_logger.base import JobLogger
from cwms_batch_events.core.notifications import enqueue_failed_job_notifications
from cwms_batch_events.core.notification_queue import NotificationQueue
from cwms_batch_events.core.models import JobMessage, JobStatus
from cwms_batch_events.core.settings import settings

CDA_API_ROOT = settings.cda_api_root


class LocalExecutor:
    def __init__(
        self,
        db: JobDatabase,
        logger: JobLogger,
        notification_queue: NotificationQueue | None = None,
    ):
        self.db = db
        self.logger = logger
        self.notification_queue = notification_queue

    def _send_failed_job_alert(
        self,
        message: JobMessage,
        *,
        error_message: str | None = None,
        logs: str | None = None,
    ):
        if self.notification_queue is None:
            return

        job = self.db.get_job_by_id(message.job_id)
        if job is None:
            return

        try:
            enqueue_failed_job_notifications(
                job,
                self.db,
                self.notification_queue,
                error_message=error_message,
                logs=logs,
            )
        except Exception as e:
            print(f"Failed to enqueue job failure alert for `{message.job_id}`: {e}")

    def run_job(self, message: JobMessage):
        from docker import DockerClient
        from docker.client import from_env

        client: DockerClient = from_env()
        container = None

        try:
            container = client.containers.run(
                image=f"{message.payload.office}-jobs",
                command=f"python /jobs/{message.payload.repo_path}",
                detach=True,
                stderr=True,
                environment=[
                    f"OFFICE={message.payload.office}",
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
                self._send_failed_job_alert(
                    message,
                    error_message=f"Local job exited with status code {status_code}",
                    logs=logs,
                )

        except Exception as e:
            self.db.update_job_status(message.job_id, JobStatus.FAILED)
            logs = traceback.format_exc()
            try:
                self.logger.push_logs_for_job(message.job_id, logs)
            except Exception as log_error:
                print(f"Failed to persist logs for `{message.job_id}`: {log_error}")
            self._send_failed_job_alert(message, error_message=str(e), logs=logs)
            raise

        finally:
            if container:
                try:
                    container.remove()
                except Exception:
                    pass
