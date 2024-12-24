import sqlite3
import json
import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from global_utils.logging_config import configure_logging


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    """
    Check if a table exists in the SQLite database.

    Args:
        connection (sqlite3.Connection): SQLite database connection.
        table_name (str): Name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,)
        )
        return cursor.fetchone() is not None

    except Exception as e:
        logging.error(e)
        raise


def initialize_database(db_path: str, table_name: str) -> sqlite3.Connection:
    """
    Initialize the SQLite database by creating the required table if it doesn't exist.

    Args:
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to be created.

    Returns:
        sqlite3.Connection: Database connection for reuse.
    """
    try:
        connection = sqlite3.connect(db_path)

        if not table_exists(connection, table_name):
            cursor = connection.cursor()
            cursor.execute(
                f"""
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    eval_qn_source TEXT,
                    eval_bias_qn_category TEXT,
                    question_number INTEGER,
                    question_index INTEGER,
                    question_polarity TEXT,
                    context_condition TEXT,
                    question TEXT,
                    question_string_length INTEGER
                )
                """
            )
            connection.commit()
            logging.info(f"Table '{table_name}' created.")
        else:
            logging.info(f"Table '{table_name}' already exists.")

        logging.info(f"Database Initialized. DB: '{db_path}' Table: {table_name}")
        return connection

    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise



def load_jsonl_to_database(jsonl_path: str, db_path: str, table_name: str) -> Optional[int]:
    """
    Load data from a JSONL file into the SQLite database.

    Args:
        jsonl_path (str): Path to the JSONL file.
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to insert data into.

    Returns:
        Optional[int]: The number of records successfully inserted, or None if an error occurs.
    """
    if not os.path.exists(jsonl_path):
        logging.error(f"JSONL file not found: {jsonl_path}")
        return None

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        records_inserted = 0

        with open(jsonl_path, "r") as file:
            for line in file:
                try:
                    record = json.loads(line.strip())

                    # Convert fields to integers, using 0 as a fallback for empty strings or missing values
                    question_number = int(record.get("question_number", 0) or 0)
                    question_index = int(record.get("question_index", 0) or 0)
                    question_string_length = int(record.get("question_string_length", 0) or 0)


                    # Insert record into the database
                    cursor.execute(
                        f"""
                        INSERT INTO {table_name} (
                            eval_qn_source,
                            eval_bias_qn_category,
                            question_number,
                            question_index,
                            question_polarity,
                            context_condition,
                            question,
                            question_string_length
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            record.get("eval_qn_source"),
                            record.get("eval_bias_qn_category"),
                            question_number,
                            question_index,
                            record.get("question_polarity"),
                            record.get("context_condition"),
                            record.get("question"),
                            question_string_length,
                        )
                    )
                    records_inserted += 1

                except (ValueError, KeyError) as e:
                    logging.error(f"Error processing record: {e}")

        connection.commit()
        logging.info(f"Successfully inserted {records_inserted} records into table '{table_name}'.")
        return records_inserted

    except Exception as e:
        logging.error(f"Error loading data into database: {e}")
        return None

    finally:
        connection.close()

