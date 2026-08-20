import logging
from typing import Dict, List, Any

logger = logging.getLogger("aegisflow.dataprep")

class IBMDataPrepKit:
    """
    IBM Data Prep Kit Integration Module.
    Transforms raw supply chain telemetry, news feeds, and ERP data into 
    clean, structured feature vectors for IBM watsonx.ai agents and RAG indexing.
    """
    def __init__(self):
        self.pipeline_name = "IBM-DataPrepKit-SupplyChain-v1"

    def clean_news_payload(self, raw_news: Dict[str, Any]) -> Dict[str, Any]:
        headline = raw_news.get("headline", "").strip()
        body = raw_news.get("body", raw_news.get("supply_chain_impact", "")).strip()
        
        severity = "LOW"
        if any(term in headline.lower() or term in body.lower() for term in ["typhoon", "catastrophe", "super typhoon", "shutdown", "critical"]):
            severity = "CRITICAL"
        elif any(term in headline.lower() or term in body.lower() for term in ["storm", "strike", "delay", "shortage"]):
            severity = "HIGH"

        return {
            "headline": headline,
            "cleaned_body": body,
            "severity_token": severity,
            "processed_by": self.pipeline_name
        }

    def prepare_supplier_telemetry(self, raw_metrics: Dict[str, Any]) -> Dict[str, Any]:
        rel = float(raw_metrics.get("reliability_score", 95.0))
        otd = float(raw_metrics.get("on_time_delivery", 92.0))
        qual = float(raw_metrics.get("quality_score", 98.0))
        delay = float(raw_metrics.get("delay_days", 0))

        composite_health_index = round((rel * 0.4 + otd * 0.4 + qual * 0.2) - (delay * 5.0), 2)
        composite_health_index = max(0.0, min(100.0, composite_health_index))

        return {
            "supplier_id": raw_metrics.get("supplier_id"),
            "health_index": composite_health_index,
            "risk_category": "CRITICAL" if composite_health_index < 60 else ("HIGH" if composite_health_index < 75 else "LOW")
        }

data_prep_kit = IBMDataPrepKit()
