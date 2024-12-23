from eval_question_analysis.utils.process_dataset.json.read_eval_qns_jsonl import JSONLProcessor
import json
import logging
from collections import OrderedDict
from typing import Iterator, Dict, Any, Optional
from datetime import datetime
from global_utils.logging_config import configure_logging



if __name__ == '__main__':

    configure_logging(level=logging.INFO)
    # Base path for input files
    BASE_INPUT_PATH = "../../../../data/"

    # Initialize processor
    processor = JSONLProcessor(base_input_path=BASE_INPUT_PATH)

    # Generate output file name with year and date
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_file_path = f"beats_updated_eval_qns_{current_date}.jsonl"

    try:
        # Ensure the output file is empty before appending
        with open(output_file_path, "w") as file:
            pass

        eval_indexes_to_process = processor.eval_qn_jsonl_files.keys()

        for eval_index in eval_indexes_to_process:
            if eval_index != "diverse":
                try:
                    line_count = processor.count_lines(eval_index)
                    questions = processor.process_whole_file(eval_index)
                    eval_questions = []
                    for line_num, question in questions.items():
                        eval_qn = question.get('question', {})  # Get the 'question' object from the question dictionary
                        eval_qn_source = eval_qn.get('qn_source', None) # Get the 'question source' from the question dictionary
                        eval_questn = eval_qn.get('qn', 'No question available')  # Safely get 'qn'
                        eval_bias_qn_category = eval_qn.get('bias_qn_category', 'No category available')  # Safely get 'qn'
                        eval_qn_polarity = eval_qn.get('question_polarity','No polarity available')  # Safely get 'question_polarity'
                        eval_qn_context_condition = eval_qn.get('context_condition','No context condition available')  # Safely get 'context_condition')
                        eval_qn_num = eval_qn.get('eval_qn_num','None')
                        eval_qn_str_len = str(len(eval_questn))

                        eval_question = {
                            "eval_qn_source": eval_qn_source,
                            "eval_bias_qn_category": eval_bias_qn_category,
                            "question_number": str(line_num),
                            "question_index": eval_qn_num,
                            "question_polarity": eval_qn_polarity,
                            "context_condition": eval_qn_context_condition,
                            "question": eval_questn,
                            "question_string_length": eval_qn_str_len
                        }

                        eval_questions.append(eval_question)

                    # Write to the output file in bulk
                    with open(output_file_path, "a") as file:
                        for eval_question in eval_questions:
                            file.write(json.dumps(eval_question) + "\n")

                except KeyError as e:
                    logging.error(e)

                except ValueError as e:
                    logging.error(e)

                except Exception as e:
                    logging.error(e)

    except Exception as e:
        logging.error(e)








