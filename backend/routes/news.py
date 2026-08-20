from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.database.db import get_db
from backend.models.models import NewsEvent, Supplier, Shipment, InventoryItem, RiskItem
from backend.schemas.schemas import NewsOut
from ai_services.services.live_intelligence import live_intelligence_service
from ai_services.agents.news_agent import news_agent

router = APIRouter(prefix="/news", tags=["External News Events"])

@router.get("", response_model=List[NewsOut])
@router.get("/", response_model=List[NewsOut])
def list_news(
    severity: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(NewsEvent)
    if severity and severity.upper() != "ALL":
        query = query.filter(NewsEvent.severity.ilike(f"%{severity}%"))
    if location and location.upper() != "ALL":
        query = query.filter(
            (NewsEvent.location.ilike(f"%{location}%")) |
            (NewsEvent.headline.ilike(f"%{location}%")) |
            (NewsEvent.supply_chain_impact.ilike(f"%{location}%"))
        )
    return query.order_by(NewsEvent.created_at.desc()).all()

@router.post("/fetch")
def fetch_and_store_live_news(db: Session = Depends(get_db)):
    """
    Fetches real-time supply chain news via News Agent and stores in database avoiding duplicate headlines.
    """
    try:
        locations = live_intelligence_service.collect_locations(db)
        suppliers = live_intelligence_service.collect_suppliers(db)
        products = live_intelligence_service.collect_products(db)

        news_res = news_agent.search(
            locations=locations,
            suppliers=suppliers,
            products=products,
            industries=["supply chain", "logistics", "semiconductor", "shipping"],
            max_records=20
        )

        articles = news_res.get("articles", [])
        stored_count = 0

        for item in articles:
            headline = item.get("headline") or item.get("title")
            if not headline:
                continue

            existing = db.query(NewsEvent).filter(NewsEvent.headline == headline).first()
            if not existing:
                news_record = NewsEvent(
                    headline=headline,
                    source=item.get("source", "Global Logistics Feed"),
                    location=item.get("location", "Global Sea Lanes"),
                    severity=item.get("severity", "MEDIUM"),
                    impact=item.get("summary") or item.get("impact", "Potential maritime supply chain disruption."),
                    supply_chain_impact=item.get("summary") or item.get("impact", "Potential maritime supply chain disruption."),
                    affected_suppliers=item.get("affected_suppliers", "ABC Electronics Co.")
                )
                db.add(news_record)
                stored_count += 1
            else:
                existing.source = item.get("source", existing.source)
                existing.severity = item.get("severity", existing.severity)

        db.commit()
        return {
            "status": "SUCCESS",
            "new_articles_stored": stored_count,
            "total_articles": db.query(NewsEvent).count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch and store live news: {str(e)}")

@router.get("/impact-chain")
def get_news_impact_chain(db: Session = Depends(get_db)):
    """
    Returns a focused relationship chain: News -> Supplier -> Shipment -> Inventory -> Risk.
    Capped at 5 news events; each event maps to at most 3 suppliers, 4 shipments,
    3 inventory items, and 2 risks — to keep the UI readable.
    """
    # Load top-5 most recent HIGH/CRITICAL news events first, then fill with others
    all_news = db.query(NewsEvent).order_by(NewsEvent.created_at.desc()).all()
    # Prioritise CRITICAL and HIGH
    priority_news = [n for n in all_news if (n.severity or "").upper() in ("CRITICAL", "HIGH")]
    other_news    = [n for n in all_news if (n.severity or "").upper() not in ("CRITICAL", "HIGH")]
    top_news = (priority_news + other_news)[:5]

    # Pre-load all data once
    all_suppliers = db.query(Supplier).all()
    all_shipments = db.query(Shipment).all()
    all_inventory = (
        db.query(InventoryItem)
        .filter(InventoryItem.days_remaining <= 14)
        .order_by(InventoryItem.days_remaining)
        .limit(20)
        .all()
    )
    active_risks = (
        db.query(RiskItem)
        .filter(RiskItem.status == "ACTIVE")
        .order_by(RiskItem.risk_score.desc())
        .limit(20)
        .all()
    )

    chain = []
    for news in top_news:
        affected_text = (news.affected_suppliers or "").lower()
        location_text = (news.location or "").lower()

        # --- Match suppliers (max 3) ----------------------------------------
        matched_suppliers = []
        for s in all_suppliers:
            name_lower = s.name.lower()
            if name_lower in affected_text or any(
                part.strip() in name_lower
                for part in affected_text.split(",")
                if len(part.strip()) > 4
            ):
                matched_suppliers.append({
                    "id": s.id,
                    "name": s.name,
                    "risk_level": s.current_risk_level or s.risk_level,
                    "reliability": s.reliability_score,
                })
            if len(matched_suppliers) == 3:
                break

        # Fallback: country match if no name match
        if not matched_suppliers:
            for s in all_suppliers:
                if s.country and s.country.lower() in location_text:
                    matched_suppliers.append({
                        "id": s.id,
                        "name": s.name,
                        "risk_level": s.current_risk_level or s.risk_level,
                        "reliability": s.reliability_score,
                    })
                if len(matched_suppliers) == 2:
                    break

        matched_supplier_ids = {s["id"] for s in matched_suppliers}

        # --- Match shipments (max 4, only from matched suppliers) -----------
        matched_shipments = []
        for sh in all_shipments:
            if sh.supplier_id in matched_supplier_ids:
                matched_shipments.append({
                    "code": sh.shipment_code,
                    "status": sh.status,
                    "delay_days": sh.delay_days,
                    "risk_level": sh.risk_level,
                })
            if len(matched_shipments) == 4:
                break

        # --- Match inventory (max 3, lowest days_remaining first) -----------
        matched_inventory = []
        for inv in all_inventory:
            matched_inventory.append({
                "product_name": inv.product_name,
                "sku": inv.sku,
                "days_remaining": inv.days_remaining,
                "stockout_risk": inv.stockout_risk,
            })
            if len(matched_inventory) == 3:
                break

        # --- Match risks (max 2, highest score first) -----------------------
        matched_risks = []
        for r in active_risks:
            if r.affected_supplier_id in matched_supplier_ids or not matched_supplier_ids:
                matched_risks.append({
                    "id": r.id,
                    "title": r.title,
                    "severity": r.severity or r.risk_level,
                    "impact": r.impact_description,
                })
            if len(matched_risks) == 2:
                break

        # Fallback: just take top-2 active risks if none matched by supplier
        if not matched_risks:
            matched_risks = [
                {
                    "id": r.id,
                    "title": r.title,
                    "severity": r.severity or r.risk_level,
                    "impact": r.impact_description,
                }
                for r in active_risks[:2]
            ]

        chain.append({
            "news": {
                "id": news.id,
                "headline": news.headline,
                "source": news.source,
                "location": news.location,
                "severity": news.severity,
                "impact": news.supply_chain_impact or news.impact,
                "created_at": news.created_at.isoformat() if news.created_at else None
            },
            "suppliers": matched_suppliers,
            "shipments": matched_shipments,
            "inventory": matched_inventory,
            "risks": matched_risks,
        })

    return chain
