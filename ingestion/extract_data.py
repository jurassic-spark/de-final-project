from src.utils import get_secret
import psycopg2
from psycopg2 import sql
import pandas as pd




def extract_data(secrets, table_name, timestamp):
    username = secrets["username"]
    password = secrets["password"]
    db_name = secrets["dbname"]
    host = secrets["host"]
    port = secrets["port"]
    connection = psycopg2.connect(user=username, password=password, dbname=db_name, host=host, port=port)
    query = f"SELECT * FROM {table_name} WHERE last_updated > %s;"
    dataframe = pd.read_sql(query, connection, params=[timestamp])
    print("dataframe:", table_name)
    return dataframe

    












    



