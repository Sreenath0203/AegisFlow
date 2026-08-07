from backend.services.risk_analyzer import analyze_supplier
from backend.services.recommendation_engine import parse_ai_response

supplier = {
    "supplier_name": "ABC Ltd",
    "location": "Chennai",
    "delay_days": 5,
    "weather": "Heavy Rain",
    "status": "Delayed"
}

ai_response = analyze_supplier(supplier)

result = parse_ai_response(ai_response)

print(result)