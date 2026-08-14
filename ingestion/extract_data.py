from src.utils import get_secret
import psycopg2
from psycopg2 import sql
import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow import Table
from datetime import datetime
import boto3
from io import BytesIO
import pandas as pd




def extract_data(secrets, table_name, timestamp):
    username = secrets["username"]
    password = secrets["password"]
    db_name = secrets["dbname"]
    host = secrets["host"]
    port = secrets["port"]
    connection = psycopg2.connect(user=username, password=password, dbname=db_name, host=host, port=port)
    query = f"SELECT * FROM {table_name} WHERE last_updated > %s;"
    dataframe = pd.read_sql(query, connection, params=[timestamp])
    print("dataframe:", table_name)
    return dataframe

def save_dataframe_to_s3_parquet(dataframe, bucket_name, table_name):
    parquet_buffer = BytesIO()

    dataframe.to_parquet(parquet_buffer, index=False)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    object_key = f"raw/{table_name}/{table_name}_{timestamp}.parquet"

    s3_client = boto3.client("s3")

    s3_client.put_object(
    Bucket=bucket_name,
    Key=object_key,
    Body=parquet_buffer.getvalue()
)

    return object_key

# df = extract_data(get_secret("totesys_database_credentials"), "sales_order", "2026-01-08 00:00:00.000")
    
# save_dataframe_to_s3_parquet(df, "rawsalesdata.finalproject", "sales_order")











    



