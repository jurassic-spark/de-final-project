import pandas as pd
import fsspec 
import s3fs
from transform.read_table import read_table




def transformed_design(table):
    # read the table
    df = read_table(table)

    # drop unwanted columns
    df = df.drop(
    columns=['created_at','last_updated']
    )
    # drop duplicate
    df = df.drop_duplicates(
    subset='design_id',
    keep='last'
    )
    print(df.head())


transformed_design('design')