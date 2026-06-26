INSERT INTO scripts (
    id,
    office,
    name,
    slug,
    description,
    repo_path,
    execution_type,
    runtime,
    resource_profile,
    env_vars,
    secret_env_names,
    active,
    roles
)
VALUES (
    'bbbbbbbb-2222-4222-8222-bbbbbbbbbbbb',
    'SWT',
    'SWT hourly jobs',
    'swt-hourly-jobs',
    'Local production-shaped SWT hourly job entrypoint',
    'bin/hourly.sh',
    'python',
    'shell',
    'small',
    '{
        "CDA_TOKEN_URL": "http://host.docker.internal:8081/auth/realms/cwms/protocol/openid-connect/token",
        "CDA_TOKEN_HOST_HEADER": "localhost:8081"
    }'::jsonb,
    ARRAY['CDA_CLIENT_ID', 'CDA_CLIENT_SECRET']::varchar[],
    true,
    ARRAY['CWMS Users']::varchar[]
)
ON CONFLICT (office, slug)
DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    repo_path = EXCLUDED.repo_path,
    execution_type = EXCLUDED.execution_type,
    runtime = EXCLUDED.runtime,
    resource_profile = EXCLUDED.resource_profile,
    env_vars = EXCLUDED.env_vars,
    secret_env_names = EXCLUDED.secret_env_names,
    active = EXCLUDED.active,
    roles = EXCLUDED.roles,
    updated_time = CURRENT_TIMESTAMP;

INSERT INTO scripts_job_runners (script_id, job_runner_id)
SELECT
    id,
    '13f391ef-7597-4b4b-a0ef-0926c09d4649'::uuid
FROM
    scripts
WHERE
    office = 'SWT'
    AND slug = 'swt-hourly-jobs'
ON CONFLICT DO NOTHING;
