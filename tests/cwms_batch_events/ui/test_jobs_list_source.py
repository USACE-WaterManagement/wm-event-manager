from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
JOBS_LIST = ROOT / "ui" / "src" / "features" / "jobs-list" / "JobsList.tsx"
USER_OFFICES_HOOK = (
    ROOT / "ui" / "src" / "features" / "jobs-list" / "useUserOffices.ts"
)


def test_jobs_list_office_filter_uses_member_offices_not_admin_offices():
    source = JOBS_LIST.read_text(encoding="utf-8")
    hook_source = USER_OFFICES_HOOK.read_text(encoding="utf-8")

    assert 'from "./useUserOffices"' in source
    assert "useAdminOffices" not in source
    assert "userOffices.data.sort()" in source
    assert "/api/users/me/offices" in hook_source
    assert "/api/users/me/admin-offices" not in hook_source
