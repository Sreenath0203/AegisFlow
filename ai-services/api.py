from fastapi import FastAPI
from services.risk_analyzer import analyze_supplier
from services.recommendation_engine import parse_ai_response

app = FastAPI()


@app.post("/analyze-risk")
def analyze(data: dict):

    ai_response = analyze_supplier(data)

    result = parse_ai_response(ai_response)

    return result