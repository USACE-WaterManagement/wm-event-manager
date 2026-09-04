import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("ALB_DNS_NAME", "http://events")
os.environ.setdefault("APP_SECRETS_ARN", "arn:aws:secretsmanager:test")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-gov-west-1")
