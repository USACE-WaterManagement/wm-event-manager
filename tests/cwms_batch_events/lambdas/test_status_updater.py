import json
from unittest import mock

import pytest
import requests
from botocore.exceptions import ClientError

from cwms_batch_events.lambdas.update_batch_job_status.status_updater import (
    get_internal_token,
    lambda_handler,
)


def test_get_internal_token_reads_and_caches_secret():
    with mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater._cached_internal_token",
        None,
    ), mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.APP_SECRETS_ARN",
        "arn",
    ), mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.secrets_client"
    ) as secrets_client:
        secrets_client.get_secret_value.return_value = {
            "SecretString": json.dumps({"APP_KEY": "secret"})
        }

        first = get_internal_token()
        second = get_internal_token()

    assert first == "secret"
    assert second == "secret"
    secrets_client.get_secret_value.assert_called_once_with(SecretId="arn")


def test_get_internal_token_re_raises_client_error():
    error = ClientError({"Error": {"Code": "Oops", "Message": "bad"}}, "GetSecretValue")

    with mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater._cached_internal_token",
        None,
    ), mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.secrets_client"
    ) as secrets_client:
        secrets_client.get_secret_value.side_effect = error

        with pytest.raises(ClientError):
            get_internal_token()


def test_lambda_handler_ignores_unsupported_status():
    with mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.requests.post"
    ) as requests_post:
        lambda_handler(
            {
                "detail": {
                    "jobName": "cwms-swt-event-script",
                    "jobId": "batch-123",
                    "status": "STARTING",
                },
                "time": "2026-04-16T12:00:00Z",
            },
            None,
        )

    requests_post.assert_not_called()


def test_lambda_handler_posts_translated_status_to_events_api():
    response = mock.Mock(status_code=204, text="")

    with mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.get_internal_token",
        return_value="secret",
    ), mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.requests.post",
        return_value=response,
    ) as requests_post, mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.API_BASE_URL",
        "http://events/api",
    ):
        lambda_handler(
            {
                "detail": {
                    "jobName": "cwms-swt-event-script",
                    "jobId": "batch-123",
                    "status": "SUCCEEDED",
                },
                "time": "2026-04-16T12:00:00Z",
            },
            None,
        )

    requests_post.assert_called_once()
    assert requests_post.call_args.kwargs["json"] == {
        "status": "Completed",
        "event_time": "2026-04-16T12:00:00Z",
    }


def test_lambda_handler_posts_status_for_shared_runner_job_names():
    response = mock.Mock(status_code=204, text="")

    with mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.get_internal_token",
        return_value="secret",
    ), mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.requests.post",
        return_value=response,
    ) as requests_post, mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.API_BASE_URL",
        "http://events/api",
    ):
        lambda_handler(
            {
                "detail": {
                    "jobName": "cwms-swt-python-hourly-20260626-1715",
                    "jobId": "batch-456",
                    "status": "RUNNING",
                },
                "time": "2026-06-26T17:15:00Z",
            },
            None,
        )

    requests_post.assert_called_once()
    assert requests_post.call_args.args[0] == (
        "http://events/api/internal/batch-jobs/batch-456/status"
    )
    assert requests_post.call_args.kwargs["json"] == {
        "status": "Running",
        "event_time": "2026-06-26T17:15:00Z",
    }


def test_lambda_handler_re_raises_request_exceptions():
    with mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.get_internal_token",
        return_value="secret",
    ), mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.requests.post",
        side_effect=requests.RequestException("boom"),
    ):
        with pytest.raises(requests.RequestException):
            lambda_handler(
                {
                    "detail": {
                        "jobName": "cwms-swt-event-script",
                        "jobId": "batch-123",
                        "status": "RUNNING",
                    },
                    "time": "2026-04-16T12:00:00Z",
                },
                None,
            )


def test_lambda_handler_ignores_unknown_batch_jobs():
    response = mock.Mock(status_code=404, text="not found")

    with mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.get_internal_token",
        return_value="secret",
    ), mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.requests.post",
        return_value=response,
    ) as requests_post:
        lambda_handler(
            {
                "detail": {
                    "jobName": "cwms-swt-python-smoke-20260626-1715",
                    "jobId": "batch-untracked",
                    "status": "RUNNING",
                },
                "time": "2026-06-26T17:15:00Z",
            },
            None,
        )

    requests_post.assert_called_once()


def test_lambda_handler_raises_when_events_api_rejects_message():
    response = mock.Mock(status_code=500, text="bad")

    with mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.get_internal_token",
        return_value="secret",
    ), mock.patch(
        "cwms_batch_events.lambdas.update_batch_job_status.status_updater.requests.post",
        return_value=response,
    ):
        with pytest.raises(RuntimeError, match="Events API rejected message"):
            lambda_handler(
                {
                    "detail": {
                        "jobName": "cwms-swt-event-script",
                        "jobId": "batch-123",
                        "status": "RUNNING",
                    },
                    "time": "2026-04-16T12:00:00Z",
                },
                None,
            )
