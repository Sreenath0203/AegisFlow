from pydantic import BaseModel


class DashboardResponse(BaseModel):
    supplier_count: int
    risk_count: int
    alerts: int
    ai_summary: str

    model_config = {
        "from_attributes": True
    }


class DashboardStats(BaseModel):
    total_suppliers: int
    active_suppliers: int
    high_risk_suppliers: int
    average_risk_score: float

    model_config = {
        "from_attributes": True
    }