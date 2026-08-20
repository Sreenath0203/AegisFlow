from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.db import get_db
from backend.models.models import Shipment
from backend.schemas.schemas import ShipmentOut

router = APIRouter(prefix="/shipments", tags=["Shipment Management"])

@router.get("", response_model=List[ShipmentOut])
@router.get("/", response_model=List[ShipmentOut])
def list_shipments(supplier_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Shipment)
    if supplier_id is not None:
        query = query.filter(Shipment.supplier_id == supplier_id)
    return query.all()

@router.get("/{shipment_id}", response_model=ShipmentOut)
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Shipment with ID {shipment_id} not found")
    return shipment

@router.get("/by-supplier/{supplier_id}", response_model=List[ShipmentOut])
def get_shipments_by_supplier(supplier_id: int, db: Session = Depends(get_db)):
    return db.query(Shipment).filter(Shipment.supplier_id == supplier_id).all()
