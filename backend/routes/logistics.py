from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.db import get_db
from backend.models.models import Shipment
from backend.schemas.schemas import ShipmentOut

router = APIRouter(prefix="/logistics", tags=["Logistics Management"])

@router.get("", response_model=List[ShipmentOut])
@router.get("/", response_model=List[ShipmentOut])
def list_logistics(db: Session = Depends(get_db)):
    return db.query(Shipment).all()

@router.get("/{shipment_id}", response_model=ShipmentOut)
def get_logistics_item(shipment_id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter((Shipment.id == shipment_id) | (Shipment.shipment_code == str(shipment_id))).first()
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Logistics record / Shipment with ID {shipment_id} not found")
    return shipment
