from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.db import get_db
from backend.models.models import Supplier, Shipment, Risk, Inventory, Recommendation
from backend.schemas.schemas import DashboardSummary, DashboardMetrics
from backend.config import settings

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardSummary)
@router.get("/", response_model=DashboardSummary)
def get_dashboard(db: Session = Depends(get_db)):
    total_suppliers = db.query(Supplier).count()
    total_shipments = db.query(Shipment).count()
    
    high_risk_suppliers = db.query(Supplier).filter(
        (Supplier.reliability_score < 90.0) | 
        (Supplier.current_risk_level.in_(["HIGH", "CRITICAL"])) | 
        (Supplier.risk_level.in_(["High", "Critical"]))
    ).count()

    delayed_shipments = db.query(Shipment).filter(
        (Shipment.delay_days > 0) | 
        (Shipment.status.in_(["AT_RISK", "DELAYED"]))
    ).count()

    critical_risks = db.query(Risk).filter(
        (Risk.severity.in_(["HIGH", "CRITICAL"])) | 
        (Risk.risk_level.in_(["High", "Critical"])) | 
        (Risk.risk_score >= 70)
    ).count()

    avg_rel = db.query(func.avg(Supplier.reliability_score)).scalar()
    average_supplier_reliability = round(float(avg_rel), 1) if avg_rel is not None else 95.0

    avg_delay = db.query(func.avg(Shipment.delay_days)).scalar()
    average_delay_days = round(float(avg_delay), 1) if avg_delay is not None else 0.0

    active_risks = db.query(Risk).all()
    if active_risks:
        max_score = max(r.risk_score for r in active_risks)
        avg_score = sum(r.risk_score for r in active_risks) / len(active_risks)
        overall_score = int((max_score * 0.7) + (avg_score * 0.3))
    else:
        overall_score = 15

    risk_level = "CRITICAL" if overall_score >= 80 else ("HIGH" if overall_score >= 60 else ("MEDIUM" if overall_score >= 40 else "LOW"))

    # Calculated financial impact based on delayed shipments and high-risk supplier exposure
    potential_impact_val = float((delayed_shipments * 15000.0) + (high_risk_suppliers * 25000.0))

    return DashboardSummary(
        total_suppliers=total_suppliers,
        total_shipments=total_shipments,
        high_risk_suppliers=high_risk_suppliers,
        delayed_shipments=delayed_shipments,
        critical_risks=critical_risks,
        average_supplier_reliability=average_supplier_reliability,
        average_delay_days=average_delay_days,
        overall_risk_score=overall_score,
        risk_level=risk_level,
        overall_risk_level=risk_level,
        critical_risks_count=critical_risks,
        at_risk_shipments=delayed_shipments,
        at_risk_shipments_count=delayed_shipments,
        suppliers_at_risk=high_risk_suppliers,
        suppliers_at_risk_count=high_risk_suppliers,
        potential_impact=potential_impact_val,
        potential_impact_formatted=f"${potential_impact_val:,.0f}",
        inventory_risks_count=1,
        active_alerts_count=len(active_risks),
        watsonx_status="ONLINE (AegisFlow Intelligence)",
        watsonx_model=settings.MODEL_ID
    )

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    return get_dashboard(db=db)

