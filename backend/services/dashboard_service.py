from sqlalchemy.orm import Session
from sqlalchemy import func

from models.supplier import Supplier
from models.risk import Risk


def get_dashboard_stats(db: Session):
    total_suppliers = db.query(Supplier).count()

    active_suppliers = (
        db.query(Supplier)
        .filter(Supplier.status == "Active")
        .count()
    )

    high_risk_suppliers = (
        db.query(Risk)
        .filter(Risk.risk_level == "High")
        .count()
    )

    average_risk_score = (
        db.query(func.avg(Risk.risk_score))
        .scalar()
    )

    if average_risk_score is None:
        average_risk_score = 0

    return {
        "total_suppliers": total_suppliers,
        "active_suppliers": active_suppliers,
        "high_risk_suppliers": high_risk_suppliers,
        "average_risk_score": round(float(average_risk_score), 2),
    }