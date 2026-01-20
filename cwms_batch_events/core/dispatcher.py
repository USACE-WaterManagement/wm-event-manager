from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.job_logger.base import JobLogger
from cwms_batch_events.core.job_runner.local import LocalJobRunner
from cwms_batch_events.core.models import JobMessage


class MissingJobRunner(Exception):
    pass


class JobDispatcher:
    def __init__(self, db: JobDatabase, logger: JobLogger):
        self.db = db
        self.logger = logger

    def dispatch_job(self, message: JobMessage):
        runner = None
        if message.runner_type == "docker-local":
            runner = LocalJobRunner(self.db, self.logger)
        if not runner:
            raise MissingJobRunner(
                f"JobRunner for runner_type {message.runner_type} not found"
            )
        runner.run_job(message)
