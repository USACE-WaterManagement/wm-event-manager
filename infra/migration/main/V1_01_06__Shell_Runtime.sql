ALTER TABLE scripts DROP CONSTRAINT scripts_runtime_check;
ALTER TABLE jobs DROP CONSTRAINT jobs_runtime_check;

ALTER TABLE
    scripts
ADD
    CONSTRAINT scripts_runtime_check CHECK (runtime IN ('python', 'node', 'java', 'shell'));

ALTER TABLE
    jobs
ADD
    CONSTRAINT jobs_runtime_check CHECK (runtime IN ('python', 'node', 'java', 'shell'));
