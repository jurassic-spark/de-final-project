import os

import pandas as pd
import s3fs

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from ingestion.extract_data import get_secret


load_dotenv()


def get_engine(secret_name):

    secret = get_secret(secret_name)
    print("Secret name:", secret_name)
    return create_engine(
        f"postgresql+psycopg2://"
        f"{secret['username']}:{secret['password']}"
        f"@{os.environ['RDS_HOST']}:"
        f"{os.environ.get('RDS_PORT', '5432')}/"
        f"{os.environ['RDS_DATABASE']}"
    )



def clear_rds_tables(engine):
    """Clear existing data from the RDS tables."""

    with engine.begin() as connection:

        connection.execute(text("""
            TRUNCATE TABLE
                fact_sales_order,
                dim_staff,
                dim_location,
                dim_currency,
                dim_design,
                dim_counterparty,
                dim_date;
        """))

    print("RDS tables cleared successfully.")


def load_tables_from_s3(bucket, engine):
    """Load the latest processed file for each table from S3 into RDS."""

    fs = s3fs.S3FileSystem()

    tables = [
        "dim_counterparty",
        "dim_currency",
        "dim_date",
        "dim_design",
        "dim_location",
        "dim_staff",
        "fact_sales"
    ]

    for table in tables:

        # Get all parquet files for this table
        files = fs.glob(
            f"{bucket}/processed/{table}/*.parquet"
        )

        if not files:
            print(f"No files found for {table}")
            continue

        # Get the latest file for this table
        latest_file = max(files)

        print(f"\nReading {table}")
        print(f"Latest file: {latest_file}")

        # Read parquet file
        df = pd.read_parquet(
            f"s3://{latest_file}",
            filesystem=fs
        )

        print(f"{len(df)} rows found")

        
        table_name = table

       
        # Load into RDS
        df.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False
        )

        print(
            f"Loaded {len(df)} rows "
            f"into {table_name}"
        )

def seed(bucket, secret_name):
    """Clear RDS and load fresh data from processed S3."""

    print("Starting database seeding...")

    engine = get_engine(secret_name)

    try:

        #  Clear existing RDS data
        clear_rds_tables(engine)

        #  Load data from S3
        load_tables_from_s3(
            bucket,
            engine
        )

        print("Database seeding completed successfully.")

    except Exception as error:

        print(f"Error during seeding: {error}")
        raise

    finally:

        engine.dispose()






def lambda_handler(event, context):

    print("Starting seed Lambda...")

    seed()

    return {
        "statusCode": 200,
        "body": "RDS seeded successfully"
    }