import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestAegisFlowAIChatbot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_chatbot_queries(self):
        test_queries = [
            ("Show current inventory.", ["Get inventory"]),
            ("Which product has critical stockout risk?", ["Get inventory"]),
            ("Show delayed shipments.", ["Get shipments"]),
            ("Which supplier has the highest current risk?", ["Get supply-chain suppliers"]),
            ("What are the current supply-chain risks?", ["Get supply-chain risks"]),
            ("What is the latest Taiwan supply-chain news?", ["Search live global supply chain news"]),
            ("What is the weather at Kaohsiung?", ["Get live weather for a location"]),
            ("Give me an overall supply-chain risk summary.", ["Get inventory", "Get supply-chain suppliers"])
        ]

        for query, expected_tools_subset in test_queries:
            response = self.client.post("/api/v1/ai/chat", json={"message": query})
            self.assertEqual(response.status_code, 200, f"Failed for query '{query}': {response.text}")
            
            data = response.json()
            print(f"\n--- Query: '{query}' ---")
            print(f"Tools Used: {data.get('tools_used')}")
            response_text = data.get('response', '')
            print(f"IBM Granite Response Sample:\n{response_text[:250].encode('utf-8', errors='ignore').decode('utf-8')}...\n")

            self.assertIn("response", data)
            self.assertTrue(len(data["response"]) > 0)
            self.assertIn("tools_used", data)
            self.assertIn("model", data)
            self.assertEqual(data["model"], "ibm/granite-4-h-small")

            # Verify at least one tool was executed
            self.assertTrue(len(data["tools_used"]) > 0)

if __name__ == "__main__":
    unittest.main()
