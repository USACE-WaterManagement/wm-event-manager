from typing import Protocol
from uuid import UUID


class JobRunner(Protocol):
    def run_job(self, office: str, script: str, job_id: UUID):
        pass
