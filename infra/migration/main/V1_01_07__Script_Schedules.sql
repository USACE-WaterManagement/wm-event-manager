ALTER TABLE scripts
    ADD COLUMN schedule_enabled boolean DEFAULT false NOT NULL,
    ADD COLUMN schedule_type varchar DEFAULT 'manual' NOT NULL,
    ADD COLUMN schedule_minute integer;

ALTER TABLE jobs
    ADD COLUMN schedule_enabled boolean DEFAULT false NOT NULL,
    ADD COLUMN schedule_type varchar DEFAULT 'manual' NOT NULL,
    ADD COLUMN schedule_minute integer;

ALTER TABLE scripts
    ADD CONSTRAINT scripts_schedule_type_check CHECK (schedule_type IN ('manual', 'hourly')),
    ADD CONSTRAINT scripts_schedule_minute_check CHECK (
        schedule_minute IS NULL OR schedule_minute BETWEEN 0 AND 59
    );

ALTER TABLE jobs
    ADD CONSTRAINT jobs_schedule_type_check CHECK (schedule_type IN ('manual', 'hourly')),
    ADD CONSTRAINT jobs_schedule_minute_check CHECK (
        schedule_minute IS NULL OR schedule_minute BETWEEN 0 AND 59
    );
