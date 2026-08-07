from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.risk_schema import (
    RiskCreate,
    RiskUpdate,
    RiskResponse,
)

from services import risk_service

router = APIRouter(
    prefix="/risks",
    tags=["Risks"]
)


@router.get("/", response_model=list[RiskResponse])
def get_risks(db: Session = Depends(get_db)):
    return risk_service.get_all_risks(db)


@router.get("/{risk_id}", response_model=RiskResponse)
def get_risk(risk_id: int, db: Session = Depends(get_db)):
    risk = risk_service.get_risk(db, risk_id)

    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    return risk


@router.post("/", response_model=RiskResponse)
def create_risk(
    risk: RiskCreate,
    db: Session = Depends(get_db)
):
    return risk_service.create_risk(db, risk)


@router.put("/{risk_id}", response_model=RiskResponse)
def update_risk(
    risk_id: int,
    risk: RiskUpdate,
    db: Session = Depends(get_db)
):
    updated = risk_service.update_risk(
        db,
        risk_id,
        risk
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Risk not found")

    return updated


@router.delete("/{risk_id}")
def delete_risk(
    risk_id: int,
    db: Session = Depends(get_db)
):
    deleted = risk_service.delete_risk(db, risk_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Risk not found")

    return {
        "success": True,
        "message": "Risk deleted successfully"
    }