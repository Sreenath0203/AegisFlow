import os
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database.db import get_db
from ai_services.granite.watsonx_client import watsonx_client
from ai_services.services.chatbot_service import chatbot_service
from ai_services.services.watson_orchestrate_service import (
    watson_orchestrate_service
)
from ai_services.agents.location_agent import location_agent
from ai_services.agents.weather_agent import weather_agent


router = APIRouter(
    prefix="/ai",
    tags=["IBM watsonx.ai Granite Intelligence"]
)


# ============================================================
# RISK ANALYSIS MODELS
# ============================================================

class RiskAnalysisInput(BaseModel):
    supplier: str = Field(
        default="ABC Electronics",
        description="Supplier name"
    )

    shipment_delay_days: int = Field(
        default=4,
        description="Days of shipment delay"
    )

    inventory_days: int = Field(
        default=3,
        description="Days of buffer inventory remaining"
    )

    weather_risk: str = Field(
        default="Severe rainfall",
        description="Weather disruption factor"
    )

    supplier_reliability: float = Field(
        default=65.0,
        description="Supplier reliability score percentage"
    )


class RiskAnalysisOutput(BaseModel):
    risk_level: str
    risk_score: float
    reason: str
    recommendation: str
    confidence: float
    model_id: Optional[str] = None


# ============================================================
# CHAT MODELS
# ============================================================

class ChatInput(BaseModel):
    message: str = Field(
        ...,
        description="User query for supply chain intelligence"
    )

    conversation_history: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Previous messages in the conversation"
    )

    thread_id: Optional[str] = Field(
        default=None,
        description="IBM watsonx Orchestrate conversation thread ID"
    )


class ChatOutput(BaseModel):
    response: str
    tools_used: List[str]
    tool_data: Optional[Dict[str, Any]] = None
    model: str


# ============================================================
# EXISTING GRANITE RISK ANALYSIS
# ============================================================

@router.post(
    "/risk-analysis",
    response_model=RiskAnalysisOutput
)
def analyze_supply_chain_risk(
    payload: RiskAnalysisInput
):
    """
    Executes IBM watsonx.ai Granite model text generation
    for supply-chain risk analysis.
    """

    input_data = (
        payload.model_dump()
        if hasattr(payload, "model_dump")
        else payload.dict()
    )

    result = watsonx_client.analyze_risk(input_data)

    return result


# ============================================================
# EXISTING AEGISFLOW CHATBOT
# ============================================================

@router.post(
    "/chat",
    response_model=ChatOutput
)
def chat_with_ai(
    payload: ChatInput,
    db: Session = Depends(get_db)
):
    """
    Existing AegisFlow supply-chain AI chatbot.

    This endpoint is preserved so the existing chatbot
    functionality is not affected.
    """

    if not payload.message or not payload.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message string cannot be empty."
        )

    try:
        result = chatbot_service.process_chat_message(
            payload.message,
            db
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AegisFlow chatbot error: {str(exc)}"
        )


# ============================================================
# IBM WATSONX ORCHESTRATE CHAT
# ============================================================

@router.post("/orchestrate-chat")
def chat_with_watson_orchestrate(
    payload: ChatInput
):
    """
    Sends a user message to the deployed IBM watsonx
    Orchestrate AegisFlow agent.

    This endpoint is intentionally separate from /chat
    so the existing AegisFlow chatbot remains unaffected.
    """

    if not payload.message or not payload.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message string cannot be empty."
        )

    try:
        result = watson_orchestrate_service.chat(
            message=payload.message,
            conversation_history=payload.conversation_history,
            thread_id=payload.thread_id
        )

        # Return only the useful response information
        # to the frontend.
        return {
            "status": "success",
            "response": result.get("response", ""),
            "thread_id": result.get("thread_id"),
            "run_id": result.get("run_id"),
            "task_id": result.get("task_id"),
            "message_id": result.get("message_id")
        }

    except Exception as exc:
        error_message = str(exc)

        # Never expose the IBM API key.
        api_key = os.getenv(
            "WATSON_ORCHESTRATE_API_KEY",
            ""
        )

        if api_key:
            error_message = error_message.replace(
                api_key,
                "[REDACTED]"
            )

        raise HTTPException(
            status_code=502,
            detail=(
                "IBM watsonx Orchestrate request failed: "
                f"{error_message}"
            )
        )


# ============================================================
# LIVE WEATHER
# ============================================================

@router.get("/weather")
def get_live_location_weather(
    location: str = Query(
        ...,
        description="Location name or city"
    )
):
    """
    Retrieves live current weather observations
    through the AegisFlow Location and Weather Agents.
    """

    try:
        geo = location_agent.geocode(location)

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Location service error: {str(exc)}"
        )

    if geo.get("status") != "FOUND":
        raise HTTPException(
            status_code=404,
            detail=(
                f"Location '{location}' "
                "could not be geocoded."
            )
        )

    try:
        weather = weather_agent.get_weather(
            latitude=geo["latitude"],
            longitude=geo["longitude"],
            location=geo.get("resolved_name") or location
        )

        return weather

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Weather service error: {str(exc)}"
        )