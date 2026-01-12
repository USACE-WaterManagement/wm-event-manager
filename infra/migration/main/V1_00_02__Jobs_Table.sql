CREATE TABLE IF NOT EXISTS jobs(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    script_name varchar NOT NULL,
    job_status varchar NOT NULL,
    username varchar NOT NULL,
    office varchar NOT NULL,
    created_time timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    run_time timestamptz,
    end_time timestamptz,
    external_job_id varchar,
    job_runner_id uuid NOT NULL,
    CONSTRAINT fk_jobs_job_runners FOREIGN KEY (job_runner_id) REFERENCES job_runners(id)
);