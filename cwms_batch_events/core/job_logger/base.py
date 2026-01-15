from typing import Protocol
from uuid import UUID


class JobLogger(Protocol):
    def get_logs_for_job(self, job_id: UUID) -> str: ...
    def push_logs_for_job(self, job_id: UUID, logs: str) -> None: ...
