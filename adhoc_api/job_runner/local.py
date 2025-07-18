import docker
import os

from .base import JobRunner

CDA_HOST = os.getenv("CDA_HOST")


class LocalJobRunner(JobRunner):
    def run_job(self, office: str, script: str):
        client = docker.from_env()
        container = client.containers.run(
            image=f"{office}-jobs",
            command=f"python /jobs/python/{script}",
            remove=True,
            stderr=True,
            environment=[
                f"OFFICE={office}",
                "GITHUB_BRANCH=cwbi-dev",
                f"CDA_API_ROOT={CDA_HOST}/",
            ],
        )

        return container
