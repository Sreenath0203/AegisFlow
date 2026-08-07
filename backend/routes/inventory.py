from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from security import get_current_user
from models.user import User

from schemas.inventory_schema import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
)

from services import inventory_service

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


@router.get("/", response_model=list[InventoryResponse])
def get_inventory(
    db: Session = Depends(get_db)
):
    return inventory_service.get_all_inventory(db)


@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory_by_id(
    inventory_id: int,
    db: Session = Depends(get_db)
):
    inventory = inventory_service.get_inventory(db, inventory_id)

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    return inventory


@router.post("/", response_model=InventoryResponse)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return inventory_service.create_inventory(db, inventory)


@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    inventory_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = inventory_service.update_inventory(
        db,
        inventory_id,
        inventory
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    return updated


@router.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = inventory_service.delete_inventory(db, inventory_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    return {
        "success": True,
        "message": "Inventory item deleted successfully"
    }