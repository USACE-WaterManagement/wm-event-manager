"""
build_catalogs.py will generate and push script catalogs for local district job repos.

Any local repos for which to build catalogs should be included in the
catalog_config.toml file.  A json script catalog will be generated for each repo
indicated in the config and pushed to the local s3/minio bucket under the appropriate
office prefix.
"""

import boto3
import json
from pathlib import Path
import tomllib

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="eventsadmin",
    aws_secret_access_key="eventsadmin",
)


def build_catalog(office: str, folder_path: str):
    path = Path(folder_path)
    python_folder = path / "python"
    if not python_folder.exists():
        raise FileNotFoundError(f"Could not find {python_folder}")
    scripts = python_folder.glob("*.py")
    return {"scripts": [f.name for f in scripts]}


def push_catalog_to_s3(office: str, catalog: dict[str, list[str]]):
    bucket_name = "wm-web-internal-dev"
    object_key = f"{office}/scripts_catalog.json"
    json_body = json.dumps(catalog, indent=2)

    s3.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=json_body,
        ContentType="application/json",
    )

    print(f"Uploaded {office} catalog to {object_key}")


def push_catalogs_from_config():
    with open("catalog_config.toml", "rb") as config_file:
        config = tomllib.load(config_file)
        for office, path in config["repos"].items():
            try:
                catalog = build_catalog(office, path)
                push_catalog_to_s3(office, catalog)
            except FileNotFoundError:
                print(f"No valid repo for {office} found at {path}")


if __name__ == "__main__":
    push_catalogs_from_config()
