import logging
import os
from cwms_batch_events.core.models import JobMessage
from cwms_batch_events.core.runtime_auth import create_runtime_token
from cwms_batch_events.core.settings import settings
from cwms_batch_events.lambdas.dispatch_job.utils import OFFICES

import boto3
from datetime import datetime

logger = logging.getLogger(__name__)
API_BASE_URL = os.getenv("ALB_DNS_NAME")

RUNTIME_JOB_DEFINITIONS = {
    "python": "cwms-python-runner-jobdef",
    "node": "cwms-node-runner-jobdef",
    "java": "cwms-java-runner-jobdef",
    "shell": "cwms-shell-runner-jobdef",
}

RESOURCE_PROFILES = {
    "small": {"VCPU": "1", "MEMORY": "2048"},
    "medium": {"VCPU": "2", "MEMORY": "4096"},
    "large": {"VCPU": "4", "MEMORY": "8192"},
}

RUNTIME_COMMANDS = {
    "python": ["python"],
    "node": ["node"],
    "java": ["bash"],
    "shell": ["bash"],
}


class BatchJobRunner:
    def __init__(self):
        self.batch = boto3.client("batch")

    def run_job(self, message: JobMessage):
        office = message.payload.office.lower()
        repo_path = message.payload.repo_path
        script_slug = message.payload.script_slug
        runtime = message.payload.runtime.lower()
        resource_profile = message.payload.resource_profile.lower()
        command_args = message.payload.command_args
        if script_slug is None:
            script_slug = repo_path.split("/")[-1]

        job_definition = RUNTIME_JOB_DEFINITIONS[runtime]
        resources = RESOURCE_PROFILES[resource_profile]
        command = [*RUNTIME_COMMANDS[runtime], f"/jobs/{repo_path}", *command_args]

        job_name = (
            f"cwms-{office}-{runtime}-{script_slug}-{datetime.now().strftime('%Y%m%d-%H%M')}"
        ).replace(".", "_")

        environment = [
            {"name": "OFFICE", "value": office},
            {"name": "JOB_ID", "value": str(message.job_id)},
            {"name": "REPO_PATH", "value": repo_path},
            {"name": "SCRIPT_PATH", "value": repo_path},
            {"name": "SCRIPT_SLUG", "value": script_slug},
            {"name": "RUNTIME", "value": runtime},
        ]
        if API_BASE_URL:
            environment.append(
                {"name": "BATCH_EVENTS_API_ROOT", "value": f"{API_BASE_URL}/api"}
            )
        if settings.batch_events_internal_token:
            environment.append(
                {
                    "name": "BATCH_EVENTS_INTERNAL_TOKEN",
                    "value": settings.batch_events_internal_token,
                }
            )
        if settings.app_key:
            environment.append(
                {
                    "name": "BATCH_EVENTS_RUNTIME_TOKEN",
                    "value": create_runtime_token(message.job_id),
                }
            )
        environment.extend(
            {"name": name, "value": value}
            for name, value in message.payload.env_vars.items()
        )

        container_override = {
            "environment": environment,
            "command": command,
            "resourceRequirements": [
                {"type": kind, "value": value}
                for kind, value in resources.items()
            ],
        }

        response = self.batch.submit_job(
            jobName=job_name,
            jobQueue=f"cwms-{OFFICES[office]['division']}-jq",
            jobDefinition=job_definition,
            ecsPropertiesOverride={
                "taskProperties": [
                    {
                        "containers": [
                            container_override,
                        ],
                    },
                ],
            },
            timeout={
                "attemptDurationSeconds": message.payload.timeout_minutes * 60,
            },
            tags={
                "Office": office,
                "Runtime": runtime,
                "ResourceProfile": resource_profile,
                "JobId": str(message.job_id),
            },
        )

        batch_job_id: str = response["jobId"]

        logger.info(
            "Succesfully submitted %s to Batch with external job id %s",
            job_name,
            batch_job_id,
        )

        return batch_job_id
