import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestIBMGraniteAIRiskAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_real_ibm_granite_risk_analysis_endpoint(self):
        payload = {
            "supplier": "ABC Electronics",
            "shipment_delay_days": 4,
            "inventory_days": 3,
            "weather_risk": "Severe rainfall",
            "supplier_reliability": 65
        }

        # Test both /api/ai/risk-analysis and /api/v1/ai/risk-analysis
        for endpoint in ["/api/ai/risk-analysis", "/api/v1/ai/risk-analysis"]:
            response = self.client.post(endpoint, json=payload)
            self.assertEqual(response.status_code, 200, f"Failed for endpoint {endpoint}: {response.text}")
            
            data = response.json()
            print(f"\nResponse from {endpoint}:", data)

            self.assertIn("risk_level", data)
            self.assertIn("risk_score", data)
            self.assertIn("reason", data)
            self.assertIn("recommendation", data)
            self.assertIn("confidence", data)

            self.assertIsInstance(data["risk_level"], str)
            self.assertIsInstance(data["risk_score"], (int, float))
            self.assertIsInstance(data["reason"], str)
            self.assertIsInstance(data["recommendation"], str)
            self.assertIsInstance(data["confidence"], (int, float))

if __name__ == "__main__":
    unittest.main()
