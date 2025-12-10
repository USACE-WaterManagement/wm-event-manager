-- pgFormatter-ignore
-- ignore the formatter to not format the flyway placeholders

-- Always re-apply roles  when running migrations: ${flyway:timestamp}

-- *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
-- create the user, reader, and writer roles
-- *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
DO $$
BEGIN
  CREATE USER ${APP_USER} WITH ENCRYPTED PASSWORD '${APP_PASSWORD}';
  EXCEPTION WHEN DUPLICATE_OBJECT THEN
  RAISE NOTICE 'not creating role ${APP_USER} -- it already exists';
END
$$;

-- reader role
DO $$
BEGIN
  CREATE ROLE events_reader;
  EXCEPTION WHEN DUPLICATE_OBJECT THEN
  RAISE NOTICE 'not creating role events_reader -- it already exists';
END
$$;

-- writer role
DO $$
BEGIN
  CREATE ROLE events_writer;
  EXCEPTION WHEN DUPLICATE_OBJECT THEN
  RAISE NOTICE 'not creating role events_writer -- it already exists';
END
$$;

-- grant privileges
GRANT SELECT ON ALL TABLES IN SCHEMA ${flyway:defaultSchema} TO events_reader;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ${flyway:defaultSchema} TO events_writer;

REVOKE ALL ON flyway_schema_history FROM events_reader;
REVOKE ALL ON flyway_schema_history FROM events_writer;

GRANT events_reader, events_writer TO ${APP_USER};

GRANT USAGE ON SCHEMA ${flyway:defaultSchema} TO ${APP_USER};

ALTER ROLE ${APP_USER} SET search_path = public, ${flyway:defaultSchema};