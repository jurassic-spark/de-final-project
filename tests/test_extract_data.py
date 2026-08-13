import pytest
import pandas as pd
from unittest import mock
from psycopg2 import OperationalError

from pandas.errors import DatabaseError
from ingestion.extract_data import extract_data


@mock.patch("ingestion.extract_data.pd.read_sql_query")
@mock.patch("ingestion.extract_data.psycopg2.connect")
def test_extract_data(mock_connect, mock_read_sql_query):
    secrets = {
        "username": "test_user",
        "password": "test_password",
        "dbname": "test_db",
        "host": "test_host",
        "port": 5432
    }

    mock_connect.return_value = mock.MagicMock()
    mock_read_sql_query.return_value = pd.DataFrame({
        "last_updated": ["2026-01-02 10:00:00"]
    })

    result = extract_data(
        secrets=secrets,
        table_name="sales_order",
        timestamp="2026-01-01 00:00:00"
    )

    assert isinstance(result, pd.DataFrame)



# sad path
def test_extract_data_raises_exception():
    secrets = {
        "username": "test_user",
        "password": "test_password",
        "dbname": "test_db",
        "host": "test.host",
        "port": 5432
    }


    with pytest.raises(OperationalError):
        extract_data(secrets, table_name="sales_order", timestamp="2026-01-01 00:00:00")






