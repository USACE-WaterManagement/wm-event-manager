CREATE TABLE IF NOT EXISTS notification_templates(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    office varchar NOT NULL,
    slug varchar NOT NULL,
    subject_template varchar NOT NULL,
    body_template varchar NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT notification_templates_office_slug UNIQUE(office, slug)
);

CREATE TABLE IF NOT EXISTS notification_groups(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    office varchar NOT NULL,
    slug varchar NOT NULL,
    name varchar NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT notification_groups_office_slug UNIQUE(office, slug)
);

CREATE TABLE IF NOT EXISTS notification_group_members(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id uuid NOT NULL,
    email varchar NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT notification_group_members_group_email UNIQUE(group_id, email),
    CONSTRAINT fk_notification_group_members_group FOREIGN KEY (group_id) REFERENCES notification_groups(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS script_notification_rules(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id uuid NOT NULL,
    event_type varchar NOT NULL CHECK (event_type = 'job_failed'),
    template_id uuid NOT NULL,
    group_id uuid NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT script_notification_rules_unique_rule UNIQUE(script_id, event_type, template_id, group_id),
    CONSTRAINT fk_script_notification_rules_script FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE,
    CONSTRAINT fk_script_notification_rules_template FOREIGN KEY (template_id) REFERENCES notification_templates(id) ON DELETE CASCADE,
    CONSTRAINT fk_script_notification_rules_group FOREIGN KEY (group_id) REFERENCES notification_groups(id) ON DELETE CASCADE
);
