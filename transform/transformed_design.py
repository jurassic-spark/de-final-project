import pandas as pd
import fsspec
import s3fs


def transformed_design():

    bucket = "js-final-proj-ingested-194169601943-dev"
    df = pd.read_parquet(
        f"s3://{bucket}"
    )

    df = df.drop(
        columns=['created_at', 'last_updated']
    )

    df = df.drop_duplicates(
        subset='design_id',
        keep='last'
    )
    print(df.head())


transformed_design()
