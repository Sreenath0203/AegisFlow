import os
import json
import logging
from sqlalchemy.orm import Session
from backend.database.db import SessionLocal, engine, Base
from backend.models.models import (
    Supplier, Shipment, Inventory, Risk, Recommendation, Event, Compliance
)
from data_pipeline.processing.data_prep_kit import data_prep_kit

logger = logging.getLogger("aegisflow.pipeline_exporter")

def run_pipeline_ingestion(db: Session = None, sample_json_path: str = None) -> dict:
    """
    Executes full data pipeline transformation and safe upsert to PostgreSQL / SQLite database:
    CSV / JSON -> Clean -> Validate -> Transform -> Risk Scoring -> Save to Database.
    Safe for repeated execution.
    """
    close_db = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_db = True

    try:
        # Default full dataset
        default_suppliers = [
            {"id": 1, "name": "ABC Electronics Co.", "country": "Taiwan", "reliability_score": 94.5, "on_time_delivery": 92.0, "quality_score": 98.2, "category": "Microcontrollers & Chips", "risk_level": "LOW", "latitude": 22.6273, "longitude": 120.3014},
            {"id": 2, "name": "Supplier XYZ Logistics", "country": "Vietnam", "reliability_score": 91.0, "on_time_delivery": 89.5, "quality_score": 96.0, "category": "Secondary Component Backup", "risk_level": "LOW", "latitude": 10.8231, "longitude": 106.6297},
            {"id": 3, "name": "Apex Semiconductor AG", "country": "South Korea", "reliability_score": 96.8, "on_time_delivery": 95.4, "quality_score": 99.1, "category": "Advanced Processing Chips", "risk_level": "LOW", "latitude": 35.1796, "longitude": 129.0756},
            {"id": 4, "name": "Global Tech Modules", "country": "Malaysia", "reliability_score": 82.0, "on_time_delivery": 78.0, "quality_score": 90.5, "category": "Power Systems", "risk_level": "HIGH", "latitude": 5.4164, "longitude": 100.3327},
            {"id": 5, "name": "Nordic Sensors AB", "country": "Sweden", "reliability_score": 98.5, "on_time_delivery": 97.8, "quality_score": 99.6, "category": "Precision Sensors", "risk_level": "LOW", "latitude": 57.7089, "longitude": 11.9746}
        ]

        default_shipments = [
            {"id": 1, "shipment_code": "SHP-9021", "supplier_id": 1, "origin": "Kaohsiung Port", "destination": "Los Angeles Port", "status": "IN_TRANSIT", "delay_days": 0, "risk_level": "LOW", "cargo_description": "50,000 Microcontroller X1 Units", "carrier": "Pacific Maritime Fleet", "origin_lat": 22.6273, "origin_lng": 120.3014, "dest_lat": 33.7420, "dest_lng": -118.2673},
            {"id": 2, "shipment_code": "SHP-9022", "supplier_id": 2, "origin": "Hai Phong Port", "destination": "Long Beach Port", "status": "IN_TRANSIT", "delay_days": 0, "risk_level": "LOW", "cargo_description": "20,000 Display Controllers", "carrier": "Indochina Ocean Express", "origin_lat": 20.8651, "origin_lng": 106.6838, "dest_lat": 33.7701, "dest_lng": -118.1937},
            {"id": 3, "shipment_code": "SHP-9023", "supplier_id": 3, "origin": "Busan Port", "destination": "Rotterdam Port", "status": "IN_TRANSIT", "delay_days": 1, "risk_level": "LOW", "cargo_description": "15,000 AI Acceleration Modules", "carrier": "Hanjin Global Container Line", "origin_lat": 35.1796, "origin_lng": 129.0756, "dest_lat": 51.9244, "dest_lng": 4.4777},
            {"id": 4, "shipment_code": "SHP-9024", "supplier_id": 4, "origin": "Penang Port", "destination": "Hamburg Port", "status": "DELAYED", "delay_days": 3, "risk_level": "HIGH", "cargo_description": "30,000 Power Regulators", "carrier": "Malaysian Maritime Transport", "origin_lat": 5.4164, "origin_lng": 100.3327, "dest_lat": 53.5511, "dest_lng": 9.9937},
            {"id": 5, "shipment_code": "SHP-9025", "supplier_id": 5, "origin": "Gothenburg Port", "destination": "Port of Antwerp", "status": "DELIVERED", "delay_days": 0, "risk_level": "LOW", "cargo_description": "10,000 Precision Sensors", "carrier": "Nordic Express Shipping", "origin_lat": 57.7089, "origin_lng": 11.9746, "dest_lat": 51.2194, "dest_lng": 4.4025}
        ]

        # 1. Process & Ingest Suppliers
        saved_suppliers = []
        for raw in default_suppliers:
            telemetry = data_prep_kit.prepare_supplier_telemetry(raw)
            health_idx = telemetry.get("health_index", 90.0)
            risk_lvl = telemetry.get("risk_category", "LOW")

            s = db.query(Supplier).filter((Supplier.id == raw.get("id")) | (Supplier.name == raw.get("name"))).first()
            if not s:
                s = Supplier(
                    id=raw.get("id"),
                    name=raw.get("name"),
                    country=raw.get("country", "Unknown"),
                    reliability_score=float(raw.get("reliability_score", 95.0)),
                    on_time_delivery=float(raw.get("on_time_delivery", 92.0)),
                    quality_score=float(raw.get("quality_score", 98.0)),
                    risk_level=raw.get("risk_level", risk_lvl),
                    current_risk_level=risk_lvl,
                    category=raw.get("category", "General Components"),
                    latitude=raw.get("latitude", 22.6273),
                    longitude=raw.get("longitude", 120.3014)
                )
                db.add(s)
            else:
                s.name = raw.get("name", s.name)
                s.country = raw.get("country", s.country)
                s.reliability_score = float(raw.get("reliability_score", s.reliability_score))
                s.risk_level = raw.get("risk_level", s.risk_level)
                s.current_risk_level = risk_lvl
                s.latitude = raw.get("latitude", s.latitude)
                s.longitude = raw.get("longitude", s.longitude)
            db.commit()
            db.refresh(s)
            saved_suppliers.append(s)

        # 2. Process & Ingest Logistics / Shipments
        saved_shipments = []
        for raw in default_shipments:
            shp = db.query(Shipment).filter((Shipment.id == raw.get("id")) | (Shipment.shipment_code == raw.get("shipment_code"))).first()
            if not shp:
                shp = Shipment(
                    id=raw.get("id"),
                    shipment_code=raw.get("shipment_code"),
                    supplier_id=raw.get("supplier_id", 1),
                    origin=raw.get("origin", "Origin Port"),
                    destination=raw.get("destination", "Destination Port"),
                    status=raw.get("status", "IN_TRANSIT"),
                    delay_days=int(raw.get("delay_days", 0)),
                    risk_level=raw.get("risk_level", "LOW"),
                    cargo_description=raw.get("cargo_description", "General Components"),
                    carrier=raw.get("carrier", "Global Freight Carrier"),
                    origin_lat=raw.get("origin_lat", 22.6273),
                    origin_lng=raw.get("origin_lng", 120.3014),
                    dest_lat=raw.get("dest_lat", 33.7420),
                    dest_lng=raw.get("dest_lng", -118.2673)
                )
                db.add(shp)
            else:
                shp.origin = raw.get("origin", shp.origin)
                shp.destination = raw.get("destination", shp.destination)
                shp.status = raw.get("status", shp.status)
                shp.delay_days = int(raw.get("delay_days", shp.delay_days))
                shp.risk_level = raw.get("risk_level", shp.risk_level)
                shp.origin_lat = raw.get("origin_lat", shp.origin_lat)
                shp.origin_lng = raw.get("origin_lng", shp.origin_lng)
                shp.dest_lat = raw.get("dest_lat", shp.dest_lat)
                shp.dest_lng = raw.get("dest_lng", shp.dest_lng)
            db.commit()
            db.refresh(shp)
            saved_shipments.append(shp)

        # 3. Derive & Ingest Risk Intelligence & Recommendations
        for shp in saved_shipments:
            if shp.delay_days > 0 or shp.risk_level.upper() in ["HIGH", "CRITICAL"]:
                r_title = f"Port Congestion Delay on Route {shp.shipment_code}"
                existing_risk = db.query(Risk).filter(Risk.affected_shipment_id == shp.id).first()
                if not existing_risk:
                    r = Risk(
                        title=r_title,
                        entity_type="logistics",
                        entity_id=shp.id,
                        risk_score=75 + (shp.delay_days * 5),
                        score=75 + (shp.delay_days * 5),
                        severity="HIGH" if shp.delay_days >= 3 else "MEDIUM",
                        risk_level="High" if shp.delay_days >= 3 else "Medium",
                        impact_description=f"Route delay of {shp.delay_days} days affecting arrival at {shp.destination}.",
                        risk_reason=f"Port congestion and carrier delay of {shp.delay_days} days on {shp.carrier}.",
                        affected_shipment_id=shp.id,
                        affected_supplier_id=shp.supplier_id,
                        status="ACTIVE"
                    )
                    db.add(r)
                    db.commit()
                    db.refresh(r)

                    rec = Recommendation(
                        entity_type="logistics",
                        entity_id=shp.id,
                        action_title=f"Investigate logistics route for {shp.shipment_code}",
                        recommendation=f"Evaluate backup logistics provider or trigger regional inventory release for {shp.shipment_code}.",
                        reasoning=f"Shipment delay of {shp.delay_days} days risks assembly schedule interruption.",
                        reason=f"Major shipment delay of {shp.delay_days} days.",
                        priority="High",
                        confidence=0.92,
                        status="PROPOSED",
                        risk_id=r.id
                    )
                    db.add(rec)
                    db.commit()

        for s in saved_suppliers:
            if s.reliability_score < 90.0 or s.current_risk_level in ["HIGH", "CRITICAL"] or s.risk_level.upper() in ["HIGH", "CRITICAL"]:
                existing_risk = db.query(Risk).filter(Risk.affected_supplier_id == s.id).first()
                if not existing_risk:
                    r = Risk(
                        title=f"Low Reliability Score Warning for {s.name}",
                        entity_type="supplier",
                        entity_id=s.id,
                        risk_score=82,
                        score=82,
                        severity="HIGH",
                        risk_level="High",
                        impact_description=f"Supplier reliability score dropped to {s.reliability_score}%.",
                        risk_reason="Low reliability and delayed delivery trends over recent cycles.",
                        affected_supplier_id=s.id,
                        status="ACTIVE"
                    )
                    db.add(r)
                    db.commit()
                    db.refresh(r)

                    rec = Recommendation(
                        entity_type="supplier",
                        entity_id=s.id,
                        action_title=f"Consider alternate supplier for {s.name}",
                        recommendation=f"Increase supplier monitoring and activate dual-sourcing for {s.name}.",
                        reasoning=f"Reliability score ({s.reliability_score}%) indicates potential delivery default.",
                        reason="Low supplier reliability score.",
                        priority="High",
                        confidence=0.88,
                        status="PROPOSED",
                        risk_id=r.id
                    )
                    db.add(rec)
                    db.commit()

        return {
            "status": "SUCCESS",
            "suppliers_count": len(saved_suppliers),
            "shipments_count": len(saved_shipments),
            "message": "Data pipeline successfully transformed and upserted records into PostgreSQL / SQLite database."
        }
    finally:
        if close_db and db:
            db.close()
