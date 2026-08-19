
import pandas as pd
from transform.transform_counterparty import clean_counterparty_data
from transform.transform_counterparty import clean_address_data
from transform.transform_counterparty import create_dim_counterparty

def test_clean_counterparty_data_removes_rows_where_counterparty_id_or_legal_address_id_is_missing():
    input_df = pd.DataFrame({
        "counterparty_id": [1, 2, None],
        "counterparty_legal_name": ["Company A", "Company B", "Company C"],
        "legal_address_id": [10, None, 30],
        "commercial_contact": ["Micheal Toy", "Melba Sanford", "Melba Sanford"],
        "delivery_contact": ["Mrs. Lucy Runolfsdottir", "Jean Hane III", "Jean Hane III"],
        "created_at": ["2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000"],
        "last_updated": ["2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000", "2022-11-03 14:20:51.563000"],
    })

    result = clean_counterparty_data(input_df)

    assert result["counterparty_id"].isna().sum() == 0
    assert result["legal_address_id"].isna().sum() == 0
    assert len(result) == 1
    assert result.loc[0, "counterparty_id"] == 1
    assert result.loc[0, "legal_address_id"] == 10

def test_clean_counterparty_data_strips_whitespace_and_lowercases():
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
    assert result.loc[0, "counterparty_legal_name"] == "company a"
    assert result.loc[0, "commercial_contact"] == "micheal toy"
    assert result.loc[0, "delivery_contact"] == "mrs. lucy runolfsdottir"
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
    assert result.loc[result["counterparty_id"] == 1, "counterparty_legal_name"].iloc[0] == "a new"


###### test cleaned address data 

def test_clean_address_data_strips_whitespace_and_lowercases_text_columns():
        input_df = pd.DataFrame({
        "address_id": [1],
        "address_line_1": [" 123 Main Street "],
        "address_line_2": [" Apartment 4 "],
        "district": [" Greater London "],
        "city": [" London "],
        "postal_code": [" SW1A 1AA "],
        "country": [" United Kingdom "],
        "phone": [" 01234567890 "],
    })

        result = clean_address_data(input_df)

        assert result.loc[0, "address_line_1"] == "123 main street"
        assert result.loc[0, "address_line_2"] == "apartment 4"
        assert result.loc[0, "district"] == "greater london"
        assert result.loc[0, "city"] == "london"
        assert result.loc[0, "postal_code"] == "sw1a 1aa"
        assert result.loc[0, "country"] == "united kingdom"
        assert result.loc[0, "phone"] == "01234567890"


def test_clean_address_data_replaces_empty_strings_with_na():
    input_df = pd.DataFrame({
        "address_id": [1],
        "address_line_1": [""],
        "address_line_2": [""],
        "district": [""],
        "city": [""],
        "postal_code": [""],
        "country": [""],
        "phone": [""],
    })

    result = clean_address_data(input_df)

    assert pd.isna(result.loc[0, "address_line_1"])
    assert pd.isna(result.loc[0, "address_line_2"])
    assert pd.isna(result.loc[0, "district"])
    assert pd.isna(result.loc[0, "city"])
    assert pd.isna(result.loc[0, "postal_code"])
    assert pd.isna(result.loc[0, "country"])
    assert pd.isna(result.loc[0, "phone"])


def test_clean_address_data_removes_rows_where_address_id_is_missing():
    input_df = pd.DataFrame({
        "address_id": [1, None],
        "address_line_1": ["123 Main Street", "456 Fake Street"],
        "address_line_2": ["Apt 1", "Apt 2"],
        "district": ["District A", "District B"],
        "city": ["London", "Manchester"],
        "postal_code": ["SW1A 1AA", "M1 1AE"],
        "country": ["United Kingdom", "United Kingdom"],
        "phone": ["111", "222"],
    })

    result = clean_address_data(input_df)

    assert result["address_id"].isna().sum() == 0
    assert len(result) == 1
    assert result.loc[0, "address_id"] == 1

def test_clean_address_data_removes_duplicate_address_ids_and_keeps_last():
    input_df = pd.DataFrame({
        "address_id": [1, 1, 2],
        "address_line_1": ["Old Address", "New Address", "Another Address"],
        "address_line_2": ["Old Line 2", "New Line 2", "Another Line 2"],
        "district": ["Old District", "New District", "Other District"],
        "city": ["Old City", "New City", "Other City"],
        "postal_code": ["OLD", "NEW", "OTHER"],
        "country": ["Old Country", "New Country", "Other Country"],
        "phone": ["111", "222", "333"],
    })

    result = clean_address_data(input_df)

    assert result["address_id"].duplicated().sum() == 0
    assert len(result) == 2

    row_for_address_1 = result[result["address_id"] == 1].iloc[0]
    assert row_for_address_1["address_line_1"] == "new address"
    assert row_for_address_1["phone"] == "222"


# tests the counterparty dataframe is merged with the address dataframe and returns correct columns for 
# dim_counterparty table (as shown in Data Warehouse diagram)


def test_create_dim_counterparty_merges_counterparty_with_address_and_renames_columns():
    cleaned_counterparty_df = pd.DataFrame({
        "counterparty_id": [1],
        "counterparty_legal_name": ["company a"],
        "legal_address_id": [10],
        "commercial_contact": ["micheal toy"],
        "delivery_contact": ["mrs. lucy runolfsdottir"],
        "created_at": ["2022-11-03 14:20:51.563000"],
        "last_updated": ["2022-11-03 14:20:51.563000"],
    })

    cleaned_address_df = pd.DataFrame({
        "address_id": [10],
        "address_line_1": ["123 main street"],
        "address_line_2": ["apt 4"],
        "district": ["greater london"],
        "city": ["london"],
        "postal_code": ["sw1a 1aa"],
        "country": ["united kingdom"],
        "phone": ["01234567890"],
    })

    result = create_dim_counterparty(
        cleaned_counterparty_df,
        cleaned_address_df,
    )

    expected_columns = [
        "counterparty_id",
        "counterparty_legal_name",
        "counterparty_legal_address_line_1",
        "counterparty_legal_address_line_2",
        "counterparty_legal_district",
        "counterparty_legal_city",
        "counterparty_legal_postal_code",
        "counterparty_legal_country",
        "counterparty_legal_phone_number",
    ]

    assert list(result.columns) == expected_columns
    assert len(result) == 1
    assert result.loc[0, "counterparty_id"] == 1
    assert result.loc[0, "counterparty_legal_name"] == "company a"
    assert result.loc[0, "counterparty_legal_address_line_1"] == "123 main street"
    assert result.loc[0, "counterparty_legal_city"] == "london"
    assert result.loc[0, "counterparty_legal_phone_number"] == "01234567890"