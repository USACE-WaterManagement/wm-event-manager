from datetime import datetime
from pathlib import Path
from unittest import mock

import botocore.session
import pytest

from cwms_batch_events.lambdas.dispatch_job.job_runner.batch import BatchJobRunner
from cwms_batch_events.core.models import ScriptRunOptions
from cwms_batch_events.core.runtime_auth import validate_runtime_token
from cwms_batch_events.core.settings import settings
from tests.factories import make_job_message


@pytest.fixture(autouse=True)
def reset_app_key(monkeypatch):
    monkeypatch.setattr(settings, "app_key", "")


def container_override(submit_kwargs):
    return submit_kwargs["ecsPropertiesOverride"]["taskProperties"][0]["containers"][0]


def test_batch_job_runner_submits_expected_batch_job():
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    fixed_now = datetime(2026, 4, 16, 12, 30)
    message = make_job_message()

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ), mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        runner = BatchJobRunner()
        job_id = runner.run_job(message)

    assert job_id == "ext-123"
    batch_client.submit_job.assert_called_once_with(
        jobName="cwms-swt-python-script-20260416-1230",
        jobQueue="cwms-swd-jq",
        jobDefinition="cwms-python-runner-jobdef",
        ecsPropertiesOverride={
            "taskProperties": [
                {
                    "containers": [
                        {
                            "environment": [
                                {"name": "OFFICE", "value": "swt"},
                                {"name": "JOB_ID", "value": str(message.job_id)},
                                {"name": "REPO_PATH", "value": "run.py"},
                                {"name": "SCRIPT_PATH", "value": "run.py"},
                                {"name": "SCRIPT_SLUG", "value": "script"},
                                {"name": "RUNTIME", "value": "python"},
                                {"name": "EXECUTION_TYPE", "value": "github_file"},
                                {
                                    "name": "BATCH_EVENTS_API_ROOT",
                                    "value": "http://events/api",
                                },
                            ],
                            "command": ["python", "/jobs/run.py"],
                            "resourceRequirements": [
                                {"type": "VCPU", "value": "1"},
                                {"type": "MEMORY", "value": "2048"},
                            ],
                        },
                    ],
                },
            ],
        },
        timeout={"attemptDurationSeconds": 1800},
        tags={
            "Office": "swt",
            "OfficeGroup": "swd",
            "Runtime": "python",
            "ResourceProfile": "small",
            "JobId": str(message.job_id),
            "ScriptSlug": "script",
        },
    )


def test_batch_job_runner_uses_repo_path_name_when_slug_missing():
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    fixed_now = datetime(2026, 4, 16, 12, 30)
    message = make_job_message(
        payload=make_job_message().payload.model_copy(
            update={"script_slug": None, "repo_path": "folder/my.script.py"}
        )
    )

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ), mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        runner = BatchJobRunner()
        runner.run_job(message)

    assert batch_client.submit_job.call_args.kwargs["jobName"] == (
        "cwms-swt-python-my_script_py-20260416-1230"
    )


def test_batch_job_runner_passes_broker_url_and_public_env_vars():
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    message = make_job_message(
        payload=ScriptRunOptions(
            office="swt",
            repo_path="run.py",
            script_slug="script",
            env_vars={"CDA_API_ROOT": "https://cda"},
        )
    )

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ), mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.API_BASE_URL",
        "http://internal-alb",
    ):
        runner = BatchJobRunner()
        runner.run_job(message)

    environment = container_override(batch_client.submit_job.call_args.kwargs)[
        "environment"
    ]
    assert {
        "name": "BATCH_EVENTS_API_ROOT",
        "value": "http://internal-alb/api",
    } in environment
    assert {"name": "CDA_API_ROOT", "value": "https://cda"} in environment


def test_batch_job_runner_passes_runtime_broker_token_when_app_key_is_configured(
    monkeypatch,
):
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    message = make_job_message()
    monkeypatch.setattr(settings, "app_key", "runtime-secret")

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ):
        runner = BatchJobRunner()
        runner.run_job(message)

    environment = container_override(batch_client.submit_job.call_args.kwargs)[
        "environment"
    ]
    token = next(
        item["value"]
        for item in environment
        if item["name"] == "BATCH_EVENTS_RUNTIME_TOKEN"
    )
    assert validate_runtime_token(token, message.job_id) == (True, None)


def test_batch_job_runner_passes_command_args_and_timeout():
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    message = make_job_message(
        payload=ScriptRunOptions(
            office="swt",
            repo_path="python/report.py",
            script_slug="report",
            command_args=["--project", "KEYS"],
            timeout_minutes=45,
        )
    )

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ):
        runner = BatchJobRunner()
        runner.run_job(message)

    submit_kwargs = batch_client.submit_job.call_args.kwargs
    assert container_override(submit_kwargs)["command"] == [
        "python",
        "/jobs/python/report.py",
        "--project",
        "KEYS",
    ]
    assert submit_kwargs["timeout"] == {"attemptDurationSeconds": 2700}


