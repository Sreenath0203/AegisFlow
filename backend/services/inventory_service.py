from sqlalchemy.orm import Session

from models.inventory import Inventory
from schemas.inventory_schema import InventoryCreate, InventoryUpdate


def get_all_inventory(db: Session):
    return db.query(Inventory).all()


def get_inventory(db: Session, inventory_id: int):
    return (
        db.query(Inventory)
        .filter(Inventory.inventory_id == inventory_id)
        .first()
    )


def create_inventory(db: Session, inventory: InventoryCreate):
    new_inventory = Inventory(**inventory.model_dump())

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return new_inventory


def update_inventory(
    db: Session,
    inventory_id: int,
    inventory: InventoryUpdate
):
    db_inventory = (
        db.query(Inventory)
        .filter(Inventory.inventory_id == inventory_id)
        .first()
    )

    if not db_inventory:
        return None

    for key, value in inventory.model_dump().items():
        setattr(db_inventory, key, value)

    db.commit()
    db.refresh(db_inventory)

    return db_inventory


def delete_inventory(db: Session, inventory_id: int):
    db_inventory = (
        db.query(Inventory)
        .filter(Inventory.inventory_id == inventory_id)
        .first()
    )

    if not db_inventory:
        return None

    db.delete(db_inventory)
    db.commit()

    return True