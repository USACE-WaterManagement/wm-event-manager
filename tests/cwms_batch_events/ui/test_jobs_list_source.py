from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
JOBS_LIST = ROOT / "ui" / "src" / "features" / "jobs-list" / "JobsList.tsx"
JOB_DETAIL = ROOT / "ui" / "src" / "features" / "jobs-list" / "JobDetail.tsx"
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


def test_job_detail_shows_shared_runtime_correlation_fields():
    source = JOB_DETAIL.read_text(encoding="utf-8")

    for field in [
        '"scriptSlug"',
        '"repoPath"',
        '"runtime"',
        '"resourceProfile"',
        '"commandArgs"',
        '"externalJobId"',
        '"id"',
    ]:
        assert field in source

    assert '"repoPath",' in source
    assert '"externalJobId",' in source
