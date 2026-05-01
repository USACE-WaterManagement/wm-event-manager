from datetime import datetime, timezone
from unittest import mock
from uuid import uuid4

from cwms_batch_events.core.models import (
    NotificationGroupRead,
    NotificationTemplateRead,
    ScriptNotificationRuleDetails,
)
from cwms_batch_events.core.notifications import (
    enqueue_failed_job_notifications,
    render_notification,
)
from tests.factories import make_job_record


def make_rule(**overrides):
    now = datetime.now(timezone.utc)
    template = overrides.pop(
        "template",
        NotificationTemplateRead(
            id=uuid4(),
            office="SWT",
            slug="job_failure_v1",
            subjectTemplate="Job {{ scriptName }} failed",
            bodyTemplate="{{ jobId }}: {{ errorMessage }}",
            active=True,
            createdTime=now,
            updatedTime=now,
        ),
    )
    group = overrides.pop(
        "group",
        NotificationGroupRead(
            id=uuid4(),
            office="SWT",
            slug="data-admins",
            name="Data Admins",
            active=True,
            createdTime=now,
            updatedTime=now,
        ),
    )
    return ScriptNotificationRuleDetails(
        id=overrides.pop("id", uuid4()),
        scriptId=overrides.pop("script_id", uuid4()),
        eventType=overrides.pop("event_type", "job_failed"),
        templateId=template.id,
        groupId=group.id,
        active=overrides.pop("active", True),
        createdTime=now,
        updatedTime=now,
        template=template,
        group=group,
    )


def test_render_notification_uses_jinja_templates():
    rendered = render_notification(
        subject_template="Job {{ scriptName }} failed",
        body_template="{{ jobId }}: {{ errorMessage }}",
        recipients=["one@example.mil"],
        data={
            "scriptName": "Hourly",
            "jobId": "job-123",
            "errorMessage": "boom",
        },
    )

    assert rendered.subject == "Job Hourly failed"
    assert rendered.body == "job-123: boom"
    assert rendered.recipients == ["one@example.mil"]


def test_failed_job_with_no_rules_does_not_enqueue():
    db = mock.Mock()
    queue = mock.Mock()
    job = make_job_record()
    db.get_active_job_failed_notification_rules.return_value = []

    response = enqueue_failed_job_notifications(job, db, queue)

    assert response == []
    queue.send_notification.assert_not_called()


def test_failed_job_with_no_active_members_does_not_enqueue():
    db = mock.Mock()
    queue = mock.Mock()
    job = make_job_record()
    rule = make_rule(script_id=job.script_id)
    db.get_active_job_failed_notification_rules.return_value = [rule]
    db.get_active_notification_group_member_emails.return_value = []

    response = enqueue_failed_job_notifications(job, db, queue)

    assert response == []
    queue.send_notification.assert_not_called()


def test_failed_job_with_active_rule_enqueues_rendered_notification():
    db = mock.Mock()
    queue = mock.Mock()
    queue.send_notification.return_value = "message-123"
    job = make_job_record(script_name="Hourly")
    rule = make_rule(script_id=job.script_id)
    db.get_active_job_failed_notification_rules.return_value = [rule]
    db.get_active_notification_group_member_emails.return_value = [
        "one@example.mil"
    ]

    response = enqueue_failed_job_notifications(
        job,
        db,
        queue,
        error_message="boom",
        logs="traceback",
    )

    assert response == ["message-123"]
    message = queue.send_notification.call_args.args[0]
    assert message.template == "job_failure_v1"
    assert message.recipients == ["one@example.mil"]
    assert message.subject == "Job Hourly failed"
    assert message.body == f"{job.id}: boom"
    assert message.data["logs"] == "traceback"
