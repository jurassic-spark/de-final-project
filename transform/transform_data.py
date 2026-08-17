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


def get_currency_name(currency_code: str) -> str | None:
    """Return the ISO currency name for a three-letter currency code."""
    currency = pycountry.currencies.get(alpha_3=currency_code)

    if currency is None:
        return None

    return currency.name


def transform_currency(df):
    cleaned_df = df.copy()

    # Keep only the columns required by dim_currency.
    cleaned_df = cleaned_df[
        [
            "currency_id",
            "currency_code",
        ]
    ]

    # Raise an error if any currency code is missing or empty.
    if (cleaned_df["currency_code"].isna() | cleaned_df["currency_code"].eq("")).any():
        raise ValueError("currency_code cannot be missing")

    # Add the full ISO currency name.
    cleaned_df["currency_name"] = cleaned_df["currency_code"].apply(get_currency_name)

    return cleaned_df
