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
    "payload",
    [
        make_script_create_payload(envVars={"AWS_BATCH_FOO": "bad"}),
        make_script_create_payload(secretEnvNames=["AWS_BATCH_TOKEN"]),
    ],
)
def test_script_create_rejects_aws_batch_reserved_env_names(payload):
    with pytest.raises(ValidationError, match="cannot start with AWS_BATCH"):
        ScriptCreate.model_validate(payload)
