from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.db import get_db
from backend.models.models import ScenarioResult
from backend.schemas.schemas import ScenarioResultOut

router = APIRouter(prefix="/scenarios", tags=["What-If Scenario Simulation"])


def _attach_disruption_type(scenario) -> dict:
    """
    Derive disruption_type and clean scenario_name from the name field.
    Name format: "DISRUPTION_TYPE:Option Name"
    Falls back gracefully for legacy rows without a colon prefix.
    """
    raw_name = scenario.name or ""
    if ":" in raw_name:
        parts = raw_name.split(":", 1)
        d_type = parts[0].strip()
        s_name = parts[1].strip()
    else:
        d_type = "SUPPLIER_FAILURE"
        s_name = scenario.scenario_name or raw_name or "Scenario Option"

    return {
        "id": scenario.id,
        "name": scenario.name,
        "scenario_name": s_name,
        "option_key": scenario.option_key,
        "cost_delta": scenario.cost_delta,
        "delay_days": scenario.delay_days,
        "risk_score": scenario.risk_score,
        "net_impact": scenario.net_impact,
        "is_recommended": scenario.is_recommended,
        "details": scenario.details,
        "disruption_type": d_type,
    }


@router.get("", response_model=List[ScenarioResultOut])
@router.get("/", response_model=List[ScenarioResultOut])
def list_scenarios(
    disruption_type: Optional[str] = Query(
        None,
        description="Filter by disruption type. E.g. SUPPLIER_FAILURE, PORT_STRIKE, TYPHOON_DISRUPTION"
    ),
    db: Session = Depends(get_db)
):
    query = db.query(ScenarioResult)

    if disruption_type:
        # name column stores "DISRUPTION_TYPE:Option Name"
        query = query.filter(
            ScenarioResult.name.like(f"{disruption_type.upper()}:%")
        )

    scenarios = query.order_by(ScenarioResult.id).all()

    if not scenarios:
        # Fallback baseline scenario options (shown when DB is empty)
        return [
            {
                "id": 1,
                "scenario_name": "Do Nothing",
                "option_key": "DO_NOTHING",
                "cost_delta": 0.0,
                "delay_days": 5,
                "risk_score": 92,
                "net_impact": "-$180,000 Line Stoppage",
                "is_recommended": False,
                "details": "High probability of assembly line outage on day 3.",
                "disruption_type": "SUPPLIER_FAILURE",
            },
            {
                "id": 2,
                "scenario_name": "Switch Procurement (40% to Supplier XYZ)",
                "option_key": "SWITCH_SUPPLIER",
                "cost_delta": 14200.0,
                "delay_days": 0,
                "risk_score": 24,
                "net_impact": "+$165,800 Net Saved",
                "is_recommended": True,
                "details": "Leverages contracted backup capacity in Vietnam. Fully mitigates line stoppage.",
                "disruption_type": "SUPPLIER_FAILURE",
            },
            {
                "id": 3,
                "scenario_name": "Expedite Shipment via Air Freight",
                "option_key": "EXPEDITE_SHIPMENT",
                "cost_delta": 48000.0,
                "delay_days": 1,
                "risk_score": 45,
                "net_impact": "+$132,000 Net Saved",
                "is_recommended": False,
                "details": "Air charter expedites delivery but incurs significant freight surcharge.",
                "disruption_type": "SUPPLIER_FAILURE",
            },
        ]

    return [_attach_disruption_type(s) for s in scenarios]
