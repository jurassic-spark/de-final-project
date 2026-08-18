import pandas as pd
import os

import pandas as pd


def create_dim_date(start_date, end_date):

    """ this function create dim_date table 
       it takes the date range as start_date, end_date
       and returns df date 

    """
    # bucket name from CLI 
    bucket = os.environ['S3_INGESTION_BUCKET'] 

    dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D"
    )

    dim_date = pd.DataFrame({
        "date_id": dates,
        "year": dates.year,
        "month": dates.month,
        "day": dates.day,
        "day_of_week": dates.dayofweek + 1,
        "day_name": dates.day_name(),
        "month_name": dates.month_name(),
        "quarter": dates.quarter
    })

    

    dim_date.to_parquet(
    f"s3://{bucket}/date/dim_date/",
    index=False
)
    return dim_date


create_dim_date('2016-01-01',2035-12-31 )