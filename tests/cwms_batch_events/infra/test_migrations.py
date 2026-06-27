from pathlib import Path


def read_migration(name: str) -> str:
    return Path(f"infra/migration/main/{name}").read_text(encoding="utf-8")


def test_enabled_schedule_shape_is_enforced_in_database_migration():
    migration = read_migration("V1_01_10__Enabled_Schedule_Shape.sql")

    assert "scripts_enabled_schedule_shape_check" in migration
    assert "jobs_enabled_schedule_shape_check" in migration
    assert "NOT schedule_enabled" in migration
    assert "schedule_type = 'hourly'" in migration
    assert "schedule_minute IS NOT NULL" in migration
    assert "schedule_type = 'cron'" in migration
    assert "schedule_cron IS NOT NULL" in migration
    assert "btrim(schedule_cron) <> ''" in migration


def test_execution_source_modes_are_allowed_in_database_migration():
    migration = read_migration("V1_01_11__Script_Execution_Source.sql")

    assert "scripts_execution_type_check" in migration
    assert "jobs_execution_type_check" in migration
    assert "'github_file'" in migration
    assert "'command'" in migration
    assert "'python'" in migration


def test_schedule_timezone_is_created_by_database_migration():
    migration = read_migration("V1_01_12__Script_Schedule_Timezone.sql")

    assert "ALTER TABLE scripts" in migration
    assert "ALTER TABLE jobs" in migration
    assert "schedule_timezone varchar DEFAULT 'UTC' NOT NULL" in migration
    assert "scripts_schedule_timezone_check" in migration
    assert "jobs_schedule_timezone_check" in migration
    assert "btrim(schedule_timezone) <> ''" in migration


def test_script_registry_fields_are_created_by_database_migrations():
    runtime_profiles = read_migration("V1_01_04__Runtime_Profiles.sql")
    runtime_env = read_migration("V1_01_05__Script_Runtime_Environment.sql")
    shell_runtime = read_migration("V1_01_06__Shell_Runtime.sql")
    schedules = read_migration("V1_01_07__Script_Schedules.sql")
    command_timeout = read_migration("V1_01_08__Script_Commands_Timeouts.sql")
    cron_schedules = read_migration("V1_01_09__Script_Cron_Schedules.sql")

    for table in ("scripts", "jobs"):
        assert f"ALTER TABLE\n    {table}" in runtime_profiles
        assert "runtime varchar DEFAULT 'python' NOT NULL" in runtime_profiles
        assert "resource_profile varchar DEFAULT 'small' NOT NULL" in runtime_profiles
        assert f"{table}_resource_profile_check" in runtime_profiles
        assert "resource_profile IN ('small', 'medium', 'large')" in runtime_profiles

        assert f"ALTER TABLE\n    {table}" in runtime_env
        assert "env_vars jsonb DEFAULT '{}'::jsonb NOT NULL" in runtime_env
        assert "secret_env_names varchar ARRAY DEFAULT '{}'::varchar[] NOT NULL" in runtime_env

        assert f"ALTER TABLE {table}" in schedules
        assert "schedule_enabled boolean DEFAULT false NOT NULL" in schedules
        assert "schedule_type varchar DEFAULT 'manual' NOT NULL" in schedules
        assert "ADD COLUMN schedule_minute integer" in schedules
        assert f"{table}_schedule_minute_check" in schedules
        assert "schedule_minute IS NULL OR schedule_minute BETWEEN 0 AND 59" in schedules

        assert f"ALTER TABLE {table}" in command_timeout
        assert "command_args varchar ARRAY DEFAULT '{}'::varchar[] NOT NULL" in command_timeout
        assert "timeout_minutes integer DEFAULT 30 NOT NULL" in command_timeout
        assert f"{table}_timeout_minutes_check" in command_timeout
        assert "timeout_minutes BETWEEN 1 AND 1440" in command_timeout

        assert f"ALTER TABLE {table}" in cron_schedules
        assert "ADD COLUMN schedule_cron varchar" in cron_schedules
        assert f"{table}_schedule_type_check" in cron_schedules
        assert "schedule_type IN ('manual', 'hourly', 'cron')" in cron_schedules
        assert f"{table}_schedule_cron_check" in cron_schedules

    assert "runtime IN ('python', 'node', 'java', 'shell')" in shell_runtime
