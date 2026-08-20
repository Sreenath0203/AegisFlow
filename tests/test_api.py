import unittest
from fastapi.testclient import TestClient
from backend.main import app
from data_pipeline.processing.pipeline_exporter import run_pipeline_ingestion

class TestAegisFlowAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run pipeline ingestion to populate test database
        run_pipeline_ingestion()
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["project"], "AegisFlow")
        self.assertEqual(data["status"], "running")

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["status"].lower() in ["healthy", "running"])

    def test_get_suppliers(self):
        response = self.client.get("/api/suppliers")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_get_supplier_by_valid_id(self):
        response = self.client.get("/api/suppliers/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], 1)

    def test_get_supplier_by_invalid_id(self):
        response = self.client.get("/api/suppliers/99999")
        self.assertEqual(response.status_code, 404)

    def test_get_logistics(self):
        response = self.client.get("/api/logistics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_get_logistics_by_valid_id(self):
        response = self.client.get("/api/logistics/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], 1)

    def test_get_logistics_by_invalid_id(self):
        response = self.client.get("/api/logistics/99999")
        self.assertEqual(response.status_code, 404)

    def test_get_risks(self):
        response = self.client.get("/api/risks")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_get_risk_by_valid_id(self):
        # Fetch list first to get an existing risk ID if present
        response_list = self.client.get("/api/risks")
        risks = response_list.json()
        if len(risks) > 0:
            risk_id = risks[0]["id"]
            response = self.client.get(f"/api/risks/{risk_id}")
            self.assertEqual(response.status_code, 200)

    def test_get_risk_by_invalid_id(self):
        response = self.client.get("/api/risks/99999")
        self.assertEqual(response.status_code, 404)

    def test_get_recommendations(self):
        response = self.client.get("/api/recommendations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_get_dashboard(self):
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_suppliers", data)
        self.assertIn("total_shipments", data)
        self.assertIn("average_supplier_reliability", data)
        self.assertIn("average_delay_days", data)

    def test_dashboard_summary(self):
        response = self.client.get("/api/v1/dashboard/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("overall_risk_score", data)

    def test_pipeline_repeated_execution(self):
        result1 = run_pipeline_ingestion()
        result2 = run_pipeline_ingestion()
        self.assertEqual(result1["status"], "SUCCESS")
        self.assertEqual(result2["status"], "SUCCESS")

if __name__ == "__main__":
    unittest.main()
