from unittest.mock import MagicMock, patch

import pytest

import pandas as pd

from transform.transform_data import (
    get_dataframe_from_s3,
    get_currency_name,
    transform_currency,
)


def test_get_dataframe_from_s3_returns_a_df():
    # Define the mock S3 location.
    bucket = "mock-s3"
    object_key = "raw/currency/currency.parquet"

    # Define the DataFrame pandas should return.
    expected_df = pd.DataFrame(
        {
            "currency_id": [1],
            "currency_code": ["mock_money"],
            "created_at": ["2022-11-03 00:00:00"],
        }
    )

    # Mock the s3fs filesystem used to access S3.
    mock_filesystem = MagicMock()

    # Mock s3fs and pandas so no real S3 request is made.
    with (
        patch(
            "transform.transform_data.s3fs.S3FileSystem",
            return_value=mock_filesystem,
        ),
        patch(
            "transform.transform_data.pd.read_parquet",
            return_value=expected_df,
        ) as mock_read_parquet,
    ):
        result_df = get_dataframe_from_s3(
            bucket,
            object_key,
        )

    # Check the function returns the expected DataFrame.
    pd.testing.assert_frame_equal(result_df, expected_df)

    # Check pandas was called with the correct S3 path and filesystem.
    mock_read_parquet.assert_called_once_with(
        "s3://mock-s3/raw/currency/currency.parquet",
        filesystem=mock_filesystem,
    )


def test_get_currency_name_returns_currency_name():
    assert get_currency_name("GBP") == "Pound Sterling"


def test_transform_currency_only_contains_required_columns():
    mock_df = pd.DataFrame(
        {
            "currency_id": [1, 2],
            "currency_code": ["GBP", "USD"],
            "created_at": ["2026-01-01", "2026-01-02"],
            "last_updated": ["2026-01-03", "2026-01-04"],
        }
    )

    result = transform_currency(mock_df)

    assert isinstance(result, pd.DataFrame)

    assert list(result.columns) == [
        "currency_id",
        "currency_code",
        "currency_name",
    ]


def test_transform_currency_raises_error_if_missing_currency_code():
    mock_df = pd.DataFrame(
        {
            "currency_id": [1, 2],
            "currency_code": ["", ""],
            "created_at": ["2026-01-01", "2026-01-02"],
            "last_updated": ["2026-01-03", "2026-01-04"],
        }
    )

    with pytest.raises(ValueError):
        transform_currency(mock_df)
