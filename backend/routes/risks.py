from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.db import get_db
from backend.models.models import Risk
from backend.schemas.schemas import RiskOut

router = APIRouter(prefix="/risks", tags=["Risk Intelligence"])

@router.get("", response_model=List[RiskOut])
@router.get("/", response_model=List[RiskOut])
def list_risks(db: Session = Depends(get_db)):
    return db.query(Risk).order_by(Risk.risk_score.desc()).all()

@router.get("/{entity_id}", response_model=RiskOut)
def get_risk(entity_id: int, db: Session = Depends(get_db)):
    risk = db.query(Risk).filter(
        (Risk.id == entity_id) | 
        (Risk.entity_id == entity_id) | 
        (Risk.affected_supplier_id == entity_id) | 
        (Risk.affected_shipment_id == entity_id)
    ).first()
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk record for entity / ID {entity_id} not found")
    return risk
