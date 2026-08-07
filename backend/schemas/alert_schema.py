from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


class AlertBase(BaseModel):
    supplier_id: int = Field(gt=0)

    alert_type: str = Field(
        min_length=2,
        max_length=100
    )

    message: str = Field(
        min_length=5,
        max_length=500
    )

    severity: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    ]

    status: Literal[
        "OPEN",
        "IN_PROGRESS",
        "RESOLVED"
    ]


class AlertCreate(AlertBase):

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_id": 1,
                "alert_type": "Delivery Delay",
                "message": "Shipment delayed by 2 days due to bad weather.",
                "severity": "HIGH",
                "status": "OPEN"
            }
        }
    }


class AlertUpdate(AlertBase):

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_id": 1,
                "alert_type": "Delivery Delay",
                "message": "Shipment delayed by 2 days due to bad weather.",
                "severity": "HIGH",
                "status": "IN_PROGRESS"
            }
        }
    }


class AlertResponse(AlertBase):
    alert_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }