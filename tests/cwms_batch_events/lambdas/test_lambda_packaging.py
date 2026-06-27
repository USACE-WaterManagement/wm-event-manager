from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_dispatcher_workflow_packages_shared_modules_and_sdk_support():
    workflow = (ROOT / ".github/workflows/cwbi-build-push-dispatcher.yml").read_text(
        encoding="utf-8"
    )
    requirements = (
        ROOT / "cwms_batch_events/lambdas/dispatch_job/requirements.txt"
    ).read_text(encoding="utf-8")

    assert "pip install -r cwms_batch_events/lambdas/dispatch_job/requirements.txt -t package" in workflow
    assert "cp -r cwms_batch_events package/" in workflow
    assert "cp cwms_batch_events/lambdas/dispatch_job/dispatcher.py package/" in workflow
    assert "boto3>=" in requirements
    assert "botocore>=" in requirements


def test_status_updater_workflow_can_remain_single_file_package():
    workflow = (
        ROOT / ".github/workflows/cwbi-build-push-status-updater.yml"
    ).read_text(encoding="utf-8")
    requirements = (
        ROOT / "cwms_batch_events/lambdas/update_batch_job_status/requirements.txt"
    ).read_text(encoding="utf-8")
    source = (
        ROOT / "cwms_batch_events/lambdas/update_batch_job_status/status_updater.py"
    ).read_text(encoding="utf-8")

    assert "cp status_updater.py package/" in workflow
    assert "requests" in requirements
    assert "cwms_batch_events" not in source
