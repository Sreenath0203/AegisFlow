from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.db import get_db
from backend.models.models import Recommendation, Supplier, Shipment, Risk
from backend.schemas.schemas import RecommendationOut

router = APIRouter(prefix="/recommendations", tags=["AI & Rule-Based Recommendations"])

@router.get("", response_model=List[RecommendationOut])
@router.get("/", response_model=List[RecommendationOut])
def list_recommendations(db: Session = Depends(get_db)):
    recs = db.query(Recommendation).order_by(Recommendation.created_at.desc()).all()
    if not recs:
        # Rule-based fallback recommendation generation if database is empty
        suppliers = db.query(Supplier).all()
        shipments = db.query(Shipment).all()
        
        fallback_recs = []
        for s in suppliers:
            if s.reliability_score < 90.0 or s.current_risk_level in ["HIGH", "CRITICAL"]:
                r = Recommendation(
                    entity_type="supplier",
                    entity_id=s.id,
                    action_title=f"Consider alternate supplier for {s.name}",
                    recommendation=f"Evaluate secondary backup supplier to mitigate low reliability ({s.reliability_score}%).",
                    reasoning="Low reliability score detected; increasing supplier monitoring.",
                    reason="Low supplier reliability.",
                    priority="High",
                    confidence=0.85,
                    status="PROPOSED"
                )
                db.add(r)
                fallback_recs.append(r)
        
        for shp in shipments:
            if shp.delay_days > 0 or shp.status in ["AT_RISK", "DELAYED"]:
                r = Recommendation(
                    entity_type="logistics",
                    entity_id=shp.id,
                    action_title=f"Investigate logistics route for {shp.shipment_code}",
                    recommendation=f"Evaluate backup logistics provider for shipment {shp.shipment_code}.",
                    reasoning=f"Major shipment delay of {shp.delay_days} days observed.",
                    reason="Logistics delay detected.",
                    priority="High",
                    confidence=0.90,
                    status="PROPOSED"
                )
                db.add(r)
                fallback_recs.append(r)

        if fallback_recs:
            db.commit()
            return fallback_recs

    return recs

@router.post("/{rec_id}/approve")
def approve_recommendation(rec_id: int, db: Session = Depends(get_db)):
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail=f"Recommendation #{rec_id} not found")
    rec.status = "APPROVED"
    db.commit()
    return {"status": "SUCCESS", "message": f"Recommendation #{rec_id} approved.", "recommendation": rec.action_title}
