import boto3
import os
import pytest
from moto import mock_aws
from src.utils import get_secret


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""

    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@mock_aws
def test_get_secrets_raises_clienterror_with_invalid_credentials(aws_credentials):
    secrets_client = boto3.client("secretsmanager", region_name="eu-west-2")
    secrets_client.create_secret(
        Name="test_secret", SecretString='{"key1": "value1", "key2": "value2"}'
    )

    expected_result = {"key1": "value1", "key2": "value2"}
    assert get_secret("test_secret") == expected_result
