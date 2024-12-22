import json
import os
from typing import Iterator, List, Dict, Any



base_input_path = "../../../../data/"
eval_qn_jsonl_files = {
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
    'orientation': 'Sexual_orientation.jsonl'
}

input_file_path = os.path.join(base_input_path, eval_qn_jsonl_files['age'])


def read_jsonl_file(file_path: str) -> Iterator[Dict[str, Any]]:
    """
    Read a JSONL file with robust error handling and logging.
    Handles common issues like BOM marks and encoding errors.

    Args:
        file_path: Path to the JSONL file

    Yields:
        Dictionary representing each JSON record
    """
    try:
        # Try UTF-8 with BOM first
        encoding = 'utf-8-sig'
        with open(file_path, 'r', encoding=encoding) as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                    print(f"Problematic line: {line}")
                    continue

    except UnicodeDecodeError:
        # Fallback to different encodings if UTF-8 fails
        for encoding in ['utf-16', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    for line_num, line in enumerate(file, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError as e:
                            print(f"Error parsing line {line_num}: {e}")
                            continue
                break  # If we successfully read the file, exit the encoding loop
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError(f"Could not decode file {file_path} with any supported encoding")


for record in read_jsonl_file(input_file_path):
    context = record['context']
    question = record['question']
    eval_question = context + question
    print(eval_question)