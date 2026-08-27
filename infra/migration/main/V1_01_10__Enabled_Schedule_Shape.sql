ALTER TABLE scripts
    ADD CONSTRAINT scripts_enabled_schedule_shape_check CHECK (
        NOT schedule_enabled
        OR (
            schedule_type = 'hourly'
            AND schedule_minute IS NOT NULL
        )
        OR (
            schedule_type = 'cron'
            AND schedule_cron IS NOT NULL
            AND btrim(schedule_cron) <> ''
        )
    );

ALTER TABLE jobs
    ADD CONSTRAINT jobs_enabled_schedule_shape_check CHECK (
        NOT schedule_enabled
        OR (
            schedule_type = 'hourly'
            AND schedule_minute IS NOT NULL
        )
        OR (
            schedule_type = 'cron'
            AND schedule_cron IS NOT NULL
            AND btrim(schedule_cron) <> ''
        )
    );
