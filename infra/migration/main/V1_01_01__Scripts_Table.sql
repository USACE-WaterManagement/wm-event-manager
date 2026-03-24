CREATE TABLE IF NOT EXISTS scripts(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    office varchar NOT NULL,
    name varchar NOT NULL,
    slug varchar NOT NULL,
    description varchar NOT NULL,
    repo_path varchar NOT NULL,
    execution_type varchar NOT NULL CHECK (execution_type IN ('python')),
    active boolean NOT NULL,
    roles varchar ARRAY,
    created_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT scripts_unique_office_slug UNIQUE(office, slug)
);