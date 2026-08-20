import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestAllEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_static_assets(self):
        r_css = self.client.get("/static/css/style.css")
        self.assertEqual(r_css.status_code, 200)

        r_api = self.client.get("/static/js/api.js")
        self.assertEqual(r_api.status_code, 200)

        r_app = self.client.get("/static/js/app.js")
        self.assertEqual(r_app.status_code, 200)

    def test_browser_root_returns_html(self):
        response = self.client.get("/", headers={"accept": "text/html,application/xhtml+xml"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("AegisFlow", response.text)
        self.assertIn("<!DOCTYPE html>", response.text)

    def test_api_root_returns_json(self):
        response = self.client.get("/", headers={"accept": "application/json"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["project"], "AegisFlow")

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_v1_dashboard_summary(self):
        response = self.client.get("/api/v1/dashboard/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("overall_risk_score", data)
        self.assertIn("overall_risk_level", data)
        self.assertIn("potential_impact", data)

    def test_v1_risks(self):
        response = self.client.get("/api/v1/risks/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_v1_suppliers(self):
        response = self.client.get("/api/v1/suppliers/")
        self.assertEqual(response.status_code, 200)
        suppliers = response.json()
        self.assertIsInstance(suppliers, list)
        if len(suppliers) > 0:
            s_id = suppliers[0]["id"]
            r_analyze = self.client.post(f"/api/v1/suppliers/{s_id}/analyze")
            self.assertEqual(r_analyze.status_code, 200)

    def test_v1_shipments(self):
        response = self.client.get("/api/v1/shipments/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_v1_inventory(self):
        response = self.client.get("/api/v1/inventory/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_v1_recommendations(self):
        response = self.client.get("/api/v1/recommendations/")
        self.assertEqual(response.status_code, 200)
        recs = response.json()
        self.assertIsInstance(recs, list)
        if len(recs) > 0:
            rec_id = recs[0]["id"]
            r_appr = self.client.post(f"/api/v1/recommendations/{rec_id}/approve")
            self.assertEqual(r_appr.status_code, 200)

    def test_v1_scenarios(self):
        response = self.client.get("/api/v1/scenarios/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_v1_compliance(self):
        response = self.client.get("/api/v1/compliance/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_v1_news(self):
        response = self.client.get("/api/v1/news/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_v1_reports_summary(self):
        response = self.client.get("/api/v1/reports/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("report_title", data)
        self.assertIn("supplier_performance", data)

    def test_v1_demo_typhoon(self):
        response = self.client.post("/api/v1/demo/trigger-typhoon-scenario")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