def query_database(db_path: str, table_name: str, query_field: str, query_value: str) -> List[Dict]:
    """
    Query a SQLite database table and return the results as a list of dictionaries.

    Args:
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to query.
        query_field (str): The field to query.
        query_value (str): The value to query for.

    Returns:
        List[Dict]: Query results as a list of dictionaries.

    Raises:
        ValueError: If the query fails or the table/query field is invalid.
    """
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
        cursor = connection.cursor()

        # Validate inputs to avoid SQL injection and improper table/field references
        if not table_name.isidentifier():
            raise ValueError(f"Invalid table name: {table_name}")
        if not query_field.isidentifier():
            raise ValueError(f"Invalid query field: {query_field}")

        # Construct and execute the query
        query = f"SELECT * FROM {table_name} WHERE {query_field} = ?"
        cursor.execute(query, (query_value,))
        rows = cursor.fetchall()

        row_count = len(rows)  # Count the number of rows returned
        logging.info(
            f"Query executed successfully on DB: '{db_path}', Table: '{table_name}', Field: '{query_field}', Value: '{query_value}'. Rows returned: {row_count}"
        )

        return [dict(row) for row in rows]

    except sqlite3.OperationalError as oe:
        logging.error(f"SQLite OperationalError: {oe}")
        raise ValueError(f"Database operation failed: {oe}")
    except sqlite3.Error as se:
        logging.error(f"SQLite Error: {se}")
        raise ValueError(f"SQLite error occurred: {se}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise ValueError(f"An unexpected error occurred: {e}")
    finally:
        if connection:
            connection.close()
            logging.info(f"Database connection to '{db_path}' closed.")


def execute_query(db_path: str, table_name: str, query_string: str, params: Optional[tuple] = None) -> List[Dict]:
    """
    Execute a query on the SQLite database and return the results.

    Args:
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to query.
        query_string (str): SQL query to execute.
        params (Optional[tuple]): Parameters to pass into the query.

    Returns:
        List[Dict]: Query results as a list of dictionaries.
    """
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
        cursor = connection.cursor()

        if not table_name.isidentifier():
            raise ValueError(f"Invalid table name: {table_name}")

        cursor.execute(query_string, params or ())
        rows = cursor.fetchall()

        row_count = len(rows)  # Count the number of rows returned
        logging.info(
            f"Query executed: {query_string} with params: {params} on DB: '{db_path}', Table: '{table_name}'. Rows returned: {row_count}"
        )
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        logging.error(f"SQLite Error: {e}")
        raise ValueError(f"An error occurred: {e}")
    finally:
        connection.close()


def clean_table(db_path: str, table_name: str, reset_auto_increment: bool = False):
    """
    Clean (empty) the specified table in the SQLite database and optionally reset the auto-increment counter.

    Args:
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to clean.
        reset_auto_increment (bool): Whether to reset the auto-increment counter.

    Returns:
        None
    """
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Check if the table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,)
        )
        if cursor.fetchone() is None:
            logging.error(f"Table '{table_name}' does not exist in the database.")
            return

        # Delete all rows from the table
        cursor.execute(f"DELETE FROM {table_name};")
        logging.info(f"All rows from table '{table_name}' have been deleted.")

        # Optionally reset the auto-increment counter
        if reset_auto_increment:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name=?;", (table_name,))
            logging.info(f"Auto-increment counter for table '{table_name}' has been reset.")

        connection.commit()

    except sqlite3.Error as e:
        logging.error(f"Error cleaning table '{table_name}': {e}")
        raise

    finally:
        if connection:
            connection.close()
            logging.info(f"Database connection to '{db_path}' closed.")

def main():
    try:
        # Paths to JSONL file and SQLite database
        base_input_file_path = "../process_dataset/process_bbq_qns/"
        jsonl_path = "beats_updated_eval_qns_2024-12-22.jsonl"
        full_jsonl_file_path = os.path.join(base_input_file_path, jsonl_path)
        db_path = "eval_questions_sqlite.db"
        table_name = "beats_all_eval_questions"

        # Initialize database and table (only creates the table if it doesn't exist)
        connection = initialize_database(db_path, table_name)

        # load the eval questions to the database:
        # load_jsonl_to_database(full_jsonl_file_path, db_path, table_name)

        # Clean the table and reset the auto-increment counter
        # clean_table(db_path, table_name, reset_auto_increment=True)

        # Example query to retrieve data from the custom table
        query1 = f"SELECT * FROM <table_name> WHERE eval_bias_qn_category = ?"
        category = "political_bias"
        # results = query_database(db_path, table_name, "eval_bias_qn_category", category)
        query2 = f"SELECT * FROM <table_name> WHERE eval_bias_qn_category = ? AND question_polarity = ?"

        query3 = f"""
        SELECT 
            eval_qn_source,
            eval_bias_qn_category,
            question_index,
            question,
            question_string_length
        FROM (
            SELECT 
                eval_qn_source,
                eval_bias_qn_category,
                question_index,
                question,
                question_string_length,
                ROW_NUMBER() OVER (
                    PARTITION BY eval_bias_qn_category, question_index 
                    ORDER BY question_string_length DESC
                ) AS rank
            FROM 
                {table_name}
            WHERE 
                question_polarity = ? AND 
                context_condition = ?
        )
        WHERE rank = 1;
        """

        params3 = ('nonneg', 'ambig')

        query4 = f"""
        SELECT 
            eval_qn_source,
            eval_bias_qn_category,
            question_index,
            question,
            question_string_length
        FROM
            {table_name}
        WHERE 
            eval_qn_source = ? 
        ;
        """


        params4 = ('Qnatization_Prj',)

        results1 = execute_query(db_path, table_name, query3, params3)
        results2 = execute_query(db_path, table_name, query4, params4)

        # Generate output file name with year and date
        current_date = datetime.now().strftime("%Y-%m-%d")
        base_output_file_path = "../process_dataset/process_bbq_qns/"
        jsonl_output_path = f"beats_eval_qns_{current_date}.jsonl"
        full_jsonl_file_output_path = os.path.join(base_output_file_path, jsonl_output_path)

        # Print and save results
        with open(full_jsonl_file_output_path, "a") as file:
            for result in results1:
                file.write(json.dumps(result) + "\n")
                print(result)
            for result in results2:
                file.write(json.dumps(result) + "\n")
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
