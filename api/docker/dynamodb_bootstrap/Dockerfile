FROM python:3.13-slim

WORKDIR /app

RUN pip install boto3

COPY dynamodb_bootstrap.py .

CMD ["python", "dynamodb_bootstrap.py"]