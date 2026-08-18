from unittest import mock
import pandas as pd

from transform.read_table import read_tables_from_s3


@mock.patch("transform.read_table.pd.read_parquet")
def test_read_tables_from_s3_return_dataframe(mock_read_parquet):

    expected_df = pd.DataFrame({
        "design_id": [1, 2],
        "name": ["A", "B"]
    })

    mock_read_parquet.return_value = expected_df

    df = read_tables_from_s3("designs")

    assert isinstance(df, pd.DataFrame)