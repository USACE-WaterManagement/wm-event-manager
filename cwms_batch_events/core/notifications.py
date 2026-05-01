from datetime import datetime, timezone

from jinja2 import Template

from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.models import (
    JobRecord,
    NotificationMessage,
    NotificationSeverity,
    RenderedNotification,
)
from cwms_batch_events.core.notification_queue import (
    MESSAGE_VERSION,
    NotificationQueue,
)


def build_job_failure_data(
    job: JobRecord,
    *,
    error_message: str | None = None,
    logs: str | None = None,
) -> dict[str, str | None]:
    return {
        "jobId": str(job.id),
        "scriptId": str(job.script_id) if job.script_id else None,
        "scriptName": job.script_name,
        "scriptSlug": job.script_slug,
        "repoPath": job.repo_path,
        "executionType": job.execution_type,
        "username": job.username,
        "office": job.office,
        "externalJobId": job.external_job_id,
        "errorMessage": error_message,
        "logs": logs,
    }


def render_notification(
    *,
    subject_template: str,
    body_template: str,
    recipients: list[str],
    data: dict[str, str | None],
) -> RenderedNotification:
    return RenderedNotification(
        recipients=recipients,
        subject=Template(subject_template).render(**data),
        body=Template(body_template).render(**data),
        data=data,
    )


def enqueue_failed_job_notifications(
    job: JobRecord,
    db: JobDatabase,
    queue: NotificationQueue | None,
    *,
    error_message: str | None = None,
    logs: str | None = None,
) -> list[str]:
    if queue is None or job.script_id is None:
        return []

    messages: list[str] = []
    rules = db.get_active_job_failed_notification_rules(job.script_id)
    data = build_job_failure_data(job, error_message=error_message, logs=logs)

    for rule in rules:
        recipients = db.get_active_notification_group_member_emails(rule.group_id)
        if not recipients:
            continue

        rendered = render_notification(
            subject_template=rule.template.subject_template,
            body_template=rule.template.body_template,
            recipients=recipients,
            data=data,
        )
        message = NotificationMessage(
            version=MESSAGE_VERSION,
            template=rule.template.slug,
            office=rule.template.office,
            severity=NotificationSeverity.HIGH,
            recipients=rendered.recipients,
            subject=rendered.subject,
            body=rendered.body,
            created_at=datetime.now(timezone.utc),
            data=rendered.data,
        )
        messages.append(queue.send_notification(message))

    return messages
