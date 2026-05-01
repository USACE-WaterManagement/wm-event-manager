from typing import Protocol
from uuid import UUID

from cwms_batch_events.core.auth.user.models import User
from cwms_batch_events.core.models import (
    JobRecord,
    JobStatus,
    NotificationGroupCreate,
    NotificationGroupMemberCreate,
    NotificationGroupMemberRead,
    NotificationGroupMemberUpdate,
    NotificationGroupRead,
    NotificationGroupUpdate,
    NotificationTemplateCreate,
    NotificationTemplateRead,
    NotificationTemplateUpdate,
    ScriptCreate,
    ScriptNotificationRuleCreate,
    ScriptNotificationRuleDetails,
    ScriptNotificationRuleRead,
    ScriptNotificationRuleUpdate,
    ScriptRead,
    ScriptRunRequest,
    ScriptUpdate,
)


class JobDatabase(Protocol):
    def bind_external_job_id(
        self,
        job_id: UUID,
        external_job_id: str,
    ) -> None: ...
    def create_job(self, payload: ScriptRunRequest, user: User) -> JobRecord: ...
    def get_job_by_external_id(self, ext_job_id: str) -> JobRecord | None: ...
    def get_job_by_id(self, job_id: UUID) -> JobRecord | None: ...
    def get_jobs_for_user(self, user_id: str) -> list[JobRecord]: ...
    def get_scripts_for_office(self, office: str) -> list[ScriptRead]: ...
    def remove_script_if_allowed(
        self, script_id: UUID, admin_offices: list[str]
    ) -> None: ...
    def retrieve_script_catalog(
        self, roles: dict[str, list[str]]
    ) -> list[ScriptRead]: ...
    def store_script(self, payload: ScriptCreate) -> ScriptRead: ...
    def update_job_status(self, job_id: UUID, status: JobStatus) -> None: ...
    def update_script(
        self, script_id: UUID, payload: ScriptUpdate, admin_offices: list[str]
    ) -> ScriptRead: ...
    def get_active_job_failed_notification_rules(
        self, script_id: UUID
    ) -> list[ScriptNotificationRuleDetails]: ...
    def get_active_notification_group_member_emails(
        self, group_id: UUID
    ) -> list[str]: ...
    def get_notification_templates_for_office(
        self, office: str
    ) -> list[NotificationTemplateRead]: ...
    def store_notification_template(
        self, payload: NotificationTemplateCreate
    ) -> NotificationTemplateRead: ...
    def update_notification_template(
        self,
        template_id: UUID,
        payload: NotificationTemplateUpdate,
        admin_offices: list[str],
    ) -> NotificationTemplateRead: ...
    def remove_notification_template_if_allowed(
        self, template_id: UUID, admin_offices: list[str]
    ) -> None: ...
    def get_notification_template_if_allowed(
        self, template_id: UUID, admin_offices: list[str]
    ) -> NotificationTemplateRead: ...
    def get_notification_groups_for_office(
        self, office: str
    ) -> list[NotificationGroupRead]: ...
    def store_notification_group(
        self, payload: NotificationGroupCreate
    ) -> NotificationGroupRead: ...
    def update_notification_group(
        self,
        group_id: UUID,
        payload: NotificationGroupUpdate,
        admin_offices: list[str],
    ) -> NotificationGroupRead: ...
    def remove_notification_group_if_allowed(
        self, group_id: UUID, admin_offices: list[str]
    ) -> None: ...
    def get_notification_group_members(
        self, group_id: UUID, admin_offices: list[str]
    ) -> list[NotificationGroupMemberRead]: ...
    def store_notification_group_member(
        self,
        group_id: UUID,
        payload: NotificationGroupMemberCreate,
        admin_offices: list[str],
    ) -> NotificationGroupMemberRead: ...
    def update_notification_group_member(
        self,
        member_id: UUID,
        payload: NotificationGroupMemberUpdate,
        admin_offices: list[str],
    ) -> NotificationGroupMemberRead: ...
    def remove_notification_group_member_if_allowed(
        self, member_id: UUID, admin_offices: list[str]
    ) -> None: ...
    def get_script_notification_rules(
        self, script_id: UUID, admin_offices: list[str]
    ) -> list[ScriptNotificationRuleRead]: ...
    def store_script_notification_rule(
        self, payload: ScriptNotificationRuleCreate, admin_offices: list[str]
    ) -> ScriptNotificationRuleRead: ...
    def update_script_notification_rule(
        self,
        rule_id: UUID,
        payload: ScriptNotificationRuleUpdate,
        admin_offices: list[str],
    ) -> ScriptNotificationRuleRead: ...
    def remove_script_notification_rule_if_allowed(
        self, rule_id: UUID, admin_offices: list[str]
    ) -> None: ...
