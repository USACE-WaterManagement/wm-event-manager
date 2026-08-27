ALTER TABLE scripts
    DROP CONSTRAINT scripts_schedule_type_check,
    ADD COLUMN schedule_cron varchar,
    ADD CONSTRAINT scripts_schedule_type_check CHECK (schedule_type IN ('manual', 'hourly', 'cron')),
    ADD CONSTRAINT scripts_schedule_cron_check CHECK (
        schedule_cron IS NULL OR array_length(regexp_split_to_array(trim(schedule_cron), '[[:space:]]+'), 1) = 5
    );

ALTER TABLE jobs
    DROP CONSTRAINT jobs_schedule_type_check,
    ADD COLUMN schedule_cron varchar,
    ADD CONSTRAINT jobs_schedule_type_check CHECK (schedule_type IN ('manual', 'hourly', 'cron')),
    ADD CONSTRAINT jobs_schedule_cron_check CHECK (
        schedule_cron IS NULL OR array_length(regexp_split_to_array(trim(schedule_cron), '[[:space:]]+'), 1) = 5
    );
