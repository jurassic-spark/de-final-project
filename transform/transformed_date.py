import pandas as pd
import fsspec 
import s3fs
from transform.read_table import read_table




def transformed_date(table):
    # read the data
    df = read_table(table)
    print(df.head())



transformed_date('address')