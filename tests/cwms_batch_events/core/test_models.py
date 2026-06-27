import pytest
from pydantic import ValidationError

from cwms_batch_events.core.models import ScriptCreate, ScriptRunOptions
from tests.factories import make_script_create_payload


@pytest.mark.parametrize(
    "env_vars",
    [
        {"AWS_BATCH_FOO": "bad"},
        {"aws_batch_foo": "bad"},
    ],
)
def test_script_run_options_reject_aws_batch_reserved_env_names(env_vars):
    with pytest.raises(ValidationError, match="cannot start with AWS_BATCH"):
        ScriptRunOptions(
            office="SWT",
            repo_path="python/report.py",
            script_slug="report",
            env_vars=env_vars,
        )


@pytest.mark.parametrize(
    "env_vars",
    [
        {"JOB_ID": "bad"},
        {"office": "bad"},
        {"BATCH_EVENTS_RUNTIME_TOKEN": "bad"},
        {"BATCH_JOB_CONTEXT_TOKEN": "bad"},
    ],
)
def test_script_run_options_reject_batch_events_reserved_env_names(env_vars):
    with pytest.raises(ValidationError, match="reserved for Batch Events runtime"):
        ScriptRunOptions(
            office="SWT",
            repo_path="python/report.py",
            script_slug="report",
            env_vars=env_vars,
        )


def test_script_run_options_reject_blank_command_args():
    with pytest.raises(ValidationError, match="commandArgs cannot contain empty strings"):
        ScriptRunOptions(
            office="SWT",
            repo_path="python/report.py",
            script_slug="report",
            command_args=["--project", ""],
        )


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        (
            {"runtime": "ruby"},
            "runtime must be one of: python, node, java, shell",
        ),
        (
            {"resource_profile": "huge"},
            "resourceProfile must be one of: small, medium, large",
        ),
        (
            {"timeout_minutes": 0},
            "timeoutMinutes must be between 1 and 1440",
        ),
        (
            {"timeout_minutes": 1441},
            "timeoutMinutes must be between 1 and 1440",
        ),
    ],
)
def test_script_run_options_reject_invalid_dispatch_values(
    payload,
    expected_message,
):
    with pytest.raises(ValidationError, match=expected_message):
        ScriptRunOptions(
            office="SWT",
            repo_path="run.py",
            script_slug="run",
            **payload,
        )


@pytest.mark.parametrize(
    "payload",
    [
        make_script_create_payload(envVars={"AWS_BATCH_FOO": "bad"}),
        make_script_create_payload(secretEnvNames=["AWS_BATCH_TOKEN"]),
        make_script_create_payload(envVars={"SCRIPT_PATH": "bad"}),
        make_script_create_payload(secretEnvNames=["BATCH_EVENTS_INTERNAL_TOKEN"]),
        make_script_create_payload(commandArgs=["--project", ""]),
    ],
)
def test_script_create_rejects_invalid_runtime_submit_values(payload):
    with pytest.raises(ValidationError):
        ScriptCreate.model_validate(payload)
