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
        KeySchema=[{"AttributeName": "JobId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "JobId", "AttributeType": "S"},
            {"AttributeName": "Script", "AttributeType": "S"},
            {"AttributeName": "User", "AttributeType": "S"},
            {"AttributeName": "Office", "AttributeType": "S"},
            {"AttributeName": "CreatedTime", "AttributeType": "S"},
            # {"AttributeName": "StartTime", "AttributeType": "S"},
            # {"AttributeName": "EndTime", "AttributeType": "S"},
            # {"AttributeName": "Status", "AttributeType": "S"},
            # {"AttributeName": "LogsUrl", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "UserIndex",
                "KeySchema": [
                    {"AttributeName": "User", "KeyType": "HASH"},
                    {"AttributeName": "CreatedTime", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "ALL",
                },
            },
            {
                "IndexName": "OfficeIndex",
                "KeySchema": [
                    {"AttributeName": "Office", "KeyType": "HASH"},
                    {"AttributeName": "CreatedTime", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "ALL",
                },
            },
            {
                "IndexName": "ScriptIndex",
                "KeySchema": [
                    {"AttributeName": "Script", "KeyType": "HASH"},
                    {"AttributeName": "CreatedTime", "KeyType": "RANGE"},
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
