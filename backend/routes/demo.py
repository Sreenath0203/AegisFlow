from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db
from ai_services.services.ai_orchestrator import ai_orchestrator

router = APIRouter(prefix="/demo", tags=["End-to-End Demo Trigger"])

@router.post("/trigger-typhoon-scenario")
def trigger_typhoon_demo(db: Session = Depends(get_db)):
    """
    Executes live Typhoon Weather Disruption End-to-End Scenario:
    News Event -> Supplier Risk -> Compliance Check -> IBM watsonx RAG -> IBM Granite LLM Reasoning -> Decision Agent Strategy & Recommendations.
    """
    result = ai_orchestrator.run_typhoon_demo_scenario(db)
    return {
        "status": "SUCCESS",
        "message": "Typhoon Weather Disruption End-to-End Multi-Agent Pipeline Executed Successfully.",
        "payload": result
    }
