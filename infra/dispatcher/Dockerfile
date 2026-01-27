FROM python:3.13-slim

WORKDIR /app

COPY infra/dispatcher/requirements.txt ./infra/dispatcher/requirements.txt
RUN pip install --no-cache-dir -r ./infra/dispatcher/requirements.txt

COPY infra/dispatcher ./infra/dispatcher

ENV PYTHONPATH=/app

CMD ["python", "-u", "infra/dispatcher/dispatcher_loop.py"]
