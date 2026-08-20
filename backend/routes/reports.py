from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.models import Risk, Supplier, Shipment, Recommendation, ScenarioResult

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("", summary="Get Executive Report Summary")
@router.get("/", summary="Get Executive Report Summary")
@router.get("/summary", summary="Get Executive Report Summary")
def get_executive_report(db: Session = Depends(get_db)):
    risks = db.query(Risk).all()
    suppliers = db.query(Supplier).all()
    shipments = db.query(Shipment).all()
    recommendations = db.query(Recommendation).all()
    scenarios = db.query(ScenarioResult).all()

    return {
        "report_title": "AegisFlow Supply Chain Decision Intelligence Executive Report",
        "generated_at": "2026-08-08",
        "risk_summary": {
            "total_active_risks": len([r for r in risks if r.status == "ACTIVE"]),
            "high_severity_count": len([r for r in risks if getattr(r, 'severity', '') in ["HIGH", "CRITICAL"]]),
            "top_risk": risks[0].title if risks else "None"
        },
        "supplier_performance": {
            "total_suppliers": len(suppliers),
            "average_reliability": round(sum(s.reliability_score for s in suppliers) / max(1, len(suppliers)), 2),
            "at_risk_suppliers": [s.name for s in suppliers if getattr(s, 'current_risk_level', '') in ["HIGH", "CRITICAL"]]
        },
        "shipment_status": {
            "total_shipments": len(shipments),
            "at_risk_count": len([s for s in shipments if getattr(s, 'status', '') == "AT_RISK"]),
            "delayed_count": len([s for s in shipments if getattr(s, 'delay_days', 0) > 0])
        },
        "recommendations_audit": [
            {
                "action": r.action_title,
                "status": r.status,
                "confidence": f"{int(((r.confidence_score or r.confidence or 0.90) * 100))}%",
                "impact": r.expected_impact or r.reasoning or "Mitigates supply disruption"
            } for r in recommendations
        ],
        "scenario_evaluations": [
            {
                "option": sc.scenario_name or sc.name or "Scenario",
                "cost_delta": f"${sc.cost_delta:,.2f}",
                "delay_days": sc.delay_days,
                "risk_score": sc.risk_score,
                "recommended": sc.is_recommended
            } for sc in scenarios
        ]
    }

