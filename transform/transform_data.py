import pandas as pd
import s3fs
import pycountry
from transform.read_table import read_tables_from_s3
import numpy as np

def get_dataframe_from_s3(
    bucket: str,
    object_key: str,
) -> pd.DataFrame:
    """Read a Parquet file from S3 and return it as a pandas DataFrame."""
    fs = s3fs.S3FileSystem()
    s3_path = f"s3://{bucket}/{object_key}"
    try:
        return pd.read_parquet(
            f"s3://{bucket}/{object_key}",
            filesystem=fs,
        )
    except Exception as error:
        raise RuntimeError(
            f"Failed to read parquet data from {s3_path}"
        ) from error


def get_currency_name(currency_code: str) -> str:
    """Return the ISO currency name for a three-letter currency code."""
    currency = pycountry.currencies.get(alpha_3=currency_code)

    if currency is None:
        raise ValueError(
            f"{currency_code!r} is not a recognised currency code"
        )

    return currency.name


def transform_currency(df: pd.DataFrame) -> pd.DataFrame:
    """Transform source currency data into the dim_currency format.

    Standardises and validates currency codes, adds currency names,
    rejects missing values, and removes duplicate currencies.
    """
    cleaned_df = df.copy()

    cleaned_df = cleaned_df[
        [
            "currency_id",
            "currency_code",
        ]
    ]

    # Remove surrounding whitespace and standardise codes to uppercase.
    cleaned_df["currency_code"] = (
        cleaned_df["currency_code"]
        .str.strip()
        .str.upper()
    )

    # Check for missing/empty values before pycountry lookup.
    if (
        cleaned_df["currency_code"].isna()
        | cleaned_df["currency_code"].eq("")
    ).any():
        raise ValueError("currency_code cannot be missing")

    # get_currency_name will raise ValueError for invalid codes.
    cleaned_df["currency_name"] = cleaned_df["currency_code"].apply(
        get_currency_name
    )

    cleaned_df = cleaned_df.drop_duplicates(
        subset=["currency_code"],
        keep= "first",
    )

    return cleaned_df

def transform_staff(s_df, d_df):
    """Transforms raw staff data into the dim_staff format using supplementary department data.
    Drops rows with duplicate staff and department ids and merges raw staff and department tables.
    Any rows with missing data are dropped and column order is corrected.
    """
    # drop rows with duplicate staff ids and drop created_at and last_updated column from staff
    staff_df = s_df.drop_duplicates(subset="staff_id", keep="last").drop(columns=['created_at', 'last_updated'])

    # drop rows with duplicate department ids and drop created_at and last_updated column from department
    department_df = d_df.drop_duplicates(subset="department_id", keep="last").drop(columns=['manager', 'created_at', 'last_updated'])

    # merge staff and department dfs and drop department_id column
    combined_df = pd.merge(staff_df, department_df, how="left", on=["department_id", "department_id"]).drop(columns=['department_id'])

    # remove rows with missing data
    cleaned_df = combined_df.replace(["NaN", "nan", "None", ""], np.nan).dropna()

    column_order = ['staff_id', 'first_name', 'last_name', 'department_name', 'location', 'email_address']
    cleaned_df = cleaned_df[column_order]

    return cleaned_df

def transform_location(df):
    """Transforms raw address data into the dim_location format.
    Drops rows with duplicate address ids, removes created_at and last_updated columns,
    and changes the "address_id" column to "location_id".
    Any rows with missing data are dropped.
    """
     # drop rows with duplicate address ids
    cleaned_df = df.drop_duplicates(subset="address_id", keep="last")

    # drop created_at and last_updated column
    cleaned_df = cleaned_df.drop(columns=['created_at', 'last_updated'])

    # rename "address_id" column to "location_id"
    cleaned_df = cleaned_df.rename(columns={'address_id': 'location_id'})

    # remove rows with missing data, except for address_line_2 and district columns
    cleaned_df = cleaned_df.replace(["NaN", "nan", "None", ""], np.nan).dropna(subset=["location_id", "address_line_1", "city", "postal_code", "country", "phone"])

    return cleaned_df







