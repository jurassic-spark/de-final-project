from unittest.mock import MagicMock, patch

import pytest

import pandas as pd

from transform.transform_data import (
    get_dataframe_from_s3,
    get_currency_name,
    transform_currency,
    transform_staff,
    transform_location,
    transform_sales,
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

def test_transform_currency_raises_error_for_invalid_code():
    mock_df = pd.DataFrame(
            {
                "currency_id": [1, 2],
                "currency_code": ["Apple", "Banana"],
                "created_at": ["2026-01-01", "2026-01-02"],
                "last_updated": ["2026-01-03", "2026-01-04"],
            }
        )

    with pytest.raises(ValueError):
            transform_currency(mock_df)

def test_transform_currency_standardises_currency_codes():
    mock_df = pd.DataFrame(
            {
                "currency_id": [1, 2],
                "currency_code": ["gbp", "usd"],
                "created_at": ["2026-01-01", "2026-01-02"],
                "last_updated": ["2026-01-03", "2026-01-04"],
            }
        )

    result_df = transform_currency(mock_df)

    assert result_df["currency_code"][0] == "GBP"
    assert result_df["currency_code"][1] == "USD"

def test_transform_staff_returns_df():
    mock_s_df = pd.DataFrame(
                {
                    "staff_id": [1, 2],
                    "first_name": ["jane", "doe"],
                    "last_name": ["john", "smith"],
                    "department_id": [1, 2],
                    "email_address": ["janedoe@emailaddress.com", "johnsmith@emailaddress.com"],
                    "created_at": ["2026-01-01", "2026-01-02"],
                    "last_updated": ["2026-01-03", "2026-01-04"],
                }
            )
    mock_d_df = pd.DataFrame(
                {
                    "department_id": [1, 2],
                    "department_name": ["finance", "comms"],
                    "location": ["manchester", "leeds"],
                    "manager": ["john", "ali"],
                    "created_at": ["2026-01-01", "2026-01-02"],
                    "last_updated": ["2026-01-03", "2026-01-04"],
                }
            )
    result = transform_staff(mock_s_df, mock_d_df)
    assert isinstance(result, pd.DataFrame)
    assert len(result.columns) == 6
    assert 'staff_id' in result.columns
    assert 'first_name' in result.columns
    assert 'last_name' in result.columns
    assert 'department_name' in result.columns
    assert 'location' in result.columns
    assert 'email_address' in result.columns


def test_transform_staff_returns_df_with_no_duplicates():
    mock_s_df = pd.DataFrame(
                    {
                        "staff_id": [1, 1],
                        "first_name": ["jane", "doe"],
                        "last_name": ["john", "smith"],
                        "department_id": [1, 2],
                        "email_address": ["janedoe@emailaddress.com", "johnsmith@emailaddress.com"],
                        "created_at": ["2026-01-01", "2026-01-02"],
                        "last_updated": ["2026-01-03", "2026-01-04"],
                    }
                )
    mock_d_df = pd.DataFrame(
                    {
                        "department_id": [1, 2],
                        "department_name": ["finance", "comms"],
                        "location": ["manchester", "leeds"],
                        "manager": ["john", "ali"],
                        "created_at": ["2026-01-01", "2026-01-02"],
                        "last_updated": ["2026-01-03", "2026-01-04"],
                    }
                )
    result = transform_staff(mock_s_df, mock_d_df)
    repeated_staff_ids = result[result["staff_id"].duplicated(keep=False)]
    assert len(repeated_staff_ids) == 0

def test_transform_staff_removes_rows_with_null_values():
    mock_s_df = pd.DataFrame(
                    {
                        "staff_id": [1, 2],
                        "first_name": ["jane", "john"],
                        "last_name": ["doe", "smith"],
                        "department_id": [1, 2],
                        "email_address": ["janedoe@emailaddress.com", "johnsmith@emailaddress.com"],
                        "created_at": ["2026-01-01", "2026-01-02"],
                        "last_updated": ["2026-01-03", "2026-01-04"],
                    }
                )
    mock_d_df = pd.DataFrame(
                    {
                        "department_id": [1, 2],
                        "department_name": ["finance", "comms"],
                        "location": ["manchester", ""],
                        "manager": ["john", "ali"],
                        "created_at": ["2026-01-01", "2026-01-02"],
                        "last_updated": ["2026-01-03", "2026-01-04"],
                    }
                )
    result = transform_staff(mock_s_df, mock_d_df)
    assert len(result) == 1

def test_transform_location_returns_df():
    mock_df = pd.DataFrame(
            {
                "address_id": [1, 2],
                "address_line_1": ["1 new street", "flat 1"],
                "address_line_2": ["", "2 new street"],
                "district": ["new district", "old district"],
                "city": ["london", "leeds"],
                "postal_code": ["L58362", "LE 84 2152"],
                "country": ["UK", "UK"],
                "phone": ["542 217832 12", "323 437811 328"],
                "created_at": ["2026-01-01", "2026-01-02"],
                "last_updated": ["2026-01-03", "2026-01-04"],
            }
        )
    result = transform_location(mock_df)
    assert isinstance(result, pd.DataFrame)
    assert len(result.columns) == 8
    assert "location_id" in result.columns
    assert "address_line_1" in result.columns
    assert "address_line_2" in result.columns
    assert "district" in result.columns
    assert "city" in result.columns
    assert "postal_code" in result.columns
    assert "country" in result.columns
    assert "phone" in result.columns

def test_transform_location_returns_df_with_no_duplicates():
    mock_df = pd.DataFrame(
            {
                "address_id": [1, 1],
                "address_line_1": ["1 new street", "flat 1"],
                "address_line_2": ["", "2 new street"],
                "district": ["new district", "old district"],
                "city": ["london", "leeds"],
                "postal_code": ["L58362", "LE 84 2152"],
                "country": ["UK", "UK"],
                "phone": ["542 217832 12", "323 437811 328"],
                "created_at": ["2026-01-01", "2026-01-02"],
                "last_updated": ["2026-01-03", "2026-01-04"],
            }
        )
    result = transform_location(mock_df)
    repeated_rows = result[result["location_id"].duplicated(keep=False)]
    assert len(repeated_rows) == 0
    assert len(result) == 1

def test_transform_location_removes_rows_with_missing_values():
    mock_df = pd.DataFrame(
            {
                "address_id": [1, 2],
                "address_line_1": ["1 new street", ""],
                "address_line_2": ["", "2 new street"],
                "district": ["new district", "old district"],
                "city": ["london", "leeds"],
                "postal_code": ["L58362", "LE 84 2152"],
                "country": ["UK", "UK"],
                "phone": ["542 217832 12", "323 437811 328"],
                "created_at": ["2026-01-01", "2026-01-02"],
                "last_updated": ["2026-01-03", "2026-01-04"],
            }
        )
    result = transform_location(mock_df)
    repeated_rows = result[result["location_id"].duplicated(keep=False)]
    assert len(repeated_rows) == 0
    assert len(result) == 1

def test_transform_sales_returns_df():
    mock_df = pd.DataFrame(
            {
                "sales_order_id": [1, 2],
                "created_at": ["2026-01-01", "2026-01-02"],
                "last_updated": ["2026-01-01", "2026-01-02"],
                "design_id": [1, 2],
                "staff_id": [1, 2],
                "counterparty_id": [1, 2],
                "units_sold": [4734, 27354],
                "unit_price": [1.45, 1.76],
                "currency_id": [1, 2],
                "agreed_delivery_date": ["2026-01-01", "2026-01-02"],
                "agreed_payment_date": ["2026-01-03", "2026-01-04"],
                "agreed_delivery_location_id": [1, 2],
            }
        )
    result = transform_sales(mock_df)
    assert isinstance(result, pd.DataFrame)
    assert len(result.columns) == 15
    assert "sales_record_id" in result.columns
    assert "sales_order_id" in result.columns
    assert "created_date" in result.columns
    assert "created_time" in result.columns
    assert "last_updated_date" in result.columns
    assert "last_updated_time" in result.columns
    assert "sales_staff_id" in result.columns
    assert "counterparty_id" in result.columns
    assert "units_sold" in result.columns
    assert "unit_price" in result.columns
    assert "currency_id" in result.columns
    assert "design_id" in result.columns
    assert "agreed_payment_date" in result.columns
    assert "agreed_delivery_date" in result.columns
    assert "agreed_delivery_location_id" in result.columns


def test_transform_sales_returns_df_with_no_duplicates():
    mock_df = pd.DataFrame(
            {
                "sales_order_id": [1, 1],
                "created_at": ["2026-01-01", "2026-01-01"],
                "last_updated": ["2026-01-02", "2026-01-02"],
                "design_id": [1, 1],
                "staff_id": [3, 3],
                "counterparty_id": [2, 2],
                "units_sold": [4734, 4734],
                "unit_price": [1.45, 1.45],
                "currency_id": [5, 5],
                "agreed_delivery_date": ["2026-01-03", "2026-01-03"],
                "agreed_payment_date": ["2026-01-02", "2026-01-02"],
                "agreed_delivery_location_id": [2, 2],
            }
        )
    result = transform_sales(mock_df)
    repeated_orders = result[result["sales_order_id"].duplicated(keep=False)]
    assert len(repeated_orders) == 0
    assert len(result) == 1

def test_transform_sales_removes_rows_with_missing_values():
    mock_df = pd.DataFrame(
            {
                "sales_order_id": [1, 1],
                "created_at": ["2026-01-01", "2026-01-01"],
                "last_updated": ["2026-01-02", "2026-01-02"],
                "design_id": [1, None],
                "staff_id": [3, 3],
                "counterparty_id": [2, 2],
                "units_sold": [4734, 4734],
                "unit_price": [1.45, 1.45],
                "currency_id": [5, 5],
                "agreed_delivery_date": ["2026-01-03", "2026-01-03"],
                "agreed_payment_date": ["2026-01-02", "2026-01-02"],
                "agreed_delivery_location_id": [2, 2],
            }
        )
    result = transform_sales(mock_df)
    assert len(result) == 1