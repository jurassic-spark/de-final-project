import pandas as pd

# pd.set_option("display.max_columns", None)
# pd.set_option("display.width", None)

bucket = "js-final-proj-ingested-194169601943-dev"

df = pd.read_parquet(
    f"s3://{bucket}/raw/counterparty/"
)

print(df.head(20))

print(df.dtypes)

print (df.shape)
print(df.isna().sum())

def clean_counterparty_data(df):
    df = df.copy()
    df = df.drop_duplicates()
    df.columns = df.columns.str.strip()
    text_cols = [
        "counterparty_legal_name",
        "delivery_contact",
        "commercial_contact",
        "created_at",
        "last_updated"
        
    ]
    # stripping white space
    for col in text_cols:
        df[col] = df[col].str.strip()

    df = df.replace("", pd.NA)

    df = df.dropna(subset=["counterparty_id", "legal_address_id"])
    df = df.sort_values("last_updated")
    # drops rows if duplicate counterparty_id
    df = df.drop_duplicates(
        subset=["counterparty_id"],

        keep="last"

    )
    # row numbers are reset after dropping rows
    df = df.reset_index(drop=True)
    return df

cleaned_counterparty_df = clean_counterparty_data(df)

print(cleaned_counterparty_df.head(20))
print(cleaned_counterparty_df.shape)
print(cleaned_counterparty_df.isna().sum())


print("\nAfter cleaning:")
print(cleaned_counterparty_df.head(20))
print(cleaned_counterparty_df.shape)
print(cleaned_counterparty_df.isna().sum())