def clean_counterparty_data(df) -> pd.DataFrame:
    """Clean counterparty data."""
    df = df.copy()
    df = df.drop_duplicates()
    df.columns = df.columns.str.strip()

    text_cols = [
        "counterparty_legal_name",
        "delivery_contact",
        "commercial_contact",
        "last_updated",
        "created_at",
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().str.lower()

    df = df.replace("", pd.NA)
    df = df.dropna(subset=["counterparty_id", "legal_address_id"])

    df = df.drop_duplicates(
        subset=["counterparty_id"],
        keep="last",
    )

    df = df.reset_index(drop=True)

    return df


def clean_address_data(df) -> pd.DataFrame:
    """Clean address data."""
    address_df = df.copy()
    address_df = address_df.drop_duplicates()
    address_df.columns = address_df.columns.str.strip()

    text_cols = [
        "address_line_1",
        "address_line_2",
        "district",
        "city",
        "postal_code",
        "country",
    ]

    for col in text_cols:
        if col in address_df.columns:
            address_df[col] = (
                address_df[col]
                .astype("string")
                .str.strip()
                .str.lower()
            )

    if "phone" in address_df.columns:
        address_df["phone"] = address_df["phone"].astype("string").str.strip()

    address_df = address_df.replace("", pd.NA)
    address_df = address_df.dropna(subset=["address_id"])

    address_df = address_df.drop_duplicates(
        subset=["address_id"],
        keep="last",
    )

    address_df = address_df.reset_index(drop=True)

    return address_df


def create_dim_counterparty(
    cleaned_counterparty_df: pd.DataFrame,
    cleaned_address_df: pd.DataFrame,
) -> pd.DataFrame:
    """Create dim_counterparty by joining counterparty and address data."""

    dim_counterparty_df = cleaned_counterparty_df.merge(
        cleaned_address_df,
        how="left",
        left_on="legal_address_id",
        right_on="address_id",
    )

    dim_counterparty_df = dim_counterparty_df[
        [
            "counterparty_id",
            "counterparty_legal_name",
            "address_line_1",
            "address_line_2",
            "district",
            "city",
            "postal_code",
            "country",
            "phone",
        ]
    ].rename(columns={
        "address_line_1": "counterparty_legal_address_line_1",
        "address_line_2": "counterparty_legal_address_line_2",
        "district": "counterparty_legal_district",
        "city": "counterparty_legal_city",
        "postal_code": "counterparty_legal_postal_code",
        "country": "counterparty_legal_country",
        "phone": "counterparty_legal_phone_number",
    })

    return dim_counterparty_df


def transform_counterparty() -> pd.DataFrame:
    """Read, clean, and transform counterparty data."""

    counterparty_df = read_tables_from_s3("counterparty")
    address_df = read_tables_from_s3("address")

    cleaned_counterparty_df = clean_counterparty_data(counterparty_df)
    cleaned_address_df = clean_address_data(address_df)

    dim_counterparty_df = create_dim_counterparty(
        cleaned_counterparty_df,
        cleaned_address_df,
    )

    return dim_counterparty_df

def transform_sales(df):
    """Transforms raw sales data into the fact_sales format.
    Splits both the created_at and last_updated columns into two columns for date and time.
  
    """
    # remove duplicates
    df.drop_duplicates(inplace=True)

    # add sales_record_id column
    df.insert(0, "sales_record_id", range(1, len(df) + 1))

    # split created_at into two separate date and time columns
    df['created_date'] = pd.to_datetime(df['created_at'], format="mixed").dt.date
    df['created_time'] = pd.to_datetime(df['created_at'], format="mixed").dt.time

    # split last_updated into two separate date and time columns
    df['last_updated_date'] = pd.to_datetime(df['last_updated'], format="mixed").dt.date
    df['last_updated_time'] = pd.to_datetime(df['last_updated'], format="mixed").dt.time

    # drop redundant created_at and last_updated columns
    cleaned_df = df.drop(columns=['created_at', 'last_updated'])

    # change agreed_delivery_date and agreed_delivery_date column types to datetime
    cleaned_df['agreed_delivery_date'] = pd.to_datetime(cleaned_df['agreed_delivery_date'])
    cleaned_df['agreed_delivery_date'] = pd.to_datetime(cleaned_df['agreed_payment_date'])

    # rename staff_id column
    cleaned_df = cleaned_df.rename(columns={'staff_id': 'sales_staff_id'})

    # remove rows with missing data
    cleaned_df = cleaned_df.replace(["NaN", "nan", "None", ""], np.nan).dropna()

    # correct column order
    column_order = ["sales_record_id", "sales_order_id", "created_date", 
        "created_time", "last_updated_date", "last_updated_time", "sales_staff_id", 
        "counterparty_id", "units_sold", "unit_price", "currency_id", "design_id",
        "agreed_payment_date", "agreed_delivery_date", "agreed_delivery_location_id" 
        ]
    cleaned_df = cleaned_df[column_order]
    
    return cleaned_df




