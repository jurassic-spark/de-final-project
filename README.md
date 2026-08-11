# de-final-project
The intention is to create a data platform that extracts data from an operational database (and potentially other sources), archives it in a data lake, and makes it available in a remodelled OLAP data warehouse.


## Project structure

```text
.
├── data/
│   ├── raw_data/
│   ├── cleaned_data/
│   └── star_schema/
├── sql/
│   ├── schema.sql
│   ├── setup_db.sh
│   └── setup_test_db.sh
├── src/
│   ├── extract.py
│   ├── clean.py
│   ├── model.py
│   ├── load.py
│   └── pipeline.py
├── tests/
├── main.py
├── Makefile
└── requirements.txt
```