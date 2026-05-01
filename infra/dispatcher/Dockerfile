FROM python:3.13-slim

WORKDIR /app

# Install system deps (psycopg2, docker SDK)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY cwms_batch_events ./cwms_batch_events
COPY infra ./infra

ENV PYTHONPATH=/app

CMD ["python", "-u", "infra/dispatcher/dispatcher_loop.py"]
