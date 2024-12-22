from openai import OpenAI
import json
import dotenv
import os
from openai_prompt_instructions import OpenAILLMPromptInstructions
from ..eval_questions_category import EvalQnCategorization
dotenv.load_dotenv()


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_ORG_ID = os.environ.get("OPENAI_ORG_ID")
OPENAI_PRJ_ID = os.environ.get("OPENAI_PRJ_ID")
client = OpenAI(
    api_key=OPENAI_API_KEY, organization=OPENAI_ORG_ID, project=OPENAI_PRJ_ID
)


prompt = OpenAILLMPromptInstructions()
eval_qn_category = EvalQnCategorization()

response = client.beta.chat.completions.parse(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": prompt.instruction},
    {"role": "user", "content": "How do I prepare for a job interview?"}
    ],
  response_format=eval_qn_category,
  temperature=1,
  max_completion_tokens=2048,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

qn_category = response.choices[0].message.parsed

print(qn_category)