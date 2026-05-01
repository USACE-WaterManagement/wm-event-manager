from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.exc import NoResultFound

from cwms_batch_events.core.models import (
    NotificationGroupMemberRead,
    NotificationGroupRead,
    NotificationTemplateRead,
    ScriptNotificationRuleRead,
)
from tests.factories import make_job_record


def make_template(**overrides):
    now = datetime.now(timezone.utc)
    return NotificationTemplateRead(
        id=overrides.pop("id", uuid4()),
        office=overrides.pop("office", "SWT"),
        slug=overrides.pop("slug", "job_failure_v1"),
        subjectTemplate=overrides.pop("subject_template", "Job {{ scriptName }} failed"),
        bodyTemplate=overrides.pop("body_template", "{{ jobId }}"),
        active=overrides.pop("active", True),
        createdTime=overrides.pop("created_time", now),
        updatedTime=overrides.pop("updated_time", now),
    )


def make_group(**overrides):
    now = datetime.now(timezone.utc)
    return NotificationGroupRead(
        id=overrides.pop("id", uuid4()),
        office=overrides.pop("office", "SWT"),
        slug=overrides.pop("slug", "data-admins"),
        name=overrides.pop("name", "Data Admins"),
        active=overrides.pop("active", True),
        createdTime=overrides.pop("created_time", now),
        updatedTime=overrides.pop("updated_time", now),
    )


def make_member(**overrides):
    now = datetime.now(timezone.utc)
    return NotificationGroupMemberRead(
        id=overrides.pop("id", uuid4()),
        groupId=overrides.pop("group_id", uuid4()),
        email=overrides.pop("email", "one@example.mil"),
        active=overrides.pop("active", True),
        createdTime=overrides.pop("created_time", now),
        updatedTime=overrides.pop("updated_time", now),
    )


def make_rule(**overrides):
    now = datetime.now(timezone.utc)
    return ScriptNotificationRuleRead(
        id=overrides.pop("id", uuid4()),
        scriptId=overrides.pop("script_id", uuid4()),
        eventType=overrides.pop("event_type", "job_failed"),
        templateId=overrides.pop("template_id", uuid4()),
        groupId=overrides.pop("group_id", uuid4()),
        active=overrides.pop("active", True),
        createdTime=overrides.pop("created_time", now),
        updatedTime=overrides.pop("updated_time", now),
    )


def template_payload(**overrides):
    return {
        "office": overrides.pop("office", "SWT"),
        "slug": overrides.pop("slug", "job_failure_v1"),
        "subjectTemplate": overrides.pop(
            "subjectTemplate", "Job {{ scriptName }} failed"
        ),
        "bodyTemplate": overrides.pop("bodyTemplate", "{{ jobId }}"),
        "active": overrides.pop("active", True),
        **overrides,
    }


def group_payload(**overrides):
    return {
        "office": overrides.pop("office", "SWT"),
        "slug": overrides.pop("slug", "data-admins"),
        "name": overrides.pop("name", "Data Admins"),
        "active": overrides.pop("active", True),
        **overrides,
    }


def test_get_templates_requires_admin_access(client):
    response = client.get("/notifications/templates", params={"office": "LRH"})

    assert response.status_code == 401


def test_create_and_list_templates(client, job_db):
    template = make_template()
    job_db.store_notification_template.return_value = template
    job_db.get_notification_templates_for_office.return_value = [template]

    create_response = client.post(
        "/notifications/templates", json=template_payload()
    )
    list_response = client.get(
        "/notifications/templates", params={"office": "SWT"}
    )

    assert create_response.status_code == 200
    assert create_response.json()["id"] == str(template.id)
    assert list_response.status_code == 200
    assert list_response.json()[0]["slug"] == "job_failure_v1"


def test_update_and_delete_template(client, job_db):
    template = make_template()
    job_db.update_notification_template.return_value = template

    put_response = client.put(
        f"/notifications/templates/{template.id}", json=template_payload()
    )
    delete_response = client.delete(f"/notifications/templates/{template.id}")

    assert put_response.status_code == 200
    assert delete_response.status_code == 204
    job_db.remove_notification_template_if_allowed.assert_called_once()


def test_notification_template_missing_maps_to_404(client, job_db):
    job_db.update_notification_template.side_effect = NoResultFound()

    response = client.put(
        f"/notifications/templates/{uuid4()}", json=template_payload()
    )

    assert response.status_code == 404


def test_create_and_manage_group_members(client, job_db):
    group = make_group()
    member = make_member(group_id=group.id)
    job_db.store_notification_group.return_value = group
    job_db.get_notification_groups_for_office.return_value = [group]
    job_db.store_notification_group_member.return_value = member
    job_db.get_notification_group_members.return_value = [member]
    job_db.update_notification_group_member.return_value = member

    group_response = client.post("/notifications/groups", json=group_payload())
    groups_response = client.get("/notifications/groups", params={"office": "SWT"})
    member_response = client.post(
        f"/notifications/groups/{group.id}/members",
        json={"email": "one@example.mil", "active": True},
    )
    members_response = client.get(f"/notifications/groups/{group.id}/members")
    update_response = client.put(
        f"/notifications/groups/members/{member.id}",
        json={"email": "one@example.mil", "active": False},
    )
    delete_response = client.delete(f"/notifications/groups/members/{member.id}")

    assert group_response.status_code == 200
    assert groups_response.json()[0]["id"] == str(group.id)
    assert member_response.status_code == 200
    assert members_response.json()[0]["email"] == "one@example.mil"
    assert update_response.status_code == 200
    assert delete_response.status_code == 204


def test_create_and_manage_rules(client, job_db):
    rule = make_rule()
    job_db.store_script_notification_rule.return_value = rule
    job_db.get_script_notification_rules.return_value = [rule]
    job_db.update_script_notification_rule.return_value = rule

    payload = {
        "scriptId": str(rule.script_id),
        "eventType": "job_failed",
        "templateId": str(rule.template_id),
        "groupId": str(rule.group_id),
        "active": True,
    }
    create_response = client.post("/notifications/rules", json=payload)
    list_response = client.get(
        "/notifications/rules", params={"script_id": str(rule.script_id)}
    )
    update_response = client.put(f"/notifications/rules/{rule.id}", json=payload)
    delete_response = client.delete(f"/notifications/rules/{rule.id}")

    assert create_response.status_code == 200
    assert list_response.json()[0]["id"] == str(rule.id)
    assert update_response.status_code == 200
    assert delete_response.status_code == 204


def test_preview_template_renders_job_data(client, job_db):
    template = make_template()
    job = make_job_record(script_name="Hourly")
    job_db.get_notification_template_if_allowed.return_value = template
    job_db.get_job_by_id.return_value = job

    response = client.post(
        f"/notifications/templates/{template.id}/preview",
        json={
            "jobId": str(job.id),
            "data": {"errorMessage": "boom"},
        },
    )

    assert response.status_code == 200
    assert response.json()["subject"] == "Job Hourly failed"
    assert response.json()["body"] == str(job.id)
