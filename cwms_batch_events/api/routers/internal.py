from fastapi import APIRouter, Depends, Header, HTTPException, status
from uuid import UUID


from cwms_batch_events.core.auth.service.dependencies import require_internal_auth
from cwms_batch_events.api.dependencies import (
    get_job_database,
)
from cwms_batch_events.core.job_database.base import JobDatabase
from cwms_batch_events.core.models import (
    BatchJobStatusUpdateRequest,
    BindExternalJobIdRequest,
    RuntimeEnvResponse,
)
from cwms_batch_events.core.processing import (
    MissingBatchJobError,
    update_batch_job_status,
)
from cwms_batch_events.core.runtime_auth import validate_runtime_token
from cwms_batch_events.core.secret_broker import (
    MissingJobError,
    MissingSecretError,
    resolve_runtime_env,
)

router = APIRouter(prefix="/internal", include_in_schema=False)


@router.post(
    "/batch-jobs/{batch_job_id}/status",
    status_code=status.HTTP_204_NO_CONTENT,
)
def update_batch_job_status_endpoint(
    batch_job_id: str,
    payload: BatchJobStatusUpdateRequest,
    _=Depends(require_internal_auth),
    job_db: JobDatabase = Depends(get_job_database),
):
    try:
        update_batch_job_status(
            batch_job_id, payload.status, payload.event_time, job_db
        )

    except MissingBatchJobError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/jobs/{job_id}/external-job-id",
    status_code=status.HTTP_204_NO_CONTENT,
)
def bind_external_job_id(
    job_id: str,
    payload: BindExternalJobIdRequest,
    _=Depends(require_internal_auth),
    job_db: JobDatabase = Depends(get_job_database),
):
    try:
        job_db.bind_external_job_id(UUID(job_id), payload.external_job_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/jobs/{job_id}/runtime-env",
    response_model=RuntimeEnvResponse,
)
def get_runtime_env(
    job_id: str,
    x_runtime_token: str = Header(None),
    job_db: JobDatabase = Depends(get_job_database),
):
    try:
        parsed_job_id = UUID(job_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job id",
        ) from e

    valid_token, token_error = validate_runtime_token(x_runtime_token, parsed_job_id)
    if not valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=token_error,
        )
    try:
        return resolve_runtime_env(parsed_job_id, job_db)

    except MissingJobError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except MissingSecretError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
