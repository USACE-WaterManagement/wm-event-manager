ALTER TABLE scripts
    ADD COLUMN schedule_timezone varchar DEFAULT 'UTC' NOT NULL,
    ADD CONSTRAINT scripts_schedule_timezone_check CHECK (
        btrim(schedule_timezone) <> ''
    );

ALTER TABLE jobs
    ADD COLUMN schedule_timezone varchar DEFAULT 'UTC' NOT NULL,
    ADD CONSTRAINT jobs_schedule_timezone_check CHECK (
        btrim(schedule_timezone) <> ''
    );
