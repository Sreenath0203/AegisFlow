from pydantic import BaseModel, Field
from typing import Literal


class InventoryBase(BaseModel):
    supplier_id: int = Field(gt=0)

    item_name: str = Field(
        min_length=2,
        max_length=100
    )

    category: str = Field(
        min_length=2,
        max_length=100
    )

    quantity: int = Field(ge=0)

    unit_price: float = Field(gt=0)

    reorder_level: int = Field(ge=0)

    status: Literal[
        "In Stock",
        "Low Stock",
        "Out of Stock"
    ]


class InventoryCreate(InventoryBase):

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_id": 1,
                "item_name": "Steel Rods",
                "category": "Raw Material",
                "quantity": 120,
                "unit_price": 450.50,
                "reorder_level": 50,
                "status": "In Stock"
            }
        }
    }


class InventoryUpdate(InventoryBase):

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_id": 1,
                "item_name": "Steel Rods",
                "category": "Raw Material",
                "quantity": 120,
                "unit_price": 450.50,
                "reorder_level": 50,
                "status": "In Stock"
            }
        }
    }


class InventoryResponse(InventoryBase):
    inventory_id: int

    model_config = {
        "from_attributes": True
    }