# Builder

FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y gcc

WORKDIR /code

ARG REQ_FILE=requirements.txt

COPY ./requirements.txt ./requirements.txt
COPY ./requirements-dev.txt ./requirements-dev.txt

RUN pip install --no-cache-dir -r ${REQ_FILE}


# Runtime

FROM python:3.13-slim

RUN addgroup --system appuser \
 && adduser  --system --ingroup appuser --uid 10001 appuser

WORKDIR /code

COPY --from=builder /usr/local /usr/local

COPY ./cwms_batch_events/api ./cwms_batch_events/api

RUN chown -R appuser:appuser /code
USER appuser

EXPOSE 8000

CMD ["gunicorn", \
    "-w", "2", \
    "-k", "uvicorn.workers.UvicornWorker", \
    "cwms_batch_events.api.main:app", \
    "--bind", "0.0.0.0:8000", \
    "--env ROOT_PATH=/api", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]