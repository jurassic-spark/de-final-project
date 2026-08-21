
import os
import psycopg2
from dotenv import load_dotenv
import boto3
import json
from ingestion.extract_data import get_secret
from botocore.exceptions import ClientError





def get_connection(secret_name):

    secret = get_secret(secret_name)

    connection = psycopg2.connect(
        host=os.environ["RDS_HOST"],
        port=os.environ.get("RDS_PORT", "5432"),
        database=os.environ["RDS_DATABASE"],
        user=secret["username"],
        password=secret["password"]
    )
    cursor = connection.cursor()

    cursor.execute("SELECT 1;")

    result = cursor.fetchone()

    cursor.close()

    if result == (1,):
        print("Successfully connected to RDS!")

    return connection


def create_tables(secret_name):
    """Create the dimension and fact tables in RDS."""

    connection = get_connection(secret_name)

    try:
        cursor = connection.cursor()

        # Drop existing tables
        cursor.execute("""
            DROP TABLE IF EXISTS fact_sales_order;
            DROP TABLE IF EXISTS dim_staff;
            DROP TABLE IF EXISTS dim_location;
            DROP TABLE IF EXISTS dim_currency;
            DROP TABLE IF EXISTS dim_design;
            DROP TABLE IF EXISTS dim_counterparty;
            DROP TABLE IF EXISTS dim_date;
        """)

        # dim_date
        cursor.execute("""
            CREATE TABLE dim_date (
                date_id DATE PRIMARY KEY NOT NULL,
                year INT NOT NULL,
                month INT NOT NULL,
                day INT NOT NULL,
                day_of_week INT NOT NULL,
                day_name VARCHAR NOT NULL,
                month_name VARCHAR NOT NULL,
                quarter INT NOT NULL
            );
        """)

        # dim_staff
        cursor.execute("""
            CREATE TABLE dim_staff (
                staff_id INT PRIMARY KEY NOT NULL,
                first_name VARCHAR NOT NULL,
                last_name VARCHAR NOT NULL,
                department_name VARCHAR NOT NULL,
                location VARCHAR NOT NULL,
                email_address VARCHAR NOT NULL
            );
        """)

        # dim_location
        cursor.execute("""
            CREATE TABLE dim_location (
                location_id INT PRIMARY KEY NOT NULL,
                address_line_1 VARCHAR NOT NULL,
                address_line_2 VARCHAR,
                district VARCHAR,
                city VARCHAR NOT NULL,
                postal_code VARCHAR NOT NULL,
                country VARCHAR NOT NULL,
                phone VARCHAR NOT NULL
            );
        """)

        # dim_currency
        cursor.execute("""
            CREATE TABLE dim_currency (
                currency_id INT PRIMARY KEY NOT NULL,
                currency_code VARCHAR NOT NULL,
                currency_name VARCHAR NOT NULL
            );
        """)

        # dim_design
        cursor.execute("""
            CREATE TABLE dim_design (
                design_id INT PRIMARY KEY NOT NULL,
                design_name VARCHAR NOT NULL,
                file_location VARCHAR NOT NULL,
                file_name VARCHAR NOT NULL
            );
        """)

        # dim_counterparty
        cursor.execute("""
            CREATE TABLE dim_counterparty (
                counterparty_id INT PRIMARY KEY NOT NULL,
                counterparty_legal_name VARCHAR NOT NULL,
                counterparty_legal_address_line_1 VARCHAR NOT NULL,
                counterparty_legal_address_line_2 VARCHAR,
                counterparty_legal_district VARCHAR,
                counterparty_legal_city VARCHAR NOT NULL,
                counterparty_legal_postal_code VARCHAR NOT NULL,
                counterparty_legal_country VARCHAR NOT NULL,
                counterparty_legal_phone_number VARCHAR NOT NULL
            );
        """)

        # fact_sales_order
        cursor.execute("""
            CREATE TABLE fact_sales_order (
                sales_record_id SERIAL PRIMARY KEY,
                sales_order_id INT NOT NULL,
                created_date DATE NOT NULL,
                created_time TIME NOT NULL,
                last_updated_date DATE NOT NULL,
                last_updated_time TIME NOT NULL,
                sales_staff_id INT NOT NULL,
                counterparty_id INT NOT NULL,
                units_sold INT NOT NULL,
                unit_price NUMERIC(10, 2) NOT NULL,
                currency_id INT NOT NULL,
                design_id INT NOT NULL,
                agreed_payment_date DATE NOT NULL,
                agreed_delivery_date DATE NOT NULL,
                agreed_delivery_location_id INT NOT NULL,

                FOREIGN KEY (created_date)
                    REFERENCES dim_date(date_id),

                FOREIGN KEY (last_updated_date)
                    REFERENCES dim_date(date_id),

                FOREIGN KEY (sales_staff_id)
                    REFERENCES dim_staff(staff_id),

                FOREIGN KEY (counterparty_id)
                    REFERENCES dim_counterparty(counterparty_id),

                FOREIGN KEY (currency_id)
                    REFERENCES dim_currency(currency_id),

                FOREIGN KEY (design_id)
                    REFERENCES dim_design(design_id),

                FOREIGN KEY (agreed_payment_date)
                    REFERENCES dim_date(date_id),

                FOREIGN KEY (agreed_delivery_date)
                    REFERENCES dim_date(date_id),

                FOREIGN KEY (agreed_delivery_location_id)
                    REFERENCES dim_location(location_id)
            );
        """)

        connection.commit()

        print("All tables created successfully.")

    except Exception as error:
        connection.rollback()
        print(f"Error creating tables: {error}")
        raise

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":

    secret_name = "SECRET_NAME"

    secret = get_secret(secret_name)

    


