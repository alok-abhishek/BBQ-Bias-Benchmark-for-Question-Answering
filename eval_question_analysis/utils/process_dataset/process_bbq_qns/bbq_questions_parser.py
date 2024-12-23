from eval_question_analysis.utils.process_dataset.json.read_eval_qns_jsonl import JSONLProcessor
import json
import logging
from collections import OrderedDict

from global_utils.logging_config import configure_logging

if __name__ == '__main__':

    configure_logging(level=logging.INFO)
    # Base path for input files
    BASE_INPUT_PATH = "../../../../data/"

    # Initialize processor
    processor = JSONLProcessor(base_input_path=BASE_INPUT_PATH)

    # Example usage
    eval_index_to_process = "gender"
    # eval_qn_number = 4

    try:
        line_count = processor.count_lines(eval_index_to_process)
        logging.info(f"Number of lines in '{eval_index_to_process}' file: {line_count}")
        """
        record = processor.get_nth_record(eval_index_to_process, eval_qn_number)
        if record:
            logging.info(f"Retrieved Record: {record}")
        else:
            logging.info("No record found.")
        """
        questions = processor.process_whole_file(eval_index_to_process)
        for line_num, question in questions.items():
            eval_qn = question.get('question', {})  # Get the 'question' object from the question dictionary
            eval_questn = eval_qn.get('qn', 'No question available')  # Safely get 'qn'
            eval_bias_qn_category = eval_qn.get('bias_qn_category', 'No question available')  # Safely get 'qn'
            eval_qn_polarity = eval_qn.get('question_polarity','No polarity available')  # Safely get 'question_polarity'
            eval_qn_context_condition = eval_qn.get('context_condition','No context condition available')  # Safely get 'context_condition')
            eval_qn_num = eval_qn.get('eval_qn_num','None')
            eval_qn_str_len = str(len(eval_questn))

            eval_question = {
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

