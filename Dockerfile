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

COPY ./adhoc_api ./adhoc_api

EXPOSE 8000

ENV DEPLOY_MODE=aws

CMD ["uvicorn", "adhoc_api.main:app", "--host", "0.0.0.0", "--port", "8000"]