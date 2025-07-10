from .base import JobRunner
import subprocess


class LocalJobRunner(JobRunner):
    def run_job(self, office: str, script: str):
        proc = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--env-file",
                ".env",
                f"{office}-jobs",
                "python",
                f"/jobs/python/{script}",
            ],
            capture_output=True,
        )
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
        }
