import psycopg2
from psycopg2 import sql
import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow import Table
from datetime import datetime
import boto3
from io import BytesIO
import pandas as pd
import os
import json
from botocore.exceptions import ClientError
from datetime import datetime, timedelta


def get_secret(secret_name):

    region_name = "eu-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return json.loads(get_secret_value_response["SecretString"])

    except ClientError as e:
        raise e


def extract_data(secrets, table_name, timestamp):
    username = secrets["username"]
    password = secrets["password"]
    db_name = secrets["dbname"]
    host = secrets["host"]
    port = secrets["port"]

    connection = psycopg2.connect(
        user=username, password=password, dbname=db_name, host=host, port=port
    )

    cur = connection.cursor()
    if timestamp == None:
        query_all = f"SELECT * FROM {table_name}"
        cur.execute(query_all)
    else:
        query_timestamp = f"SELECT * FROM {table_name} WHERE last_updated > %s"
        cur.execute(query_timestamp, (timestamp,))

    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    connection.close()

    data_string = [
        tuple(str(col) if hasattr(col, "isoformat") else col for col in row)
        for row in rows
    ]
    df = pd.DataFrame(data_string, columns=columns)

    print("dataframe:", table_name)
    return df


def save_dataframe_to_s3_parquet(dataframe, bucket_name, table_name):
    parquet_buffer = BytesIO()

    dataframe.to_parquet(parquet_buffer, index=False)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    object_key = f"raw/{table_name}/{table_name}_{timestamp}.parquet"  # Potential specificity using timestamps here

    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket=bucket_name, Key=object_key, Body=parquet_buffer.getvalue()
    )

    return object_key


def lambda_handler(event, context):
    s3_client = boto3.client("s3")
    ingest_objects = s3_client.list_objects_v2(Bucket=os.environ["INGEST_BUCKET"])

    if ingest_objects.get("KeyCount", 0) > 0:
        timestamp = datetime.now() - timedelta(minutes=30)
    else:
        timestamp = None

    secret = get_secret("totesys_database_credentials")

    known_tables = [
        "sales_order",
        "design",
        "currency",
        "staff",
        "counterparty",
        "address",
        "department",
        "purchase_order",
        "payment_type",
        "payment",
        "transaction",
    ]

    for table in known_tables:
        df = extract_data(secret, table, timestamp=timestamp)

        save_dataframe_to_s3_parquet(
            dataframe=df, bucket_name=os.environ["INGEST_BUCKET"], table_name=table
        )
