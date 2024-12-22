from enum import Enum
from typing import Optional
from pydantic import BaseModel
class EvalQnCategory(str, Enum):
    gender = "gender_bias"
    race_ethnicity = "race_and_ethnicity_bias"
    socioeconomic = "socioeconomic_bias"
    cultural = "cultural_bias"
    religion = "religion_bias"
    sexual_orientation = "sexual_orientation_bias"
    disability = "disability_bias"
    age = "age_bias"
    geography = "geography_bias"
    political = "political_bias"
    stereotype = "stereotype_bias"
    automation = "automation_bias"

class EvalQnCategorization(BaseModel):
    is_bias_eval: bool
    is_categorized: bool
    category: Optional[EvalQnCategory]
    explanation_if_categorized: Optional[str]
    explanation_if_not_bias_eval: Optional[str]



