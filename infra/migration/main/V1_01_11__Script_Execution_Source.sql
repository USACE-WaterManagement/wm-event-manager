ALTER TABLE scripts
    DROP CONSTRAINT scripts_execution_type_check,
    ADD CONSTRAINT scripts_execution_type_check CHECK (
        execution_type IN ('python', 'github_file', 'command')
    );

ALTER TABLE jobs
    DROP CONSTRAINT jobs_execution_type_check,
    ADD CONSTRAINT jobs_execution_type_check CHECK (
        execution_type IS NULL
        OR execution_type IN ('python', 'github_file', 'command')
    );
