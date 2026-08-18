import pandas as pd
import s3fs
import pycountry


def get_dataframe_from_s3(
    bucket: str,
    object_key: str,
) -> pd.DataFrame:
    """Read a Parquet file from S3 and return it as a pandas DataFrame."""
    fs = s3fs.S3FileSystem()

    return pd.read_parquet(
        f"s3://{bucket}/{object_key}",
        filesystem=fs,
    )


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