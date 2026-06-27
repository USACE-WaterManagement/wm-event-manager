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

DEFAULT_RUNTIME_JOB_DEFINITIONS = {
    "python": "cwms-python-runner-jobdef",
    "node": "cwms-node-runner-jobdef",
    "java": "cwms-java-runner-jobdef",
    "shell": "cwms-shell-runner-jobdef",
}

DEFAULT_RESOURCE_PROFILES = {
    "small": {"VCPU": "1", "MEMORY": "2048"},
    "medium": {"VCPU": "2", "MEMORY": "4096"},
    "large": {"VCPU": "4", "MEMORY": "8192"},
}

DEFAULT_RUNTIME_COMMANDS = {
    "python": ["python"],
    "node": ["node"],
    "java": ["java"],
    "shell": ["bash"],
}

DEFAULT_COMMAND_RUNTIME_COMMANDS = {
    "python": ["bash", "-lc"],
    "node": ["bash", "-lc"],
    "java": ["bash", "-lc"],
    "shell": ["bash", "-lc"],
}


def configured_map(defaults, overrides):
    return {**defaults, **overrides}


def configured_value(kind, values, key):
    try:
        return values[key]
    except KeyError as exc:
        supported = ", ".join(sorted(values))
        raise ValueError(
            f"Unsupported {kind} '{key}'. Supported values: {supported}"
        ) from exc


def command_for_payload(message: JobMessage, runtime_commands: dict[str, list[str]]) -> list[str]:
    payload = message.payload
    runtime = payload.runtime.lower()
    execution_type = (payload.execution_type or "github_file").lower()

    if execution_type == "command":
        command = " ".join([payload.repo_path, *payload.command_args]).strip()
        return [
            *configured_value("runtime command", DEFAULT_COMMAND_RUNTIME_COMMANDS, runtime),
            command,
        ]

    return [
        *configured_value("runtime command", runtime_commands, runtime),
        f"/jobs/{payload.repo_path}",
        *payload.command_args,
    ]


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

        runtime_job_definitions = configured_map(
            DEFAULT_RUNTIME_JOB_DEFINITIONS, settings.batch_runtime_job_definitions
        )
        resource_profiles = configured_map(
            DEFAULT_RESOURCE_PROFILES, settings.batch_resource_profiles
        )
        runtime_commands = configured_map(
            DEFAULT_RUNTIME_COMMANDS, settings.batch_runtime_commands
        )

        job_definition = configured_value("runtime", runtime_job_definitions, runtime)
        resources = configured_value(
            "resource profile", resource_profiles, resource_profile
        )
        command = command_for_payload(message, runtime_commands)

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
            {"name": "EXECUTION_TYPE", "value": message.payload.execution_type or "github_file"},
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
                {"type": kind, "value": value} for kind, value in resources.items()
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
                "OfficeGroup": OFFICES[office]["division"],
                "Runtime": runtime,
                "ResourceProfile": resource_profile,
                "JobId": str(message.job_id),
                "ScriptSlug": script_slug,
            },
        )

        batch_job_id: str = response["jobId"]

        logger.info(
            "Succesfully submitted %s to Batch with external job id %s",
            job_name,
            batch_job_id,
        )

        return batch_job_id
