ALTER TABLE scripts
    ADD COLUMN command_args varchar ARRAY DEFAULT '{}'::varchar[] NOT NULL,
    ADD COLUMN timeout_minutes integer DEFAULT 30 NOT NULL;

ALTER TABLE jobs
    ADD COLUMN command_args varchar ARRAY DEFAULT '{}'::varchar[] NOT NULL,
    ADD COLUMN timeout_minutes integer DEFAULT 30 NOT NULL;

ALTER TABLE scripts
    ADD CONSTRAINT scripts_timeout_minutes_check CHECK (
        timeout_minutes BETWEEN 1 AND 1440
    );

ALTER TABLE jobs
    ADD CONSTRAINT jobs_timeout_minutes_check CHECK (
        timeout_minutes BETWEEN 1 AND 1440
    );
