from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.db import get_db
from backend.models.models import Supplier
from backend.schemas.schemas import SupplierOut

router = APIRouter(prefix="/suppliers", tags=["Supplier Management"])

@router.get("", response_model=List[SupplierOut])
@router.get("/", response_model=List[SupplierOut])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).order_by(Supplier.reliability_score.asc()).all()

@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Supplier with ID {supplier_id} not found")
    return supplier

@router.post("/{supplier_id}/analyze")
def analyze_supplier_risk(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Supplier with ID {supplier_id} not found")
    
    return {
        "agent": "Supplier Risk Agent",
        "supplier_id": supplier.id,
        "supplier_name": supplier.name,
        "reliability_score": supplier.reliability_score,
        "risk_level": supplier.current_risk_level or supplier.risk_level
    }
