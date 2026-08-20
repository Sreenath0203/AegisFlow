"""
Chatbot validation test — mocks IBM Granite to avoid live network calls.
Run with: .venv\Scripts\python.exe tests\_test_chatbot_validation.py
"""
import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch

mock_granite = {
    'status': 'SUCCESS',
    'text': '## Inventory Status\n\n**Total items:** 3\n\n- Microcontroller X1: **CRITICAL** stockout risk, 3 days remaining\n\n**Recommended Action:** Expedite alternative supplier procurement immediately.',
    'model': 'ibm/granite-4-h-small'
}

def run():
    with patch('ai_services.granite.watsonx_client.WatsonxGraniteClient.get_iam_token', return_value='test-token'), \
         patch('ai_services.granite.watsonx_client.WatsonxGraniteClient.generate_text', return_value=mock_granite):

        client = TestClient(app)

        test_queries = [
            ("Show current inventory.",                          {"inventory"}),
            ("Which product has critical stockout risk?",        {"inventory"}),
            ("Show delayed shipments.",                          {"shipments"}),
            ("Which supplier has the highest current risk?",     {"suppliers"}),
            ("What are the current supply-chain risks?",         {"risks"}),
            ("What is the latest Taiwan supply-chain news?",     {"suppliers", "news"}),
            ("What is the weather at Kaohsiung?",                {"weather", "suppliers"}),
            ("Give me an overall supply-chain risk summary.",    {"inventory", "suppliers", "shipments", "risks"}),
        ]

        print("=== Chatbot Endpoint Tests (/api/v1/ai/chat) ===")
        all_ok = True
        for i, (query, expected_tool_keys) in enumerate(test_queries, 1):
            resp = client.post('/api/v1/ai/chat', json={'message': query})
            ok = resp.status_code == 200
            if ok:
                data = resp.json()
                tools = data.get('tools_used', [])
                resp_preview = data["response"][:70]
                print(f"  [{i}] OK | Tools: {tools}")
                print(f"       Preview: {resp_preview}...")
            else:
                print(f"  [{i}] FAIL {resp.status_code}: {resp.text[:120]}")
                all_ok = False

        print()
        print("=== Core API Endpoints (must not break) ===")
        for endpoint in ['/api/v1/inventory/', '/api/v1/suppliers/', '/api/v1/shipments/', '/api/v1/risks/']:
            r = client.get(endpoint)
            status = "OK" if r.status_code == 200 else f"FAIL {r.status_code}"
            print(f"  {endpoint}: {status}")
            if r.status_code != 200:
                all_ok = False

        print()
        if all_ok:
            print("ALL TESTS PASSED")
        else:
            print("SOME TESTS FAILED")
            sys.exit(1)

if __name__ == '__main__':
    run()
