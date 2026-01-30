"""
Lambda function: update_batch_job_status

This Lambda will update the cwms-batch-events job database status for a job
whenever an AWS Batch job state change event occurs. It is intended to be triggered
through EventBridge. It handles FAILED, RUNNING, and SUCCEEDED job status types. The
status is converted to a cwms-batch-events status code and the run_time or end_time
is updated as needed.
"""

from cwms_batch_events.core.job_database.postgres import session
from cwms_batch_events.core.processing import update_batch_job_status


def lambda_handler(event, context):
    try:
        detail = event.get("detail", {})
        batch_job_id = detail.get("jobId")
        status = detail.get("status")
        time_iso = event.get("time")

        update_batch_job_status(batch_job_id, status, time_iso, session.create_session)

        return {"status": "ok"}

    except Exception as e:
        print(f"Error updating batch job status: {e}")
        return {"status": "error", "message": str(e)}
