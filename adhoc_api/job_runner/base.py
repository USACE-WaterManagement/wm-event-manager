from abc import ABC, abstractmethod


class JobRunner(ABC):
    @abstractmethod
    def run_job(self, office: str, script: str):
        pass
