from pydantic import BaseModel, Field
from typing import Literal


class SupplierBase(BaseModel):
    supplier_name: str = Field(
        min_length=2,
        max_length=100
    )

    location: str = Field(
        min_length=2,
        max_length=100
    )

    status: Literal[
        "Active",
        "Inactive",
        "Pending"
    ]


class SupplierCreate(SupplierBase):

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_name": "ABC Logistics Pvt Ltd",
                "location": "Coimbatore",
                "status": "Active"
            }
        }
    }


class SupplierUpdate(SupplierBase):

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_name": "ABC Logistics Pvt Ltd",
                "location": "Coimbatore",
                "status": "Active"
            }
        }
    }


class SupplierResponse(SupplierBase):
    supplier_id: int

    model_config = {
        "from_attributes": True
    }