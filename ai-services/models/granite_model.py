from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

from backend.config import (
    WATSONX_API_KEY,
    WATSONX_PROJECT_ID,
    WATSONX_URL,
    MODEL_ID,
)

credentials = Credentials(
    api_key=WATSONX_API_KEY,
    url=WATSONX_URL
)

model = ModelInference(
    model_id=MODEL_ID,
    credentials=credentials,
    project_id=WATSONX_PROJECT_ID
)

def generate_response(prompt):
    response = model.generate_text(
        prompt=prompt,
        params={
            "max_new_tokens": 200,
            "temperature": 0.2
        }
    )
    return response