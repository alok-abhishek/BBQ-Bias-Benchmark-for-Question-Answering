import json
import os
from typing import Iterator, Dict, Any, Optional
from itertools import islice
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class JSONLProcessor:
    def __init__(self, base_input_path: str):
        """Initialize JSONLProcessor with a base path for input files."""
        self.base_input_path = base_input_path
        self.eval_qn_jsonl_files = {
            'age': 'Age.jsonl',
            'disability': 'Disability_status.jsonl',
            'gender': 'Gender_identity.jsonl',
            'nationality': 'Nationality.jsonl',
            'physical': 'Physical_appearance.jsonl',
            'race': 'Race_ethnicity.jsonl',
            'race_gender': 'Race_x_gender.jsonl',
            'race_ses': 'Race_x_SES.jsonl',
            'religion': 'Religion.jsonl',
            'ses': 'SES.jsonl',
            'orientation': 'Sexual_orientation.jsonl',
            'diverse': "llm_eval_qns_diverse_topicsv2.jsonl"
        }

    def read_jsonl_file(self, file_path: str) -> Iterator[Dict[str, Any]]:
        """
        Read a JSONL file with robust error handling and logging.

        Args:
            file_path: Path to the JSONL file

        Yields:
            Dictionary representing each JSON record
        """
        encodings = ['utf-8-sig', 'utf-16', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    for line_num, line in enumerate(file, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError as e:
                            logging.warning(f"Error parsing line {line_num}: {e}")
                            logging.debug(f"Problematic line: {line}")
                            continue
                return  # Exit once successful
            except UnicodeDecodeError:
                logging.warning(f"Failed to decode file with encoding: {encoding}")
                continue

        raise ValueError(f"Could not decode file {file_path} with any supported encoding")

    def get_file_path(self, key: str) -> str:
        """Get the full file path for a given key."""
        if key not in self.eval_qn_jsonl_files:
            raise KeyError(f"Invalid key '{key}'. Valid options are: {list(self.eval_qn_jsonl_files.keys())}")
        return os.path.join(self.base_input_path, self.eval_qn_jsonl_files[key])

    def process_eval_qn_data_file(self, file_key: str) -> Iterator[Dict[str, Any]]:
        """
        Process an evaluation question data file.

        Args:
            file_key: Key to identify the file to process

        Returns:
            Iterator of parsed JSON records
        """
        file_path = self.get_file_path(file_key)
        return self.read_jsonl_file(file_path)

    def get_nth_record(self, file_key: str, n: int) -> Optional[str]:
        """
        Get the nth record from the specified JSONL file.

        Args:
            file_key: Key to identify the file to process
            n: Record number to retrieve (1-based index)

        Returns:
            Combined context and question as a single string, or None if not found
        """
        records = self.process_eval_qn_data_file(file_key)

        try:
            eval_qn = next(islice(records, n - 1, n))
            if file_key != "diverse":
                context = eval_qn.get('context', '')
                question = eval_qn.get('question', '')
                return f"{context} {question}".strip()
            else:
                question = eval_qn.get('question', '')
                return f"{question}".strip()

        except StopIteration:
            logging.error(f"Record number {n} not found in file '{file_key}'")
            return None

    def count_lines(self, file_key: str) -> int:
        """
        Count the number of lines in a JSONL file.

        Args:
            file_key: Key to identify the file to process

        Returns:
            Number of lines in the file
        """
        file_path = self.get_file_path(file_key)
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                return sum(1 for _ in file)
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            return 0
        except Exception as e:
            logging.error(f"Error counting lines in file '{file_key}': {e}")
            return 0

if __name__ == '__main__':
    # Base path for input files
    BASE_INPUT_PATH = "../../../../data/"

    # Initialize processor
    processor = JSONLProcessor(base_input_path=BASE_INPUT_PATH)

    # Example usage
    eval_index_to_process = "diverse"
    eval_qn_number = 4

    try:
        line_count = processor.count_lines(eval_index_to_process)
        logging.info(f"Number of lines in '{eval_index_to_process}' file: {line_count}")
        record = processor.get_nth_record(eval_index_to_process, eval_qn_number)
        if record:
            logging.info(f"Retrieved Record: {record}")
        else:
            logging.info("No record found.")
    except KeyError as e:
        logging.error(e)
    except ValueError as e:
        logging.error(e)
