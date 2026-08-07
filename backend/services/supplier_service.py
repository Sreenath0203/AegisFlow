from sqlalchemy.orm import Session

from models.supplier import Supplier
from schemas.supplier_schema import SupplierCreate, SupplierUpdate


def get_all_suppliers(db: Session):
    return db.query(Supplier).all()


def get_supplier(db: Session, supplier_id: int):
    return db.query(Supplier).filter(
        Supplier.supplier_id == supplier_id
    ).first()


def create_supplier(db: Session, supplier: SupplierCreate):
    new_supplier = Supplier(**supplier.model_dump())

    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)

    return new_supplier


def update_supplier(db: Session, supplier_id: int, supplier: SupplierUpdate):

    existing = get_supplier(db, supplier_id)

    if not existing:
        return None

    for key, value in supplier.model_dump().items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    return existing


def delete_supplier(db: Session, supplier_id: int):

    supplier = get_supplier(db, supplier_id)

    if not supplier:
        return None

    db.delete(supplier)
    db.commit()

    return supplier