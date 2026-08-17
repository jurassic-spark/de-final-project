import pandas as pd
import fsspec
import s3fs
import os




def read_table(table):
    bucket = os.environ['S3_INGESTION_BUCKET'] # export s3 name in CLI
    df = pd.read_parquet(
        f's3://{bucket}/raw/{table}')
    print(df.head())
    return df
 

    