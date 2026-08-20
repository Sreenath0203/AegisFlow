from sqlalchemy.orm import Session
from backend.models.models import (
    Supplier, Shipment, InventoryItem, RiskItem, Recommendation,
    ComplianceRecord, NewsEvent, ScenarioResult
)
import logging

logger = logging.getLogger("aegisflow.seed")

def seed_database(db: Session):
    # Check if already seeded
    if db.query(Supplier).count() > 0:
        logger.info("Database already contains data. Skipping seed.")
        return

    logger.info("Seeding initial supply chain demo dataset...")

    # 1. Suppliers
    s1 = Supplier(
        name="ABC Electronics Co.",
        country="Taiwan",
        reliability_score=94.5,
        on_time_delivery=92.0,
        quality_score=98.2,
        current_risk_level="LOW",
        contact_email="supply@abcelectronics.tw",
        category="Microcontrollers & Chips"
    )
    s2 = Supplier(
        name="Supplier XYZ Logistics",
        country="Vietnam",
        reliability_score=91.0,
        on_time_delivery=89.5,
        quality_score=96.0,
        current_risk_level="LOW",
        contact_email="dispatch@supplierxyz.vn",
        category="Secondary Component Backup"
    )
    s3 = Supplier(
        name="Apex Semiconductor AG",
        country="South Korea",
        reliability_score=96.8,
        on_time_delivery=95.4,
        quality_score=99.1,
        current_risk_level="LOW",
        contact_email="orders@apexsemi.kr",
        category="Advanced Processing Chips"
    )
    s4 = Supplier(
        name="Global Tech Modules",
        country="Malaysia",
        reliability_score=88.0,
        on_time_delivery=85.0,
        quality_score=93.5,
        current_risk_level="MEDIUM",
        contact_email="info@globaltech.my",
        category="Power Systems"
    )
    s5 = Supplier(
        name="Nordic Sensors AB",
        country="Sweden",
        reliability_score=98.5,
        on_time_delivery=97.8,
        quality_score=99.6,
        current_risk_level="LOW",
        contact_email="logistics@nordicsensors.se",
        category="Precision Sensors"
    )
    db.add_all([s1, s2, s3, s4, s5])
    db.commit()

    # 2. Shipments
    sh1 = Shipment(
        shipment_code="SHP-9021",
        supplier_id=s1.id,
        origin="Kaohsiung Port, Taiwan",
        destination="Los Angeles Port, USA",
        status="IN_TRANSIT",
        delay_days=0,
        risk_level="LOW",
        cargo_description="50,000 Microcontroller X1 Units",
        carrier="Pacific Maritime Fleet"
    )
    sh2 = Shipment(
        shipment_code="SHP-9022",
        supplier_id=s2.id,
        origin="Hai Phong Port, Vietnam",
        destination="Long Beach Port, USA",
        status="IN_TRANSIT",
        delay_days=0,
        risk_level="LOW",
        cargo_description="20,000 Display Controllers",
        carrier="Indochina Ocean Express"
    )
    sh3 = Shipment(
        shipment_code="SHP-9023",
        supplier_id=s3.id,
        origin="Busan Port, South Korea",
        destination="Rotterdam Port, Netherlands",
        status="IN_TRANSIT",
        delay_days=1,
        risk_level="LOW",
        cargo_description="15,000 AI Acceleration Modules",
        carrier="Hanjin Global Container Line"
    )
    sh4 = Shipment(
        shipment_code="SHP-9024",
        supplier_id=s4.id,
        origin="Penang Port, Malaysia",
        destination="Hamburg Port, Germany",
        status="IN_TRANSIT",
        delay_days=2,
        risk_level="MEDIUM",
        cargo_description="30,000 Power Regulators",
        carrier="Malaysian Maritime Transport"
    )
    db.add_all([sh1, sh2, sh3, sh4])
    db.commit()

    # 3. Inventory
    inv1 = InventoryItem(
        product_name="Microcontroller X1",
        sku="MCU-X1-88",
        current_stock=150,
        daily_demand=50,
        days_remaining=3,
        reorder_level=500,
        stockout_risk_level="MEDIUM",
        unit_cost=45.0
    )
    inv2 = InventoryItem(
        product_name="Display Controller D2",
        sku="DSP-D2-44",
        current_stock=1200,
        daily_demand=40,
        days_remaining=30,
        reorder_level=400,
        stockout_risk_level="LOW",
        unit_cost=28.5
    )
    inv3 = InventoryItem(
        product_name="Memory Module M8",
        sku="MEM-M8-12",
        current_stock=850,
        daily_demand=35,
        days_remaining=24,
        reorder_level=300,
        stockout_risk_level="LOW",
        unit_cost=62.0
    )
    inv4 = InventoryItem(
        product_name="Power Regulator P1",
        sku="PWR-P1-09",
        current_stock=400,
        daily_demand=25,
        days_remaining=16,
        reorder_level=200,
        stockout_risk_level="LOW",
        unit_cost=18.0
    )
    db.add_all([inv1, inv2, inv3, inv4])
    db.commit()

    # 4. News Events
    n1 = NewsEvent(
        headline="Port Congestion Reported at European Terminals",
        source="Maritime Executive",
        location="Rotterdam, Netherlands",
        severity="LOW",
        supply_chain_impact="Minor 1-2 day delay on westbound freight due to labor schedule adjustments.",
        affected_suppliers="Apex Semiconductor AG"
    )
    n2 = NewsEvent(
        headline="Semiconductor Raw Material Prices Stabilize in Q3",
        source="Tech Supply Journal",
        location="Global",
        severity="LOW",
        supply_chain_impact="Favorable pricing outlook for upcoming silicon wafer production cycles.",
        affected_suppliers="Global Industry Wide"
    )
    db.add_all([n1, n2])
    db.commit()

    # 5. Compliance Records
    c1 = ComplianceRecord(
        title="ABC Electronics Master Supply Agreement (MSA-2025)",
        category="CONTRACT",
        entity_name="ABC Electronics Co.",
        compliance_status="COMPLIANT",
        penalty_risk=15000.0,
        force_majeure_clause="Clause 14.2: Excuses performance delay only if storm advisory > Category 3 issued by national agency within 24h notice.",
        required_action="Monitor East Asia weather bulletins and file written notice within 24h of severe disruption."
    )
    c2 = ComplianceRecord(
        title="EU Corporate Sustainability Due Diligence (CSDDD)",
        category="REGULATION",
        entity_name="European Union Operations",
        compliance_status="COMPLIANT",
        penalty_risk=50000.0,
        force_majeure_clause="N/A",
        required_action="Annual carbon emissions audit required for all tier-1 shipping lines."
    )
    c3 = ComplianceRecord(
        title="Multi-Sourcing Governance Policy (POL-SUP-04)",
        category="POLICY",
        entity_name="Internal Procurement",
        compliance_status="AT_RISK",
        penalty_risk=0.0,
        force_majeure_clause="N/A",
        required_action="Rebalance Microcontroller X1 order volume to maintain at least 30% secondary supplier allocation."
    )
    db.add_all([c1, c2, c3])
    db.commit()

    # 6. Baseline Risk & Recommendation
    r1 = RiskItem(
        title="Minor Port Schedule Delay on Route SHP-9024",
        risk_score=35,
        risk_type="LOGISTICS",
        probability=0.4,
        severity="LOW",
        financial_impact=12000.0,
        affected_supplier_id=s4.id,
        affected_shipment_id=sh4.id,
        evidence="Port congestion advisory at Hamburg terminal + 2 days carrier delay.",
        ai_explanation="IBM Granite analysis: Low severity logistics bottleneck. Buffer stock for Power Regulator P1 (16 days) exceeds predicted 2-day port delay.",
        status="ACTIVE"
    )
    db.add(r1)
    db.commit()

    rec1 = Recommendation(
        action_title="Maintain Standard Monitoring for SHP-9024",
        reason="Current inventory buffer (16 days remaining) easily absorbs the estimated 2-day Hamburg port delay.",
        confidence_score=0.92,
        expected_impact="Zero operational impact on assembly line.",
        financial_saving=0.0,
        delay_reduction_days=0,
        alternative_actions='[{"option": "Air Freight Expedite", "cost": "$15,000", "verdict": "Unnecessary expense"}]',
        status="PROPOSED",
        risk_id=r1.id
    )
    db.add(rec1)
    db.commit()

    logger.info("Seed data successfully created.")
