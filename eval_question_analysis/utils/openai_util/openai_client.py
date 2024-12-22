from openai import OpenAI
import logging

class OpenAIClient:
    def __init__(self, api_key: str, organization: str):
        self.client = OpenAI(api_key=api_key, organization=organization)

    def make_chat_completion(self, model: str, messages: list, response_format: dict, **kwargs):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=response_format,
                **kwargs
            )
            return response
        except Exception as e:
            logging.error(f"Failed to get chat completion: {e}")
            raise
