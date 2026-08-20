from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    role = Column(String(50), default="OPERATOR")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    country = Column(String(100), nullable=False, default="Unknown")
    reliability_score = Column(Float, default=95.0)
    on_time_delivery = Column(Float, default=92.0)
    quality_score = Column(Float, default=98.0)
    risk_level = Column(String(20), default="Low")  # Low, Moderate, High, Critical
    current_risk_level = Column(String(20), default="LOW")
    category = Column(String(100), default="General Components")
    contact_email = Column(String(150), nullable=True)
    latitude = Column(Float, nullable=True, default=22.6273)
    longitude = Column(Float, nullable=True, default=120.3014)

    @property
    def supplier_id(self) -> int:
        return self.id

    @property
    def supplier_name(self) -> str:
        return self.name

    @property
    def delivery_days(self) -> float:
        return round(100.0 - self.on_time_delivery, 1)

    @property
    def supplier_category(self) -> str:
        return self.category

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    unit_cost = Column(Float, default=50.0)

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    shipment_code = Column(String(50), unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    origin = Column(String(100))
    destination = Column(String(100))
    status = Column(String(50), default="IN_TRANSIT")
    delay_days = Column(Integer, default=0)
    risk_level = Column(String(20), default="Low")
    cargo_description = Column(String(250), nullable=True)
    carrier = Column(String(150), nullable=True)
    origin_lat = Column(Float, nullable=True, default=22.6273)
    origin_lng = Column(Float, nullable=True, default=120.3014)
    dest_lat = Column(Float, nullable=True, default=33.7420)
    dest_lng = Column(Float, nullable=True, default=-118.2673)

    @property
    def shipment_id(self) -> int:
        return self.id

    @property
    def delay_category(self) -> str:
        if self.delay_days == 0:
            return "ON_TIME"
        elif self.delay_days <= 2:
            return "MINOR_DELAY"
        else:
            return "CRITICAL_DELAY"

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(150), default="Default Item")
    sku = Column(String(50), default="SKU-GENERIC")
    current_stock = Column(Integer, default=1000)
    daily_demand = Column(Integer, default=50)
    reorder_level = Column(Integer, default=300)
    days_remaining = Column(Integer, default=20)
    stockout_risk = Column(String(20), default="Low")
    stockout_risk_level = Column(String(20), default="LOW")
    unit_cost = Column(Float, default=45.0)

InventoryItem = Inventory

class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), default="supplier")  # supplier, shipment, logistics
    entity_id = Column(Integer, nullable=True, default=1)
    title = Column(String(200), nullable=False, default="Supply Chain Risk")
    risk_type = Column(String(50), default="GENERAL")
    risk_score = Column(Integer, default=30)
    score = Column(Integer, default=30)
    severity = Column(String(20), default="Low")  # Low, Moderate, High, Critical
    risk_level = Column(String(20), default="Low")
    impact_description = Column(Text, nullable=True)
    risk_reason = Column(Text, nullable=True)
    probability = Column(Float, default=0.5)
    financial_impact = Column(Float, default=0.0)
    affected_supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    affected_shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)
    evidence = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)
    status = Column(String(30), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        if "score" in kwargs and "risk_score" not in kwargs:
            kwargs["risk_score"] = kwargs["score"]
        elif "risk_score" in kwargs and "score" not in kwargs:
            kwargs["score"] = kwargs["risk_score"]
        if "severity" in kwargs and "risk_level" not in kwargs:
            kwargs["risk_level"] = kwargs["severity"]
        elif "risk_level" in kwargs and "severity" not in kwargs:
            kwargs["severity"] = kwargs["risk_level"]
        if "risk_reason" in kwargs and "impact_description" not in kwargs:
            kwargs["impact_description"] = kwargs["risk_reason"]
        elif "impact_description" in kwargs and "risk_reason" not in kwargs:
            kwargs["risk_reason"] = kwargs["impact_description"]
        super().__init__(**kwargs)

RiskItem = Risk

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String(250), nullable=False)
    source = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    severity = Column(String(20), default="Low")
    impact = Column(Text, nullable=True)
    supply_chain_impact = Column(Text, nullable=True)
    affected_suppliers = Column(String(250), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

NewsEvent = Event

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), default="supplier")
    entity_id = Column(Integer, nullable=True, default=1)
    action_title = Column(String(200), nullable=False, default="Recommend Alternate Logistics")
    recommendation = Column(String(200), nullable=True)
    reasoning = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    confidence = Column(Float, default=0.90)
    confidence_score = Column(Float, default=0.90)
    priority = Column(String(20), default="High")
    expected_impact = Column(Text, nullable=True)
    financial_saving = Column(Float, default=0.0)
    delay_reduction_days = Column(Integer, default=0)
    alternative_actions = Column(Text, nullable=True)
    status = Column(String(30), default="PROPOSED")
    risk_id = Column(Integer, ForeignKey("risks.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        if "action_title" in kwargs and "recommendation" not in kwargs:
            kwargs["recommendation"] = kwargs["action_title"]
        elif "recommendation" in kwargs and "action_title" not in kwargs:
            kwargs["action_title"] = kwargs["recommendation"]
        if "reason" in kwargs and "reasoning" not in kwargs:
            kwargs["reasoning"] = kwargs["reason"]
        elif "reasoning" in kwargs and "reason" not in kwargs:
            kwargs["reason"] = kwargs["reasoning"]
        if "confidence_score" in kwargs and "confidence" not in kwargs:
            kwargs["confidence"] = kwargs["confidence_score"]
        elif "confidence" in kwargs and "confidence_score" not in kwargs:
            kwargs["confidence_score"] = kwargs["confidence"]
        super().__init__(**kwargs)

class Scenario(Base):
    __tablename__ = "scenarios"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="Default Scenario")
    scenario_name = Column(String(100), nullable=True)
    option_key = Column(String(50), nullable=True)
    cost_delta = Column(Float, default=0.0)
    delay_days = Column(Integer, default=0)
    risk_score = Column(Integer, default=30)
    net_impact = Column(String(250), nullable=True)
    is_recommended = Column(Boolean, default=False)
    details = Column(Text, nullable=True)

ScenarioResult = Scenario

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(100))
    file_path = Column(String(250))

class Compliance(Base):
    __tablename__ = "compliance"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    category = Column(String(100), default="POLICY")
    entity_name = Column(String(150), nullable=True)
    policy_name = Column(String(200), nullable=False, default="Standard Compliance Policy")
    status = Column(String(50), default="COMPLIANT")
    compliance_status = Column(String(50), default="COMPLIANT")
    penalty_risk = Column(Float, default=0.0)
    force_majeure_clause = Column(Text, nullable=True)
    required_actions = Column(Text, nullable=True)
    required_action = Column(Text, nullable=True)

ComplianceRecord = Compliance
