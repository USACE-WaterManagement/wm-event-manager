from datetime import datetime, timezone
import re
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import uuid

from cwms_batch_events.core.auth.user.models import User
from cwms_batch_events.core.job_database.postgres.models import (
    JobModel,
    JobRunnerModel,
    NotificationGroupMemberModel,
    NotificationGroupModel,
    NotificationTemplateModel,
    ScriptModel,
    ScriptNotificationRuleModel,
)
from cwms_batch_events.core.models import (
    JobRecord,
    JobStatus,
    NotificationEventType,
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
from cwms_batch_events.core.utils import get_runner_id


class SlugError(Exception):
    pass


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    value = re.sub(r"^-+|-+$", "", value)
    return value


class PostgresJobDatabase:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_admin_office(self, office: str, admin_offices: list[str]) -> None:
        if office not in admin_offices:
            raise PermissionError(
                f"User does not have script admin access for office '{office}'"
            )

    def _load_group_for_admin(
        self, group_id: uuid.UUID, admin_offices: list[str]
    ) -> NotificationGroupModel:
        group = self.db.get_one(NotificationGroupModel, group_id)
        if group.office is not None:
            self._ensure_admin_office(group.office, admin_offices)
        return group

    def _load_script_for_admin(
        self, script_id: uuid.UUID, admin_offices: list[str]
    ) -> ScriptModel:
        script = self.db.get_one(ScriptModel, script_id)
        self._ensure_admin_office(script.office, admin_offices)
        return script

    def _raise_slug_error(self, slug: str, office: str) -> None:
        raise SlugError(f"Slug '{slug}' already in use for office '{office}'")

    def bind_external_job_id(
        self,
        job_id: uuid.UUID,
        external_job_id: str,
    ) -> None:
        job = self._load_job_for_update(job_id)

        if job.external_job_id is None:
            job.external_job_id = external_job_id
            self.db.commit()
            return

        if job.external_job_id == external_job_id:
            return

        raise ValueError(
            f"Job {job_id} already bound to {job.external_job_id}, "
            f"cannot bind to {external_job_id}"
        )

    def create_job(self, payload: ScriptRunRequest, user: User) -> JobRecord:
        script = self.db.get_one(ScriptModel, payload.script_id)

        if set(script.roles).isdisjoint(user.roles[script.office]):
            raise PermissionError("Not authorized to run requested script")

        job = JobModel()
        job.id = uuid.uuid4()
        job.script_id = script.id
        job.script_name = script.name
        job.script_slug = script.slug
        job.job_status = JobStatus.PENDING
        job.username = user.username
        job.office = script.office
        job.repo_path = script.repo_path
        job.execution_type = script.execution_type
        job.job_runner_id = get_runner_id()

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return JobRecord.model_validate(job)

    def get_job_by_id(self, job_id: uuid.UUID) -> JobRecord | None:
        job_model = self.db.get(JobModel, job_id)
        if job_model is None:
            return None
        return JobRecord.model_validate(job_model)

    def get_job_by_external_id(self, ext_job_id: str) -> JobRecord | None:
        job_model = self.db.scalars(
            select(JobModel).where(JobModel.external_job_id == ext_job_id)
        ).one_or_none()
        if job_model is None:
            return None
        return JobRecord.model_validate(job_model)

    def get_jobs_for_user(self, user_id: str) -> list[JobRecord]:
        job_models = self.db.scalars(
            select(JobModel)
            .where(JobModel.username == user_id)
            .order_by(JobModel.created_time.desc())
        ).all()
        return [JobRecord.model_validate(model) for model in job_models]

    def get_scripts_for_office(self, office: str):
        script_models = self.db.scalars(
            select(ScriptModel).where(ScriptModel.office == office)
        ).all()
        return [
            ScriptRead.model_validate(script_model) for script_model in script_models
        ]

    def _load_job_for_update(self, job_id: uuid.UUID):
        job = (
            self.db.query(JobModel)
            .filter(JobModel.id == job_id)
            .with_for_update()
            .one_or_none()
        )

        if not job:
            raise ValueError(f"Job {job_id} does not exist")

        return job

    def remove_script_if_allowed(
        self, script_id: uuid.UUID, admin_offices: list[str]
    ) -> None:
        with self.db.begin():
            script = self.db.get_one(ScriptModel, script_id)
            self._ensure_admin_office(script.office, admin_offices)
            self.db.delete(script)

    def retrieve_script_catalog(self, roles: dict[str, list[str]]) -> list[ScriptRead]:
        """Current method may become inefficient if all_scripts becomes huge. At that
        point, consider storing user roles (temporarily?) in database to perform
        filtering operation entirely within SQL."""
        all_scripts = self.db.scalars(select(ScriptModel)).all()
        runnable_scripts = [
            script
            for script in all_scripts
            if script.office in roles
            and script.active
            and not set(script.roles).isdisjoint(roles[script.office])
        ]

        return [ScriptRead.model_validate(script) for script in runnable_scripts]

    def store_script(self, payload: ScriptCreate) -> ScriptRead:
        try:
            with self.db.begin():
                script = ScriptModel()
                script.office = payload.office
                script.name = payload.name
                script.slug = slugify(payload.name)
                script.description = payload.description
                script.repo_path = payload.repo_path
                script.execution_type = payload.execution_type
                script.active = payload.active
                script.roles = payload.roles

                job_runners = self.db.scalars(
                    select(JobRunnerModel).where(
                        JobRunnerModel.id.in_(payload.job_runners)
                    )
                ).all()
                if len(job_runners) != len(payload.job_runners):
                    raise ValueError("Invalid job runner ID provided")
                script.job_runners = list(job_runners)

                self.db.add(script)
                self.db.flush()
                self.db.refresh(script)

            return ScriptRead.model_validate(script)

        except IntegrityError as e:
            self.db.rollback()

            if "slug" not in str(e).lower():
                raise

            self._raise_slug_error(slugify(payload.name), payload.office)

    def update_job_status(self, job_id: uuid.UUID, status: JobStatus) -> None:
        job = self._load_job_for_update(job_id)

        now = datetime.now(timezone.utc)

        job.job_status = status
        if status == JobStatus.RUNNING:
            job.run_time = now
        elif status in (JobStatus.COMPLETED, JobStatus.FAILED):
            job.end_time = now
        self.db.commit()

    def update_script(
        self, script_id: uuid.UUID, payload: ScriptUpdate, admin_offices: list[str]
    ) -> ScriptRead:
        with self.db.begin():
            script = self.db.get_one(ScriptModel, script_id)
            self._ensure_admin_office(script.office, admin_offices)
            for field, value in payload.model_dump(by_alias=False).items():
                if field == "job_runners":
                    job_runners = self.db.scalars(
                        select(JobRunnerModel).where(
                            JobRunnerModel.id.in_(payload.job_runners)
                        )
                    ).all()
                    if len(job_runners) != len(payload.job_runners):
                        raise ValueError("Invalid job runner ID provided")
                    script.job_runners = list(job_runners)
                else:
                    setattr(script, field, value)

            script.updated_time = datetime.now()
            self.db.flush()
            self.db.refresh(script)

        return ScriptRead.model_validate(script)

    def get_active_job_failed_notification_rules(
        self, script_id: uuid.UUID
    ) -> list[ScriptNotificationRuleDetails]:
        rules = self.db.scalars(
            select(ScriptNotificationRuleModel)
            .join(ScriptNotificationRuleModel.template)
            .where(
                ScriptNotificationRuleModel.script_id == script_id,
                ScriptNotificationRuleModel.event_type == NotificationEventType.JOB_FAILED,
                ScriptNotificationRuleModel.active.is_(True),
                NotificationTemplateModel.active.is_(True),
            )
        ).all()
        return [ScriptNotificationRuleDetails.model_validate(rule) for rule in rules]

    def get_active_notification_group_member_emails(
        self, group_id: uuid.UUID
    ) -> list[str]:
        members = self.db.scalars(
            select(NotificationGroupMemberModel)
            .where(
                NotificationGroupMemberModel.group_id == group_id,
                NotificationGroupMemberModel.active.is_(True),
            )
            .order_by(NotificationGroupMemberModel.email)
        ).all()
        return [member.email for member in members]

    def get_notification_templates_for_office(
        self, office: str | None = None
    ) -> list[NotificationTemplateRead]:
        templates = self.db.scalars(
            select(NotificationTemplateModel)
            .where(
                (NotificationTemplateModel.office == office)
                | (NotificationTemplateModel.office.is_(None))
                if office is not None
                else NotificationTemplateModel.office.is_(None)
            )
            .order_by(NotificationTemplateModel.slug)
        ).all()
        return [NotificationTemplateRead.model_validate(model) for model in templates]

    def store_notification_template(
        self, payload: NotificationTemplateCreate
    ) -> NotificationTemplateRead:
        try:
            with self.db.begin():
                template = NotificationTemplateModel(**payload.model_dump(by_alias=False))
                self.db.add(template)
                self.db.flush()
                self.db.refresh(template)
            return NotificationTemplateRead.model_validate(template)
        except IntegrityError:
            self.db.rollback()
            self._raise_slug_error(payload.slug, payload.office)

    def update_notification_template(
        self,
        template_id: uuid.UUID,
        payload: NotificationTemplateUpdate,
        admin_offices: list[str],
    ) -> NotificationTemplateRead:
        try:
            with self.db.begin():
                template = self.db.get_one(NotificationTemplateModel, template_id)
                if template.office is not None:
                    self._ensure_admin_office(template.office, admin_offices)
                if payload.office is not None:
                    self._ensure_admin_office(payload.office, admin_offices)
                for field, value in payload.model_dump(by_alias=False).items():
                    setattr(template, field, value)
                template.updated_time = datetime.now(timezone.utc)
                self.db.flush()
                self.db.refresh(template)
            return NotificationTemplateRead.model_validate(template)
        except IntegrityError:
            self.db.rollback()
            self._raise_slug_error(payload.slug, payload.office)

    def remove_notification_template_if_allowed(
        self, template_id: uuid.UUID, admin_offices: list[str]
    ) -> None:
        with self.db.begin():
            template = self.db.get_one(NotificationTemplateModel, template_id)
            if template.office is not None:
                self._ensure_admin_office(template.office, admin_offices)
            self.db.delete(template)

    def get_notification_template_if_allowed(
        self, template_id: uuid.UUID, admin_offices: list[str]
    ) -> NotificationTemplateRead:
        template = self.db.get_one(NotificationTemplateModel, template_id)
        if template.office is not None:
            self._ensure_admin_office(template.office, admin_offices)
        return NotificationTemplateRead.model_validate(template)

    def get_notification_groups_for_office(self, office: str | None = None) -> list[NotificationGroupRead]:
        groups = self.db.scalars(
            select(NotificationGroupModel)
            .where(
                (NotificationGroupModel.office == office)
                | (NotificationGroupModel.office.is_(None))
                if office is not None
                else NotificationGroupModel.office.is_(None)
            )
            .order_by(NotificationGroupModel.slug)
        ).all()
        return [NotificationGroupRead.model_validate(model) for model in groups]

    def store_notification_group(
        self, payload: NotificationGroupCreate
    ) -> NotificationGroupRead:
        try:
            with self.db.begin():
                group = NotificationGroupModel(**payload.model_dump(by_alias=False))
                self.db.add(group)
                self.db.flush()
                self.db.refresh(group)
            return NotificationGroupRead.model_validate(group)
        except IntegrityError:
            self.db.rollback()
            self._raise_slug_error(payload.slug, payload.office)

    def update_notification_group(
        self,
        group_id: uuid.UUID,
        payload: NotificationGroupUpdate,
        admin_offices: list[str],
    ) -> NotificationGroupRead:
        try:
            with self.db.begin():
                group = self.db.get_one(NotificationGroupModel, group_id)
                if group.office is not None:
                    self._ensure_admin_office(group.office, admin_offices)
                if payload.office is not None:
                    self._ensure_admin_office(payload.office, admin_offices)
                for field, value in payload.model_dump(by_alias=False).items():
                    setattr(group, field, value)
                group.updated_time = datetime.now(timezone.utc)
                self.db.flush()
                self.db.refresh(group)
            return NotificationGroupRead.model_validate(group)
        except IntegrityError:
            self.db.rollback()
            self._raise_slug_error(payload.slug, payload.office)

    def remove_notification_group_if_allowed(
        self, group_id: uuid.UUID, admin_offices: list[str]
    ) -> None:
        with self.db.begin():
            group = self._load_group_for_admin(group_id, admin_offices)
            self.db.delete(group)

    def get_notification_group_members(
        self, group_id: uuid.UUID, admin_offices: list[str]
    ) -> list[NotificationGroupMemberRead]:
        self._load_group_for_admin(group_id, admin_offices)
        members = self.db.scalars(
            select(NotificationGroupMemberModel)
            .where(NotificationGroupMemberModel.group_id == group_id)
            .order_by(NotificationGroupMemberModel.email)
        ).all()
        return [NotificationGroupMemberRead.model_validate(model) for model in members]

    def store_notification_group_member(
        self,
        group_id: uuid.UUID,
        payload: NotificationGroupMemberCreate,
        admin_offices: list[str],
    ) -> NotificationGroupMemberRead:
        try:
            with self.db.begin():
                self._load_group_for_admin(group_id, admin_offices)
                member = NotificationGroupMemberModel(
                    group_id=group_id,
                    **payload.model_dump(by_alias=False),
                )
                self.db.add(member)
                self.db.flush()
                self.db.refresh(member)
            return NotificationGroupMemberRead.model_validate(member)
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Email '{payload.email}' already exists in group")

    def update_notification_group_member(
        self,
        member_id: uuid.UUID,
        payload: NotificationGroupMemberUpdate,
        admin_offices: list[str],
    ) -> NotificationGroupMemberRead:
        try:
            with self.db.begin():
                member = self.db.get_one(NotificationGroupMemberModel, member_id)
                if member.group.office is not None:
                    self._ensure_admin_office(member.group.office, admin_offices)
                for field, value in payload.model_dump(by_alias=False).items():
                    setattr(member, field, value)
                member.updated_time = datetime.now(timezone.utc)
                self.db.flush()
                self.db.refresh(member)
            return NotificationGroupMemberRead.model_validate(member)
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Email '{payload.email}' already exists in group")

    def remove_notification_group_member_if_allowed(
        self, member_id: uuid.UUID, admin_offices: list[str]
    ) -> None:
        with self.db.begin():
            member = self.db.get_one(NotificationGroupMemberModel, member_id)
            if member.group.office is not None:
                self._ensure_admin_office(member.group.office, admin_offices)
            self.db.delete(member)

    def get_script_notification_rules(
        self, script_id: uuid.UUID, admin_offices: list[str]
    ) -> list[ScriptNotificationRuleRead]:
        self._load_script_for_admin(script_id, admin_offices)
        rules = self.db.scalars(
            select(ScriptNotificationRuleModel)
            .where(ScriptNotificationRuleModel.script_id == script_id)
            .order_by(ScriptNotificationRuleModel.created_time)
        ).all()
        return [ScriptNotificationRuleRead.model_validate(rule) for rule in rules]

    def store_script_notification_rule(
        self, payload: ScriptNotificationRuleCreate, admin_offices: list[str]
    ) -> ScriptNotificationRuleRead:
        try:
            with self.db.begin():
                self._validate_rule_payload(payload, admin_offices)
                if payload.active:
                    self._deactivate_active_script_notification_rules(
                        payload.script_id, payload.event_type
                    )
                rule = ScriptNotificationRuleModel(**payload.model_dump(by_alias=False))
                self.db.add(rule)
                self.db.flush()
                self.db.refresh(rule)
            return ScriptNotificationRuleRead.model_validate(rule)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Notification rule already exists")

    def update_script_notification_rule(
        self,
        rule_id: uuid.UUID,
        payload: ScriptNotificationRuleUpdate,
        admin_offices: list[str],
    ) -> ScriptNotificationRuleRead:
        try:
            with self.db.begin():
                self._validate_rule_payload(payload, admin_offices)
                rule = self.db.get_one(ScriptNotificationRuleModel, rule_id)
                self._ensure_admin_office(rule.script.office, admin_offices)
                if payload.active:
                    self._deactivate_active_script_notification_rules(
                        payload.script_id, payload.event_type, exclude_rule_id=rule_id
                    )
                for field, value in payload.model_dump(by_alias=False).items():
                    setattr(rule, field, value)
                rule.updated_time = datetime.now(timezone.utc)
                self.db.flush()
                self.db.refresh(rule)
            return ScriptNotificationRuleRead.model_validate(rule)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Notification rule already exists")

    def remove_script_notification_rule_if_allowed(
        self, rule_id: uuid.UUID, admin_offices: list[str]
    ) -> None:
        with self.db.begin():
            rule = self.db.get_one(ScriptNotificationRuleModel, rule_id)
            self._ensure_admin_office(rule.script.office, admin_offices)
            self.db.delete(rule)

    def _validate_rule_payload(
        self,
        payload: ScriptNotificationRuleCreate | ScriptNotificationRuleUpdate,
        admin_offices: list[str],
    ) -> None:
        script = self._load_script_for_admin(payload.script_id, admin_offices)
        template = self.db.get_one(NotificationTemplateModel, payload.template_id)
        if payload.event_type != NotificationEventType.JOB_FAILED:
            raise ValueError("Only job_failed notification rules are supported")
        if template.office is not None and template.office != script.office:
            raise ValueError("Notification template office must match script office")
        if not payload.cda_user_list_id and not payload.manual_recipients:
            raise ValueError(
                "A CDA user list or at least one manual recipient is required"
            )

    def _deactivate_active_script_notification_rules(
        self,
        script_id: uuid.UUID,
        event_type: NotificationEventType,
        exclude_rule_id: uuid.UUID | None = None,
    ) -> None:
        statement = select(ScriptNotificationRuleModel).where(
            ScriptNotificationRuleModel.script_id == script_id,
            ScriptNotificationRuleModel.event_type == event_type,
            ScriptNotificationRuleModel.active.is_(True),
        )
        if exclude_rule_id is not None:
            statement = statement.where(ScriptNotificationRuleModel.id != exclude_rule_id)
        for rule in self.db.scalars(statement).all():
            rule.active = False
            rule.updated_time = datetime.now(timezone.utc)
