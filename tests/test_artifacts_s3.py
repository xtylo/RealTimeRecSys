import json

import boto3
from moto import mock_aws

from app.infrastructure.artifacts import load_artifacts


@mock_aws
def test_load_artifacts_from_s3(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("ARTIFACTS_SOURCE", "s3")
    monkeypatch.setenv("ARTIFACTS_BUCKET", "test-bucket")
    monkeypatch.setenv("ARTIFACTS_PREFIX", "models/v1")

    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")
    s3.put_object(Bucket="test-bucket", Key="models/v1/related.json", Body=json.dumps({"1": [2]}))
    s3.put_object(Bucket="test-bucket", Key="models/v1/popular.json", Body=json.dumps([5]))

    related, popular = load_artifacts()
    assert related == {"1": [2]}
    assert popular == [5]
