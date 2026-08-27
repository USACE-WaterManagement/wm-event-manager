ALTER TABLE
    scripts
ADD
    env_vars jsonb DEFAULT '{}'::jsonb NOT NULL,
ADD
    secret_env_names varchar ARRAY DEFAULT '{}'::varchar[] NOT NULL;

ALTER TABLE
    jobs
ADD
    env_vars jsonb DEFAULT '{}'::jsonb NOT NULL,
ADD
    secret_env_names varchar ARRAY DEFAULT '{}'::varchar[] NOT NULL;
