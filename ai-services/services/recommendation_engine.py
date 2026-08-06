import json

def parse_ai_response(response):

    response = response.replace("```json", "")
    response = response.replace("```", "")

    start = response.find("{")
    end = response.rfind("}") + 1

    response = response[start:end]

    return json.loads(response)