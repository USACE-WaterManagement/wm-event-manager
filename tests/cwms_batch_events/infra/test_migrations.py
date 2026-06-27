from pathlib import Path


def test_enabled_schedule_shape_is_enforced_in_database_migration():
    migration = Path(
        "infra/migration/main/V1_01_10__Enabled_Schedule_Shape.sql"
    ).read_text()

    assert "scripts_enabled_schedule_shape_check" in migration
    assert "jobs_enabled_schedule_shape_check" in migration
    assert "NOT schedule_enabled" in migration
    assert "schedule_type = 'hourly'" in migration
    assert "schedule_minute IS NOT NULL" in migration
    assert "schedule_type = 'cron'" in migration
    assert "schedule_cron IS NOT NULL" in migration
    assert "btrim(schedule_cron) <> ''" in migration
