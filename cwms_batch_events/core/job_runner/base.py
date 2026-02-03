from typing import Protocol

from cwms_batch_events.core.models import JobMessage


class JobRunner(Protocol):
    def run_job(self, message: JobMessage) -> str: ...
