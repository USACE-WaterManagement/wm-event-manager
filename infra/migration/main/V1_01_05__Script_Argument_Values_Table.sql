CREATE TABLE IF NOT EXISTS script_argument_values(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    script_argument_id uuid NOT NULL,
    value varchar NOT NULL,
    CONSTRAINT unique_script_argument_value UNIQUE (script_argument_id, value),
    CONSTRAINT fk_script_argument_values_script_arguments FOREIGN KEY (script_argument_id) REFERENCES script_arguments(id) ON DELETE CASCADE
);