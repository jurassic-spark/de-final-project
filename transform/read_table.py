import pandas as pd
import fsspec
import s3fs
import os




def read_tables_from_s3(table, bucket):
    df = pd.read_parquet(
        f's3://{bucket}/raw/{table}')
    print(df.head())
    return df
 

    