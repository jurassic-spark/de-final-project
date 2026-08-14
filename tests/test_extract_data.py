import pytest
import pandas as pd
from unittest import mock
from psycopg2 import OperationalError
from pandas.errors import DatabaseError
from ingestion.extract_data import (
    extract_data,
    lambda_handler,
    save_dataframe_to_s3_parquet,
)
import boto3
import pytest
from moto import mock_aws
from pandas.testing import assert_frame_equal
from io import BytesIO
from datetime import datetime as real_datetime


@mock.patch("ingestion.extract_data.pd.read_sql_query")
@mock.patch("ingestion.extract_data.psycopg2.connect")
def test_extract_data(mock_connect, mock_read_sql_query):
    secrets = {
        "username": "test_user",
        "password": "test_password",
        "dbname": "test_db",
        "host": "test_host",
        "port": 5432,
    }

    mock_connect.return_value = mock.MagicMock()
    mock_read_sql_query.return_value = pd.DataFrame(
        {"last_updated": ["2026-01-02 10:00:00"]}
    )

    result = extract_data(
        secrets=secrets, table_name="sales_order", timestamp="2026-01-01 00:00:00"
    )

    assert isinstance(result, pd.DataFrame)


# sad path
def test_extract_data_raises_exception():
    secrets = {
        "username": "test_user",
        "password": "test_password",
        "dbname": "test_db",
        "host": "test.host",
        "port": 5432,
    }

    with pytest.raises(OperationalError):
        extract_data(secrets, table_name="sales_order", timestamp="2026-01-01 00:00:00")


@mock_aws
def test_save_dataframe_to_s3_parquet():
    # arrange
    s3_client = boto3.client("s3", region_name="us-east-1")
    # create a bucket
    s3_client.create_bucket(Bucket="mock-s3")
    mock_data = {
        "secrets": ["secrets"],
        "table_name": ["sales_order"],
        "timestamp": ["2026-01-01 00:00:00"],
    }
    mock_df = pd.DataFrame(mock_data)
    filepath = save_dataframe_to_s3_parquet(mock_df, "mock-s3", "sales_order")
    response = s3_client.get_object(
        Bucket="mock-s3",
        Key=filepath,
    )
    saved_df = pd.read_parquet(BytesIO(response["Body"].read()))

    assert_frame_equal(mock_df, saved_df)


@mock.patch("ingestion.extract_data.save_dataframe_to_s3_parquet")
@mock.patch("ingestion.extract_data.extract_data")
@mock.patch("ingestion.extract_data.get_secret")
@mock.patch("ingestion.extract_data.boto3.client")
def test_lambda_handler_extracts_all_data_when_bucket_is_empty(
    mock_boto_client,
    mock_get_secret,
    mock_extract_data,
    mock_save_dataframe,
    monkeypatch,
):
    monkeypatch.setenv("INGEST_BUCKET", "mock-s3")

    mock_s3_client = mock.MagicMock()
    mock_boto_client.return_value = mock_s3_client

    mock_s3_client.list_objects_v2.return_value = {"KeyCount": 0}

    mock_get_secret.return_value = {
        "username": "test_user",
        "password": "test_password",
        "dbname": "test_db",
        "host": "test_host",
        "port": 5432,
    }

    mock_extract_data.return_value = pd.DataFrame()

    lambda_handler({}, None)

    # store the args passed to the mock_extract_data function
    # for the first table 'sales_order' which is index [0]
    first_call = mock_extract_data.call_args_list[0]

    # assert that the keyword arg for the mock_extract_data function
    #'timestamp' is a None value
    assert first_call.kwargs["timestamp"] == None
    assert mock_extract_data.call_count == 11
    assert mock_save_dataframe.call_count == 11


@mock.patch("ingestion.extract_data.save_dataframe_to_s3_parquet")
@mock.patch("ingestion.extract_data.extract_data")
@mock.patch("ingestion.extract_data.get_secret")
@mock.patch("ingestion.extract_data.boto3.client")
@mock.patch("ingestion.extract_data.datetime")
def test_lambda_handler_uses_timestamp_when_bucket_contains_data(
    mock_datetime,
    mock_boto_client,
    mock_get_secret,
    mock_extract_data,
    mock_save_dataframe,
    monkeypatch,
):
    monkeypatch.setenv("INGEST_BUCKET", "mock-s3")

    mock_s3_client = mock.MagicMock()
    mock_boto_client.return_value = mock_s3_client

    mock_s3_client.list_objects_v2.return_value = {"KeyCount": 11}

    mock_get_secret.return_value = {
        "username": "test_user",
        "password": "test_password",
        "dbname": "test_db",
        "host": "test_host",
        "port": 5432,
    }

    mock_datetime.now.return_value = real_datetime(
        2026,
        5,
        10,
        12,
        0,
        0,
    )

    mock_extract_data.return_value = pd.DataFrame()

    lambda_handler({}, None)

    first_call = mock_extract_data.call_args_list[0]

    assert first_call.kwargs["timestamp"] == real_datetime(
        2026,
        5,
        10,
        11,
        30,
        0,
    )
