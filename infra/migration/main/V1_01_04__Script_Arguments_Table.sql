CREATE TABLE IF NOT EXISTS script_arguments(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id uuid NOT NULL,
    name varchar NOT NULL,
    label varchar NOT NULL,
    argument_type varchar NOT NULL CHECK (
        argument_type IN ('positional', 'flag')
    ),
    flag_name varchar,
    short_flag char(1),
    expects_value boolean NOT NULL DEFAULT TRUE,
    description varchar NOT NULL,
    required boolean NOT NULL DEFAULT false,
    constraint_type varchar NOT NULL DEFAULT 'none' CHECK (
        constraint_type IN ('none', 'fixed_values')
    ),
    position integer NOT NULL,
    CONSTRAINT flag_fields_valid CHECK (
        (
            argument_type = 'flag'
            AND flag_name IS NOT NULL
        )
        OR (
            argument_type = 'positional'
            AND flag_name IS NULL
            AND short_flag IS NULL
        )
    ),
    CONSTRAINT unique_script_argument_name UNIQUE (script_id, name),
    CONSTRAINT fk_script_arguments_scripts FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE
);