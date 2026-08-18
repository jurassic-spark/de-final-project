
import pandas as pd
from transform.transform_counterparty import clean_counterparty_data
def test_clean_counterparty_data_removes_rows_where_counterparty_id_and_legal_address_id_is_missing():
    input_df = pd.DataFrame({
        "counterparty_id": [1, 2, None],
        "counterparty_legal_name": ["Company A", "Company B", "Company C"],
        "legal_address_id": [10, None, 30],
        "commercial_contact": ["Micheal Toy", "Melba Sanford", "Melba Sanford"],
        "delivery_contact":["Mrs. Lucy Runolfsdottir", "Jean Hane III", "Jean Hane III"],
        "created_at": ["2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000"],
        "last_updated": ["2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000"]
        })

    result = clean_counterparty_data(input_df)
    assert result["counterparty_id"].isna().sum() == 0
    assert result["legal_address_id"].isna().sum() == 0
    assert len(result) == 1

def test_clean_counterparty_data_strips_whitespace():
    input_df = pd.DataFrame({
    "counterparty_id": [1],
    "counterparty_legal_name": [" Company A "],
    "legal_address_id": [10],
    "commercial_contact": [" Micheal Toy "],
    "delivery_contact":[" Mrs. Lucy Runolfsdottir "],
    "created_at": ["  2022-11-03 14:20:51.563000"],
    "last_updated": ["  2022-11-03 14:20:51.563000"]
    })

    result = clean_counterparty_data(input_df)
    assert result.loc[0, "counterparty_legal_name"] == "Company A"
    assert result.loc[0, "commercial_contact"] == "Micheal Toy"
    assert result.loc[0, "delivery_contact"] == "Mrs. Lucy Runolfsdottir"
    assert result.loc[0, "created_at"] == "2022-11-03 14:20:51.563000"
    assert result.loc[0, "last_updated"] == "2022-11-03 14:20:51.563000"

def test_clean_counterparty_data_replaces_empty_strings_with_na():
    input_df = pd.DataFrame({
        "counterparty_id": [1],
        "counterparty_legal_name": [""],
        "legal_address_id": [10],
        "commercial_contact":[""],
        "delivery_contact": [""],
        "created_at": ["2022-11-03 14:20:51.563000"],
        "last_updated": ["2022-11-03 14:20:51.563000"]
            
            
    })

    result = clean_counterparty_data(input_df)

    assert pd.isna(result.loc[0, "counterparty_legal_name"])
    assert pd.isna(result.loc[0, "commercial_contact"])
    assert pd.isna(result.loc[0, "delivery_contact"])


def test_clean_counterparty_data_removes_duplicate_counterparty_ids():
    input_df = pd.DataFrame({
        "counterparty_id": [1, 1, 2],
        "counterparty_legal_name": ["A Old", "A New", "B"],
        "legal_address_id": [10, 10, 20],
        "commercial_contact": ["Mrs. Lucy Runolfsdottir", "Jean Hane III", "Jean Hane III"],
        "delivery_contact": ["Mrs. Lucy Runolfsdottir", "Jean Hane III", "Jean Hane III"],
        "created_at": ["2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000"],
        "last_updated": ["2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000"]
    })

    result = clean_counterparty_data(input_df)

    assert result["counterparty_id"].duplicated().sum() == 0
    assert len(result) == 2




