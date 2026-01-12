CREATE TABLE IF NOT EXISTS job_runners(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug varchar NOT NULL,
    label varchar NOT NULL,
    description varchar NOT NULL,
    active boolean NOT NULL,
    created_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
);