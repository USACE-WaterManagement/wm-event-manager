from types import SimpleNamespace

from cwms_batch_events.core.models import NotificationMessage, NotificationSeverity
from cwms_batch_events.core.notification_queue import MESSAGE_VERSION, NotificationQueue


def test_send_notification_returns_message_id():
    queue = NotificationQueue.__new__(NotificationQueue)
    queue.queue = SimpleNamespace(
        send_message=lambda MessageBody: {"MessageId": "notification-123"}
    )
    message = NotificationMessage(
        version=MESSAGE_VERSION,
        template="job_failure_v1",
        office="SWT",
        severity=NotificationSeverity.HIGH,
        recipients=["alerts@example.mil"],
        subject="Job failed",
        body="Something broke",
        created_at="2026-04-16T12:00:00Z",
        data={"jobId": "job-123"},
    )

    response = queue.send_notification(message)

    assert response == "notification-123"
