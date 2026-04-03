CREATE TABLE IF NOT EXISTS scripts_job_runners(
    script_id uuid NOT NULL,
    job_runner_id uuid NOT NULL,
    PRIMARY KEY (script_id, job_runner_id),
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE,
    FOREIGN KEY (job_runner_id) REFERENCES job_runners(id) ON DELETE CASCADE
);