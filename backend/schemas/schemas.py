from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class HealthCheckResponse(BaseModel):
    status: str

class RootResponse(BaseModel):
    project: str
    status: str

class SupplierOut(BaseModel):
    id: int
    supplier_id: Optional[int] = None
    name: str
    supplier_name: Optional[str] = None
    country: str
    reliability_score: float
    on_time_delivery: float
    delivery_days: Optional[float] = None
    quality_score: float
    risk_level: str
    current_risk_level: Optional[str] = None
    category: Optional[str] = None
    supplier_category: Optional[str] = None
    contact_email: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True

class ShipmentOut(BaseModel):
    id: int
    shipment_id: Optional[int] = None
    shipment_code: str
    supplier_id: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    status: str
    delay_days: int
    delay_category: Optional[str] = None
    risk_level: str
    cargo_description: Optional[str] = None
    carrier: Optional[str] = None
    origin_lat: Optional[float] = None
    origin_lng: Optional[float] = None
    dest_lat: Optional[float] = None
    dest_lng: Optional[float] = None

    class Config:
        from_attributes = True

LogisticsOut = ShipmentOut

class InventoryOut(BaseModel):
    id: int
    product_name: Optional[str] = "Default Item"
    sku: Optional[str] = "SKU-GENERIC"
    current_stock: Optional[int] = 1000
    daily_demand: Optional[int] = 50
    reorder_level: Optional[int] = 300
    days_remaining: Optional[int] = 20
    stockout_risk: Optional[str] = "Low"
    stockout_risk_level: Optional[str] = "LOW"
    unit_cost: Optional[float] = 45.0

    class Config:
        from_attributes = True

class RiskOut(BaseModel):
    id: int
    entity_type: Optional[str] = "supplier"
    entity_id: Optional[int] = 1
    title: Optional[str] = "Supply Chain Risk"
    risk_type: Optional[str] = "LOGISTICS"
    risk_score: int
    score: Optional[int] = None
    severity: Optional[str] = "Low"
    risk_level: Optional[str] = "Low"
    impact_description: Optional[str] = None
    risk_reason: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RecommendationOut(BaseModel):
    id: int
    entity_type: Optional[str] = "supplier"
    entity_id: Optional[int] = 1
    action_title: str
    recommendation: Optional[str] = None
    reasoning: Optional[str] = None
    reason: Optional[str] = None
    confidence: Optional[float] = 0.90
    confidence_score: Optional[float] = 0.90
    priority: Optional[str] = "High"
    status: Optional[str] = "PROPOSED"
    expected_impact: Optional[str] = None
    financial_saving: Optional[float] = 0.0
    delay_reduction_days: Optional[int] = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    total_suppliers: int
    total_shipments: int
    high_risk_suppliers: int
    delayed_shipments: int
    critical_risks: int
    average_supplier_reliability: float
    average_delay_days: float

class DashboardSummary(BaseModel):
    total_suppliers: Optional[int] = 5
    total_shipments: Optional[int] = 5
    high_risk_suppliers: Optional[int] = 2
    delayed_shipments: Optional[int] = 2
    critical_risks: Optional[int] = 1
    average_supplier_reliability: Optional[float] = 87.5
    average_delay_days: Optional[float] = 1.4
    overall_risk_score: Optional[int] = 45
    risk_level: Optional[str] = "MEDIUM"
    overall_risk_level: Optional[str] = "MEDIUM"
    critical_risks_count: Optional[int] = 1
    at_risk_shipments: Optional[int] = 2
    at_risk_shipments_count: Optional[int] = 2
    suppliers_at_risk: Optional[int] = 2
    suppliers_at_risk_count: Optional[int] = 2
    potential_impact: Optional[float] = 0.0
    potential_impact_formatted: Optional[str] = "$0"
    inventory_risks_count: Optional[int] = 1
    active_alerts_count: Optional[int] = 3
    watsonx_status: Optional[str] = "ONLINE"
    watsonx_model: Optional[str] = None

    class Config:
        from_attributes = True

class ComplianceOut(BaseModel):
    id: int
    title: Optional[str] = None
    category: Optional[str] = "POLICY"
    entity_name: Optional[str] = None
    policy_name: Optional[str] = None
    status: Optional[str] = "COMPLIANT"
    compliance_status: Optional[str] = "COMPLIANT"
    penalty_risk: Optional[float] = 0.0
    required_action: Optional[str] = None

    class Config:
        from_attributes = True

class NewsOut(BaseModel):
    id: int
    headline: str
    source: Optional[str] = None
    location: Optional[str] = None
    severity: Optional[str] = "LOW"
    impact: Optional[str] = None
    supply_chain_impact: Optional[str] = None
    affected_suppliers: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ScenarioResultOut(BaseModel):
    id: int
    scenario_name: Optional[str] = None
    name: Optional[str] = None
    option_key: Optional[str] = None
    cost_delta: float
    delay_days: int
    risk_score: int
    net_impact: Optional[str] = None
    is_recommended: Optional[bool] = False
    details: Optional[str] = None
    disruption_type: Optional[str] = None

    class Config:
        from_attributes = True
