from pydantic import BaseModel, Field
from typing import Literal


class RecommendationCreate(BaseModel):

    supplier_id: int = Field(gt=0)

    recommendation: str = Field(
        min_length=5,
        max_length=500
    )

    reason: str = Field(
        min_length=5,
        max_length=500
    )

    priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_id": 1,
                "recommendation": "Switch to alternate supplier",
                "reason": "Supplier has consistently delayed shipments and has a high risk score.",
                "priority": "HIGH"
            }
        }
    }


class RecommendationResponse(BaseModel):

    recommendation_id: int

    supplier_id: int

    recommendation: str

    reason: str

    priority: str

    model_config = {
        "from_attributes": True
    }