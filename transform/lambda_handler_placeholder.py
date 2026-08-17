import os

import pandas as pd
import s3fs


def lambda_handler(event, context):
    bucket = os.environ["INGEST_BUCKET"]

    df = pd.read_parquet(
        f"s3://{bucket}/raw/design"
    )

    return {
        "statusCode": 200,
        "rows": len(df),
        "columns": df.columns.tolist()
    }