def test_batch_job_runner_supports_command_execution_type():
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    message = make_job_message(
        payload=ScriptRunOptions(
            office="swt",
            repo_path="cwms-cli users list | grep Test",
            script_slug="users-list",
            execution_type="command",
            runtime="shell",
            command_args=["&&", "ls", "-l"],
        )
    )

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ):
        runner = BatchJobRunner()
        runner.run_job(message)

    submit_kwargs = batch_client.submit_job.call_args.kwargs
    assert container_override(submit_kwargs)["command"] == [
        "bash",
        "-lc",
        "cwms-cli users list | grep Test && ls -l",
    ]
    assert {"name": "EXECUTION_TYPE", "value": "command"} in container_override(
        submit_kwargs
    )["environment"]


def test_batch_job_runner_supports_shell_runtime():
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    message = make_job_message(
        payload=ScriptRunOptions(
            office="swt",
            repo_path="bin/hourly.sh",
            script_slug="hourly",
            runtime="shell",
        )
    )

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ):
        runner = BatchJobRunner()
        runner.run_job(message)

    submit_kwargs = batch_client.submit_job.call_args.kwargs
    assert submit_kwargs["jobDefinition"] == "cwms-shell-runner-jobdef"
    assert submit_kwargs["tags"]["Runtime"] == "shell"
    assert {"name": "RUNTIME", "value": "shell"} in container_override(submit_kwargs)[
        "environment"
    ]


def test_batch_job_runner_routes_and_tags_jobs_by_office_group():
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    message = make_job_message(
        payload=ScriptRunOptions(
            office="lrl",
            repo_path="bin/hourly.sh",
            script_slug="hourly",
            runtime="shell",
            resource_profile="medium",
        )
    )

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ):
        runner = BatchJobRunner()
        runner.run_job(message)

    submit_kwargs = batch_client.submit_job.call_args.kwargs
    assert submit_kwargs["jobQueue"] == "cwms-lrd-jq"
    assert submit_kwargs["tags"]["Office"] == "lrl"
    assert submit_kwargs["tags"]["OfficeGroup"] == "lrd"
    assert submit_kwargs["tags"]["ScriptSlug"] == "hourly"


@pytest.mark.parametrize(
    ("runtime", "repo_path", "expected_command", "expected_job_definition"),
    [
        ("node", "node/report.js", ["node", "/jobs/node/report.js"], "cwms-node-runner-jobdef"),
        ("java", "java/Report.java", ["java", "/jobs/java/Report.java"], "cwms-java-runner-jobdef"),
    ],
)
def test_batch_job_runner_uses_runtime_command_defaults(
    runtime,
    repo_path,
    expected_command,
    expected_job_definition,
):
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    message = make_job_message(
        payload=ScriptRunOptions(
            office="swt",
            repo_path=repo_path,
            script_slug="report",
            runtime=runtime,
        )
    )

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ):
        runner = BatchJobRunner()
        runner.run_job(message)

    submit_kwargs = batch_client.submit_job.call_args.kwargs
    assert submit_kwargs["jobDefinition"] == expected_job_definition
    assert container_override(submit_kwargs)["command"] == expected_command


def test_batch_job_runner_uses_configured_runtime_and_resource_overrides(monkeypatch):
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    message = make_job_message(
        payload=ScriptRunOptions(
            office="swt",
            repo_path="python/report.py",
            script_slug="report",
            runtime="python",
            resource_profile="large",
        )
    )
    monkeypatch.setattr(
        settings,
        "batch_runtime_job_definitions",
        {"python": "dev-cwms-python-runner-jobdef"},
    )
    monkeypatch.setattr(
        settings,
        "batch_resource_profiles",
        {"large": {"VCPU": "8", "MEMORY": "16384"}},
    )
    monkeypatch.setattr(
        settings,
        "batch_runtime_commands",
        {"python": ["uv", "run", "python"]},
    )

    with mock.patch(
        "cwms_batch_events.lambdas.dispatch_job.job_runner.batch.boto3.client",
        return_value=batch_client,
    ):
        runner = BatchJobRunner()
        runner.run_job(message)

    submit_kwargs = batch_client.submit_job.call_args.kwargs
    assert submit_kwargs["jobDefinition"] == "dev-cwms-python-runner-jobdef"
    assert container_override(submit_kwargs)["command"] == [
        "uv",
        "run",
        "python",
        "/jobs/python/report.py",
    ]
    assert container_override(submit_kwargs)["resourceRequirements"] == [
        {"type": "VCPU", "value": "8"},
        {"type": "MEMORY", "value": "16384"},
    ]


def test_dispatcher_lambda_pins_batch_submit_model_support():
    requirements = Path(
        "cwms_batch_events/lambdas/dispatch_job/requirements.txt"
    ).read_text(encoding="utf-8")
    submit_shape = (
        botocore.session.get_session()
        .get_service_model("batch")
        .operation_model("SubmitJob")
        .input_shape
    )

    assert "boto3>=" in requirements
    assert "botocore>=" in requirements
    assert "ecsPropertiesOverride" in submit_shape.members


def test_batch_job_runner_reports_unsupported_runtime():
    with pytest.raises(ValueError, match="runtime must be one of"):
        ScriptRunOptions(
            office="swt",
            repo_path="ruby/report.rb",
            script_slug="report",
            runtime="ruby",
        )
