from typing import Protocol


class JobRunner(Protocol):
    def run_job(self, office: str, script: str, job_id: str):
        pass
