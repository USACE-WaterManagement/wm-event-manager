from datetime import datetime
from unittest import mock

from cwms_batch_events.lambdas.dispatch_job.job_runner.batch import BatchJobRunner
from cwms_batch_events.core.models import ScriptRunOptions
from tests.factories import make_job_message


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
        containerOverrides={
            "environment": [
                {"name": "OFFICE", "value": "swt"},
                {"name": "JOB_ID", "value": str(message.job_id)},
                {"name": "REPO_PATH", "value": "run.py"},
                    {"name": "SCRIPT_PATH", "value": "run.py"},
                    {"name": "SCRIPT_SLUG", "value": "script"},
                    {"name": "RUNTIME", "value": "python"},
                    {"name": "BATCH_EVENTS_API_ROOT", "value": "http://events/api"},
                ],
            "resourceRequirements": [
                {"type": "VCPU", "value": "1"},
                {"type": "MEMORY", "value": "2048"},
            ],
        },
        tags={
            "Office": "swt",
            "Runtime": "python",
            "ResourceProfile": "small",
            "JobId": str(message.job_id),
        },
    )


def test_batch_job_runner_uses_repo_path_name_when_slug_missing():
    batch_client = mock.Mock()
    batch_client.submit_job.return_value = {"jobId": "ext-123"}
    fixed_now = datetime(2026, 4, 16, 12, 30)
    message = make_job_message(
        payload=make_job_message().payload.model_copy(update={"script_slug": None, "repo_path": "folder/my.script.py"})
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

    environment = batch_client.submit_job.call_args.kwargs["containerOverrides"][
        "environment"
    ]
    assert {"name": "BATCH_EVENTS_API_ROOT", "value": "http://internal-alb/api"} in environment
    assert {"name": "CDA_API_ROOT", "value": "https://cda"} in environment
