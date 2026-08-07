from pydantic import BaseModel, Field
from typing import Literal


class RiskBase(BaseModel):
    supplier_id: int = Field(gt=0)

    risk_score: float = Field(
        ge=0,
        le=100
    )

    risk_level: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    ]

    delay_days: int = Field(ge=0)

    weather: str = Field(
        min_length=2,
        max_length=100
    )


class RiskCreate(RiskBase):

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_id": 1,
                "risk_score": 82.5,
                "risk_level": "HIGH",
                "delay_days": 5,
                "weather": "Heavy Rain"
            }
        }
    }


class RiskUpdate(RiskBase):

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_id": 1,
                "risk_score": 82.5,
                "risk_level": "HIGH",
                "delay_days": 5,
                "weather": "Heavy Rain"
            }
        }
    }


class RiskResponse(RiskBase):
    risk_id: int

    model_config = {
        "from_attributes": True
    }