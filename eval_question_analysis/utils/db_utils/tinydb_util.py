import json
import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from tinydb import TinyDB, Query
from tinydb.table import Table
from global_utils.logging_config import configure_logging


def initialize_database(db_path: str, table_name: str) -> Table:
    """
    Initialize the TinyDB database and get the specified table.

    Args:
        db_path (str): Path to the TinyDB database file.
        table_name (str): Name of the table to be created or accessed.

    Returns:
        Table: The TinyDB table object.
    """
    try:
        db = TinyDB(db_path)
        table = db.table(table_name)
        logging.info(f"Database initialized. DB: '{db_path}', Table: '{table_name}'")
        return table

    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise


def load_jsonl_to_database(jsonl_path: str, db_path: str, table_name: str) -> Optional[int]:
    """
    Load data from a JSONL file into the TinyDB database.

    Args:
        jsonl_path (str): Path to the JSONL file.
        db_path (str): Path to the TinyDB database file.
        table_name (str): Name of the table to insert data into.

    Returns:
        Optional[int]: The number of records successfully inserted, or None if an error occurs.
    """
    if not os.path.exists(jsonl_path):
        logging.error(f"JSONL file not found: {jsonl_path}")
        return None

    try:
        db = TinyDB(db_path)
        table = db.table(table_name)
        records_inserted = 0

        with open(jsonl_path, "r") as file:
            for line in file:
                try:
                    record = json.loads(line.strip())
                    # Insert record into the TinyDB table
                    table.insert(record)
                    records_inserted += 1

                except (ValueError, KeyError) as e:
                    logging.error(f"Error processing record: {e}")

        logging.info(f"Successfully inserted {records_inserted} records into table '{table_name}'.")
        return records_inserted

    except Exception as e:
        logging.error(f"Error loading data into database: {e}")
        return None


def query_database(db_path: str, table_name: str, query_field: str, query_value: Any) -> List[Dict]:
    """
    Query a TinyDB table and return the results as a list of dictionaries.

    Args:
        db_path (str): Path to the TinyDB database file.
        table_name (str): Name of the table to query.
        query_field (str): The field to query.
        query_value (Any): The value to query for.

    Returns:
        List[Dict]: Query results as a list of dictionaries.
    """
    try:
        db = TinyDB(db_path)
        table = db.table(table_name)
        query = Query()

        # Query the table
        results = table.search(query[query_field] == query_value)
        logging.info(
            f"Query executed on DB: '{db_path}', Table: '{table_name}', Field: '{query_field}', Value: '{query_value}'. Rows returned: {len(results)}"
        )

        return results

    except Exception as e:
        logging.error(f"Error querying database: {e}")
        raise


def clean_table(db_path: str, table_name: str):
    """
    Clean (empty) the specified table in the TinyDB database.

    Args:
        db_path (str): Path to the TinyDB database file.
        table_name (str): Name of the table to clean.

    Returns:
        None
    """
    try:
        db = TinyDB(db_path)
        table = db.table(table_name)
        table.truncate()  # Clears all records in the table
        logging.info(f"All rows from table '{table_name}' have been deleted.")

    except Exception as e:
        logging.error(f"Error cleaning table '{table_name}': {e}")
        raise


def main():
    try:
        # Paths to JSONL file and TinyDB database
        base_input_file_path = "../process_dataset/process_bbq_qns/"
        jsonl_path = "beats_updated_eval_qns_2024-12-22.jsonl"
        full_jsonl_file_path = os.path.join(base_input_file_path, jsonl_path)
        db_path = "eval_questions_tinydb.json"
        table_name = "beats_all_eval_questions"

        # Initialize database and table
        table = initialize_database(db_path, table_name)

        # Load the eval questions to the database
        load_jsonl_to_database(full_jsonl_file_path, db_path, table_name)

        # Clean the table
        # clean_table(db_path, table_name)

        # Query the database
        category = "political_bias"
        results = query_database(db_path, table_name, "eval_bias_qn_category", category)

        # Print results
        for result in results:
            print(result)

    except Exception as e:
        logging.error(e)
        raise


if __name__ == "__main__":
    try:
        configure_logging(level=logging.INFO)
        main()

    except Exception as e:
        logging.error(e)
