from .base import JobRunner
import docker


class LocalJobRunner(JobRunner):
    def run_job(self, office: str, script: str):
        client = docker.from_env()
        container = client.containers.run(
            image=f"{office}-jobs",
            command=f"python /jobs/python/{script}",
            remove=True,
            stderr=True,
            environment=[
                "OFFICE=lrh",
                "GITHUB_BRANCH=cwbi-dev",
                "CDA_API_ROOT=https://water.dev.cwbi.us/cwms-data/",
            ],
        )

        return container
