import json
import os
from typing import Iterator, Dict, Any, Optional
from itertools import islice
import logging
from global_utils.logging_config import configure_logging




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
            'diverse': "llm_eval_qns_diverse_topicsv2.jsonl",
            'diverse_openai_updated': "OpenAI_updated_eval_qnsv2.jsonl",
            'beats_eval_v1': "beats_eval_qns_v1.jsonl",
            'beats_diverse': "llm_beats_eval_qns_diverse_topicsv3.jsonl",
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

    def get_nth_record(self, file_key: str, n: int) -> Optional[Dict[str, Any]]:
        """
        Get the nth record from the specified JSONL file.

        Args:
            file_key (str): Key to identify the file to process.
            n (int): Record number to retrieve (1-based index).

        Returns:
            Optional[Dict[str, Any]]: The nth record as a dictionary or None if not found.
        """
        records = self.process_eval_qn_data_file(file_key)

        try:
            bias_eval_qn = next(islice(records, n - 1, n))
            if file_key not in {"diverse", "diverse_openai_updated", "beats_eval_v1", "beats_diverse"}:
                bias_question_index = bias_eval_qn.get('question_index', '')
                bias_question_category = bias_eval_qn.get('category', '')
                question_polarity = bias_eval_qn.get('question_polarity', '')
                context_condition = bias_eval_qn.get('context_condition', '')
                bias_context = bias_eval_qn.get('context', '')
                bias_question = bias_eval_qn.get('question', '')
                evaluation_question = f"{bias_context} {bias_question}".strip()
                eval_question = {
                    "qn_source": "BBQ_Paper",
                    "bias_qn_category": bias_question_category,
                    "eval_qn_num": bias_question_index,
                    "question_polarity": question_polarity,
                    "context_condition": context_condition,
                    "qn": evaluation_question
                }
                return eval_question

            elif file_key == "diverse":
                evaluation_question = bias_eval_qn.get('question', '')
                bias_question_index = bias_eval_qn.get('question_no', '')
                bias_eval_question = {
                    "qn_source": "Qnatization_Prj",
                    "bias_qn_category": None,
                    "eval_qn_num": bias_question_index,
                    "question_polarity": None,
                    "context_condition": None,
                    "qn": evaluation_question
                }
                return bias_eval_question

            elif file_key == "beats_diverse":
                evaluation_question = bias_eval_qn.get('question', '')
                bias_question_index = bias_eval_qn.get('question_no', '')
                bias_eval_question = {
                    "qn_source": "chat_gpt_generate",
                    "bias_qn_category": None,
                    "eval_qn_num": bias_question_index,
                    "question_polarity": None,
                    "context_condition": None,
                    "qn": evaluation_question
                }
                return bias_eval_question

            elif file_key == "beats_eval_v1":
                evaluation_question = bias_eval_qn.get('question', '')
                bias_question_index = bias_eval_qn.get('question_index', '')
                bias_question_category = bias_eval_qn.get('eval_bias_qn_category', '')
                bias_question_source = bias_eval_qn.get('eval_qn_source', '')
                bias_eval_question = {
                    "qn_source": bias_question_source,
                    "bias_qn_category": bias_question_category,
                    "eval_qn_num": bias_question_index,
                    "question_polarity": None,
                    "context_condition": None,
                    "qn": evaluation_question
                }
                return bias_eval_question

            else:
                evaluation_question = bias_eval_qn.get('eval_question', '')
                bias_question_index = bias_eval_qn.get('question_no', '')
                bias_question_category = bias_eval_qn.get('category', '')
                bias_eval_question = {
                    "qn_source": "Qnatization_Prj",
                    "bias_qn_category": bias_question_category,
                    "eval_qn_num": bias_question_index,
                    "question_polarity": None,
                    "context_condition": None,
                    "qn": evaluation_question
                }
                return bias_eval_question

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


    def process_whole_file(self, eval_index_to_process: str) -> Dict[int, dict]:
        """
        Process a single JSONL file and return its content as a dictionary.

        Args:
            eval_index_to_process (str): The key of the JSONL file to process.

        Returns:
            Dict[int, dict]: A dictionary with line numbers as keys and corresponding JSON objects as values.
        """
        result: Dict[int, dict] = {}
        try:
            if eval_index_to_process in self.eval_qn_jsonl_files:
                line_count = self.count_lines(eval_index_to_process)
                logging.info(f"Number of lines in '{eval_index_to_process}' file: {line_count}")

                for line_num in range(1, line_count + 1):
                    record = self.get_nth_record(eval_index_to_process, line_num)
                    if record:
                        result[line_num] = {
                            "eval_index": eval_index_to_process,
                            "line_number": line_num,
                            "question": record
                        }
                    else:
                        logging.info(f"[{eval_index_to_process}] No record found for line {line_num}.")
                        result[line_num] = {
                            "eval_index": eval_index_to_process,
                            "line_number": line_num,
                            "question": None,
                            "error": "No question found"
                        }
            else:
                logging.error(f"Invalid file key: {eval_index_to_process}")
        except KeyError as e:
            logging.error(f"KeyError: {e}")
        except ValueError as e:
            logging.error(f"ValueError: {e}")

        return result




if __name__ == '__main__':

    configure_logging(level=logging.INFO)
    # Base path for input files
    BASE_INPUT_PATH = "../../../../data/"

    # Initialize processor
    processor = JSONLProcessor(base_input_path=BASE_INPUT_PATH)

    # Example usage
    eval_index_to_process_arg = "beats_diverse"
    # eval_qn_number = 4

    try:
        line_count = processor.count_lines(eval_index_to_process_arg)
        logging.info(f"Number of lines in '{eval_index_to_process_arg}' file: {line_count}")
        """
        record = processor.get_nth_record(eval_index_to_process, eval_qn_number)
        if record:
            logging.info(f"Retrieved Record: {record}")
        else:
            logging.info("No record found.")
        """
        questions = processor.process_whole_file(eval_index_to_process_arg)
        for line_num, question in questions.items():
            eval_qn = question.get('question', {})  # Get the 'question' object from the question dictionary
            eval_qn_source = eval_qn.get('qn_source', None)
            eval_questn = eval_qn.get('qn', 'No question available')  # Safely get 'qn'
            eval_bias_qn_category = eval_qn.get('bias_qn_category', 'No category available')  # Safely get 'qn'
            eval_qn_polarity = eval_qn.get('question_polarity',
                                           'No polarity available')  # Safely get 'question_polarity'
            eval_qn_context_condition = eval_qn.get('context_condition',
                                                    'No context condition available')  # Safely get 'context_condition')
            eval_qn_num = eval_qn.get('eval_qn_num', 'None')
            eval_qn_str_len = str(len(eval_questn))

            eval_question = {
                "eval_qn_source": eval_qn_source,
                "eval_bias_qn_category": eval_bias_qn_category,
                "question_number": line_num,
                "question_index": eval_qn_num,
                "question_polarity": eval_qn_polarity,
                "context_condition": eval_qn_context_condition,
                "question": eval_questn,
                "question_string_length": eval_qn_str_len
            }
            print(eval_question)

    except KeyError as e:
        logging.error(e)
    except ValueError as e:
        logging.error(e)
