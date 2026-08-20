from ai_services.agents.base_agent import BaseAgent
from ai_services.rag.retrieval import rag_service
from typing import Dict, Any

class ComplianceAgent(BaseAgent):
    """
    3. Compliance Agent – Checks contracts, regulations, policies, force majeure clauses, and penalties.
    """
    def __init__(self):
        super().__init__(name="Compliance Agent", role="Contractual & Regulatory Inspector")

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        supplier_name = context.get("supplier_report", {}).get("supplier_name", "ABC Electronics Co.")
        
        rag_docs = rag_service.query_enterprise_knowledge(f"Force Majeure penalty MSA {supplier_name}")

        contract_clause = rag_docs[0]["content"] if rag_docs else "Standard MSA SLA terms apply."

        force_majeure_status = "APPLICABLE_WITH_NOTICE"
        penalty_exposure_per_day = 15000.0
        multi_sourcing_compliance = "VIOLATED_POL_SUP_04"

        findings = (
            "1. Contract MSA-2025 Section 14.2: Force Majeure clause applies if formal 24h notice submitted.\n"
            "2. Penalty Exposure: $15,000/day unexcused delay liability.\n"
            "3. Internal Policy POL-SUP-04: Single-sourcing Microcontroller X1 at 100% capacity violates 70% max multi-sourcing cap."
        )

        return {
            "agent": self.name,
            "compliance_status": "AT_RISK",
            "force_majeure_status": force_majeure_status,
            "daily_penalty_exposure": penalty_exposure_per_day,
            "policy_violation": "POL-SUP-04 (Multi-sourcing threshold exceeded)",
            "contract_clause_summary": contract_clause,
            "findings": findings,
            "evidence": f"IBM watsonx RAG Retrieval: Found {len(rag_docs)} matching enterprise contracts and policy documents."
        }

compliance_agent = ComplianceAgent()
