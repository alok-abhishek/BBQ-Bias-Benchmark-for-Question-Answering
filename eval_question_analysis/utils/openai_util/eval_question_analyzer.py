from openai_client import OpenAIClient
from models.eval_question_schema import EvalQnCategorization
from openai_prompt_instructions import OpenAILLMPromptInstructions
import logging
import json
from pydantic import ValidationError

class EvalQuestionAnalyzer:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        self.prompt = OpenAILLMPromptInstructions()

    @staticmethod
    def get_response_format() -> dict:
        """Define the structured JSON schema for response format."""
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "eval_question_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "is_bias_eval": {
                            "type": "boolean",
                            "description": "Indicates whether the evaluation question tests for bias."
                        },
                        "is_categorized": {
                            "type": "boolean",
                            "description": "Indicates whether the evaluation question has been categorized."
                        },
                        "category": {
                            "type": "string",
                            "description": "The category of the bias, if applicable.",
                            "enum": [
                                "gender_bias",
                                "race_and_ethnicity_bias",
                                "socioeconomic_bias",
                                "cultural_bias",
                                "religion_bias",
                                "sexual_orientation_bias",
                                "disability_bias",
                                "age_bias",
                                "geography_bias",
                                "political_bias",
                                "stereotype_bias",
                                "automation_bias"
                            ]
                        },
                        "explanation_if_categorized": {
                            "type": "string",
                            "description": "Explanation if the question is categorized."
                        },
                        "explanation_if_not_bias_eval": {
                            "type": "string",
                            "description": "Explanation if the question is not categorized as bias evaluation."
                        },
                        "improved_bias_eval_question": {
                            "type": "string",
                            "description": "A suggested improved version of the evaluation question to reduce bias."
                        }
                    },
                    "required": [
                        "is_bias_eval",
                        "is_categorized",
                        "category",
                        "explanation_if_categorized",
                        "explanation_if_not_bias_eval",
                        "improved_bias_eval_question"
                    ],
                    "additionalProperties": False
                }
            }
        }

    def analyze_question(self, question: str) -> tuple[EvalQnCategorization, dict]:
        """
        Analyze an evaluation question for bias and categorization.

        Args:
            question (str): The evaluation question to analyze.

        Returns:
            tuple:
                - EvalQnCategorization: Parsed and validated response.
                - dict: Raw JSON data from the response.
        """
        response_format = self.get_response_format()
        messages = [
            {"role": "system", "content": self.prompt.instruction},
            {"role": "user", "content": question}
        ]

        try:
            response = self.openai_client.make_chat_completion(
                model="gpt-4o",
                messages=messages,
                response_format=response_format,
                temperature=1,
                max_completion_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            response_content = response.choices[0].message.content
            parsed_data = json.loads(response_content)
            # Validate and return parsed data
            validated_model = EvalQnCategorization(**parsed_data)
            # Return both validated and raw JSON
            return validated_model, parsed_data
        except (json.JSONDecodeError, ValidationError) as e:
            logging.error(f"Error parsing or validating the response: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during analysis: {e}")
            raise

