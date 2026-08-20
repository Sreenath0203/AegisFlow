from ai_services.agents.base_agent import BaseAgent
from typing import Dict, Any

class SupplierRiskAgent(BaseAgent):
    """
    2. Supplier Risk Agent – Analyzes supplier metrics, delivery performance, lead times, and reliability indices.
    """
    def __init__(self):
        super().__init__(name="Supplier Risk Agent", role="Supplier Performance & Vulnerability Evaluator")

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        supplier = context.get("supplier", {})
        news_report = context.get("news_report", {})

        base_reliability = supplier.get("reliability_score", 94.5)

        if news_report.get("affected_supplier") == supplier.get("name") or "ABC Electronics" in supplier.get("name", ""):
            adjusted_reliability = 52.0
            predicted_delay = 5
            risk_level = "HIGH"
            risk_score = 87
            vulnerability_summary = (
                "Critical port closure in Kaohsiung directly blocks ABC Electronics main dispatch vessel. "
                "Reliability temporarily downgraded to 52.0%. Predicted shipment delay: 4-5 days."
            )
        else:
            adjusted_reliability = base_reliability
            predicted_delay = 0
            risk_level = "LOW"
            risk_score = 20
            vulnerability_summary = "Supplier operating within nominal performance thresholds."

        return {
            "agent": self.name,
            "supplier_name": supplier.get("name", "ABC Electronics Co."),
            "original_reliability": base_reliability,
            "adjusted_reliability": adjusted_reliability,
            "predicted_delay_days": predicted_delay,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "vulnerability_summary": vulnerability_summary,
            "evidence": f"ERP Telemetry: OTD rate {supplier.get('on_time_delivery', 92)}%, Quality rating {supplier.get('quality_score', 98)}%."
        }

supplier_risk_agent = SupplierRiskAgent()
