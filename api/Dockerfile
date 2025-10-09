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

WORKDIR /code

COPY --from=builder /usr/local /usr/local

COPY ./events_api ./events_api

EXPOSE 8000

CMD ["gunicorn", \
    "-w", "2", \
    "-k", "uvicorn.workers.UvicornWorker", \
    "events_api.main:app", \
    "--bind", "0.0.0.0:8000", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]