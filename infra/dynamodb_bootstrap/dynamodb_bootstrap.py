import boto3
import time
import os
from botocore.exceptions import EndpointConnectionError

dynamodb_endpoint = os.getenv("DYNAMODB_HOST", "http://dynamodb:9010")
table_name = "WM-Event-Manager-Jobs"

dynamodb = boto3.client(
    "dynamodb",
    endpoint_url=dynamodb_endpoint,
    region_name="us-west-1",
    aws_access_key_id="eventsadmin",
    aws_secret_access_key="eventsadmin",
)


def wait_for_dynamodb(max_attempts=10, delay=2):
    for attempt in range(1, max_attempts + 1):
        try:
            dynamodb.list_tables()
            print("DynamoDB is ready.")
            return True
        except EndpointConnectionError:
            print(
                f"DynamoDB not ready (attempt {attempt}/{max_attempts}), retrying in {delay}s..."
            )
            time.sleep(delay)
    print("DynamoDB did not become ready in time.")
    return False


def create_table(name):
    tables = dynamodb.list_tables()
    if name in tables.get("TableNames", []):
        print(f"ℹ️ Table '{name}' already exists.")
        return

    dynamodb.create_table(
        TableName=table_name,
        BillingMode="PAY_PER_REQUEST",
        KeySchema=[{"AttributeName": "job_id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "job_id", "AttributeType": "S"},
            {"AttributeName": "script", "AttributeType": "S"},
            {"AttributeName": "user", "AttributeType": "S"},
            {"AttributeName": "office", "AttributeType": "S"},
            {"AttributeName": "created_time", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "user_index",
                "KeySchema": [
                    {"AttributeName": "user", "KeyType": "HASH"},
                    {"AttributeName": "created_time", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "ALL",
                },
            },
            {
                "IndexName": "office_index",
                "KeySchema": [
                    {"AttributeName": "office", "KeyType": "HASH"},
                    {"AttributeName": "created_time", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "ALL",
                },
            },
            {
                "IndexName": "script_index",
                "KeySchema": [
                    {"AttributeName": "script", "KeyType": "HASH"},
                    {"AttributeName": "created_time", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "ALL",
                },
            },
        ],
    )


if __name__ == "__main__":
    if wait_for_dynamodb():
        create_table(table_name)
