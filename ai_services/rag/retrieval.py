import logging
from typing import List, Dict, Any
from backend.config.settings import settings
from ai_services.granite.watsonx_client import watsonx_client

logger = logging.getLogger("aegisflow.rag")

class WatsonxRAGService:
    """
    IBM watsonx.ai Enterprise Retrieval-Augmented Generation (RAG) Service.
    Retrieves enterprise contracts, SLAs, supplier policies, and contingency playbooks.
    """
    def __init__(self):
        self.collection_id = settings.WATSONX_RAG_COLLECTION_ID
        self._knowledge_base = [
            {
                "id": "KB-DOC-001",
                "title": "Master Supply Agreement - ABC Electronics (MSA-2025)",
                "category": "Contract SLA",
                "keywords": ["ABC Electronics", "Taiwan", "Kaohsiung", "Penalty", "Force Majeure", "Microcontroller X1"],
                "content": (
                    "MSA-2025 Section 14.2 (Force Majeure): Performance delays are excused only upon receipt of official "
                    "meteorological Category 3 or higher storm warning within 24 hours of event declaration. "
                    "Unexcused shipment delays incur a penalty of $15,000/day. Supplier must maintain 5-day contingency notification lead time."
                )
            },
            {
                "id": "KB-DOC-002",
                "title": "Backup Procurement Framework - Supplier XYZ Logistics",
                "category": "Supplier Capacity",
                "keywords": ["Supplier XYZ", "Vietnam", "Hai Phong", "Backup", "Microcontroller X1", "Capacity"],
                "content": (
                    "Supplier XYZ Logistics is pre-vetted as a Tier-1 secondary supplier for Microcontroller X1 compatible chips. "
                    "Contracted emergency capacity: Up to 15,000 units/week with express 48-hour dispatch lead time via Air Freight or Indochina Express maritime."
                )
            },
            {
                "id": "KB-DOC-003",
                "title": "Internal Multi-Sourcing Governance Policy (POL-SUP-04)",
                "category": "Enterprise Policy",
                "keywords": ["Policy", "Multi-Sourcing", "Governance", "Risk Mitigation", "Stockout"],
                "content": (
                    "Enterprise Supply Policy POL-SUP-04 mandates that no single component SKU critical to assembly line continuity "
                    "shall depend > 70% on a single geographic region. If severe regional disruption exceeds 72 hours, "
                    "procurement team is authorized to shift up to 50% order volume to secondary regional partners."
                )
            },
            {
                "id": "KB-DOC-004",
                "title": "Disruption Mitigation Playbook: Maritime Port Shutdown",
                "category": "Contingency Playbook",
                "keywords": ["Weather", "Typhoon", "Port Shutdown", "Air Freight", "Split Order"],
                "content": (
                    "Playbook SC-ALT-09: In case of typhoon-induced port closure in East Asia (> 4 days delay predicted), "
                    "recommended strategy is: (1) Split order 60/40 between primary and backup supplier, "
                    "(2) Expedite 10% of emergency buffer via priority Air Freight to prevent line shutdown, "
                    "(3) Notify downstream manufacturing schedulers immediately."
                )
            }
        ]

    def query_enterprise_knowledge(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        logger.info(f"Querying IBM watsonx RAG service for query: '{query}'")
        query_words = set(query.lower().split())
        scored_docs = []

        for doc in self._knowledge_base:
            score = 0
            full_text = (doc["title"] + " " + doc["content"] + " " + " ".join(doc["keywords"])).lower()
            for word in query_words:
                if len(word) > 2 and word in full_text:
                    score += 1
            for kw in doc["keywords"]:
                if kw.lower() in query.lower():
                    score += 3
            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = [doc for score, doc in scored_docs[:top_k]]
        if not results:
            results = self._knowledge_base[:top_k]
        return results

rag_service = WatsonxRAGService()
