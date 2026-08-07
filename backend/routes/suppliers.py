from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from security import get_current_user
from models.user import User

from schemas.supplier_schema import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
)

from services import supplier_service

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


@router.get("/", response_model=list[SupplierResponse])
def get_suppliers(
    db: Session = Depends(get_db)
):
    return supplier_service.get_all_suppliers(db)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    supplier = supplier_service.get_supplier(db, supplier_id)

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return supplier


@router.post("/", response_model=SupplierResponse)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return supplier_service.create_supplier(db, supplier)


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = supplier_service.update_supplier(
        db,
        supplier_id,
        supplier
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return updated


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = supplier_service.delete_supplier(
        db,
        supplier_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return {
        "success": True,
        "message": "Supplier deleted successfully"
    }