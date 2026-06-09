ALTER TABLE
    scripts
ADD
    runtime varchar DEFAULT 'python' NOT NULL,
ADD
    resource_profile varchar DEFAULT 'small' NOT NULL;

ALTER TABLE
    jobs
ADD
    runtime varchar DEFAULT 'python' NOT NULL,
ADD
    resource_profile varchar DEFAULT 'small' NOT NULL;

ALTER TABLE
    scripts
ADD
    CONSTRAINT scripts_runtime_check CHECK (runtime IN ('python', 'node', 'java'));

ALTER TABLE
    jobs
ADD
    CONSTRAINT jobs_runtime_check CHECK (runtime IN ('python', 'node', 'java'));

ALTER TABLE
    scripts
ADD
    CONSTRAINT scripts_resource_profile_check CHECK (
        resource_profile IN ('small', 'medium', 'large')
    );

ALTER TABLE
    jobs
ADD
    CONSTRAINT jobs_resource_profile_check CHECK (
        resource_profile IN ('small', 'medium', 'large')
    );
