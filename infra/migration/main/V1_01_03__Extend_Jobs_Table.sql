ALTER TABLE
    jobs
ADD
    script_id uuid,
ADD
    script_slug varchar,
ADD
    repo_path varchar,
ADD
    execution_type varchar CHECK (execution_type IN ('python')) DEFAULT 'python' NOT NULL,
ADD
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE
SET
    NULL;

UPDATE
    jobs
SET
    repo_path = CONCAT('python/', script_name)
WHERE
    repo_path IS NULL;

ALTER TABLE
    jobs
ALTER COLUMN
    repo_path
SET
    NOT NULL;