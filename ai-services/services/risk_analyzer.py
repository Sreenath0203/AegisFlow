from models.granite_model import generate_response


def analyze_supplier(data):
    prompt = f"""
You are an AI Supply Chain Risk Analyst.

Analyze the supplier below.

Supplier Name: {data['supplier_name']}
Location: {data['location']}
Delay Days: {data['delay_days']}
Weather: {data['weather']}
Status: {data['status']}

Return ONLY in this JSON format:

{{
  "risk_level":"",
  "recommendation":"",
  "reason":"",
  "priority":""
}}

Do not return markdown.
"""

    return generate_response(prompt)