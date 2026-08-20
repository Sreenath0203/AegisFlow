import re
import logging
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models.models import Supplier, Shipment, InventoryItem, Risk, NewsEvent
from ai_services.agents.location_agent import location_agent
from ai_services.agents.weather_agent import weather_agent
from ai_services.agents.news_agent import news_agent
from ai_services.granite.watsonx_client import watsonx_client

logger = logging.getLogger("aegisflow.chatbot")

# ---------------------------------------------------------------------------
# Location keywords → canonical query string used for geocoding / news
# ---------------------------------------------------------------------------
_LOCATION_KEYWORDS: List[tuple] = [
    (["kaohsiung"], "Kaohsiung, Taiwan"),
    (["taipei"], "Taipei, Taiwan"),
    (["taiwan", "taiwanese"], "Taiwan"),
    (["malaysia", "penang", "kuala lumpur", "kl"], "Malaysia"),
    (["vietnam", "ho chi minh", "hanoi"], "Vietnam"),
    (["korea", "south korea", "busan", "seoul"], "South Korea"),
    (["japan", "osaka", "tokyo"], "Japan"),
    (["china", "shenzhen", "guangzhou", "shanghai"], "China"),
    (["europe", "rotterdam", "hamburg"], "Europe"),
    (["usa", "united states", "los angeles", "long beach"], "United States"),
]

def _extract_location(msg_lower: str) -> Optional[str]:
    """Return the best-matching location string from the user message or None."""
    for keywords, canonical in _LOCATION_KEYWORDS:
        if any(kw in msg_lower for kw in keywords):
            return canonical
    return None


def _extract_news_topic(msg_lower: str) -> str:
    """Return a focused news search topic based on user message."""
    loc = _extract_location(msg_lower)
    if loc:
        return loc
    for kw in ["semiconductor", "chip", "microchip", "electronics"]:
        if kw in msg_lower:
            return "semiconductor supply chain"
    for kw in ["shipping", "freight", "container", "port"]:
        if kw in msg_lower:
            return "global shipping disruption"
    return "supply chain disruption"


def _trim_list(data: list, max_items: int = 8) -> list:
    """Keep only the most relevant items to avoid bloating the LLM prompt."""
    return data[:max_items]


class ChatbotService:
    """
    AegisFlow Supply-Chain AI Chatbot Service.
    Intelligently maps natural language user queries to AegisFlow backend & IBM tools,
    executes live database / external tool queries, and synthesizes clear, executive,
    business-friendly responses using IBM Granite (watsonx.ai).
    """

    def tool_get_inventory(self, db: Session) -> Dict[str, Any]:
        items = db.query(InventoryItem).all()
        return {
            "tool": "Get inventory",
            "count": len(items),
            "data": _trim_list([
                {
                    "product_name": item.product_name,
                    "sku": item.sku,
                    "current_stock": item.current_stock,
                    "daily_demand": item.daily_demand,
                    "reorder_level": item.reorder_level,
                    "days_remaining": item.days_remaining,
                    "stockout_risk": item.stockout_risk or item.stockout_risk_level or "Low",
                    "unit_cost": item.unit_cost
                }
                for item in items
            ])
        }

    def tool_get_suppliers(self, db: Session) -> Dict[str, Any]:
        suppliers = db.query(Supplier).all()
        return {
            "tool": "Get supply-chain suppliers",
            "count": len(suppliers),
            "data": _trim_list([
                {
                    "id": s.id,
                    "name": s.name,
                    "country": s.country,
                    "reliability_score": s.reliability_score,
                    "current_risk_level": s.current_risk_level or s.risk_level or "LOW",
                    "category": s.category,
                    "on_time_delivery": s.on_time_delivery
                }
                for s in suppliers
            ])
        }

    def tool_get_shipments(self, db: Session) -> Dict[str, Any]:
        shipments = db.query(Shipment).all()
        return {
            "tool": "Get shipments",
            "count": len(shipments),
            "data": _trim_list([
                {
                    "shipment_code": shp.shipment_code,
                    "supplier_id": shp.supplier_id,
                    "origin": shp.origin,
                    "destination": shp.destination,
                    "status": shp.status,
                    "delay_days": shp.delay_days,
                    "risk_level": shp.risk_level,
                    "cargo_description": shp.cargo_description,
                    "carrier": shp.carrier
                }
                for shp in shipments
            ])
        }

    def tool_get_risks(self, db: Session) -> Dict[str, Any]:
        risks = db.query(Risk).all()
        return {
            "tool": "Get supply-chain risks",
            "count": len(risks),
            "data": _trim_list([
                {
                    "id": r.id,
                    "title": r.title,
                    "entity_type": r.entity_type,
                    "risk_score": r.risk_score,
                    "severity": r.severity or r.risk_level or "Low",
                    "impact_description": (r.impact_description or r.risk_reason or "")[:200],
                    "status": r.status
                }
                for r in risks
            ])
        }

    def tool_get_weather(self, location_name: str = "Kaohsiung, Taiwan") -> Dict[str, Any]:
        geo = location_agent.geocode(location_name)
        if geo.get("status") == "FOUND":
            weather = weather_agent.get_weather(
                geo["latitude"],
                geo["longitude"],
                geo.get("resolved_name") or location_name
            )
            return {
                "tool": "Get live weather for a location",
                "location": location_name,
                "data": weather
            }
        return {
            "tool": "Get live weather for a location",
            "location": location_name,
            "data": {"status": "NOT_FOUND", "message": f"Could not geocode location '{location_name}'"}
        }

    def tool_search_news(self, db: Session, query_topic: str = "Taiwan") -> Dict[str, Any]:
        db_news = db.query(NewsEvent).all()
        news_list = [
            {
                "headline": n.headline,
                "source": n.source,
                "location": n.location,
                "severity": n.severity,
                "impact": (n.supply_chain_impact or n.impact or "")[:200],
                "affected_suppliers": n.affected_suppliers
            }
            for n in db_news
        ]

        # Also attempt live news agent query
        try:
            live_news = news_agent.search(
                locations=[query_topic],
                suppliers=[],
                products=[],
                industries=["supply chain", "shipping", "semiconductor"]
            )
            if live_news and isinstance(live_news, dict) and "articles" in live_news:
                news_list.extend([
                    {
                        "headline": a.get("title"),
                        "source": a.get("source"),
                        "location": query_topic,
                        "severity": "HIGH",
                        "impact": (a.get("summary") or "")[:200],
                        "affected_suppliers": "Global Supply Nodes"
                    }
                    for a in live_news.get("articles", [])[:3]
                ])
        except Exception:
            pass

        return {
            "tool": "Search live global supply chain news",
            "topic": query_topic,
            "count": len(news_list),
            "data": _trim_list(news_list)
        }

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def process_chat_message(self, user_message: str, db: Session) -> Dict[str, Any]:
        """
        Main Chatbot Entry Point.
        Identifies user intent, selects and executes AegisFlow tools,
        and uses IBM Granite to format an executive business response.
        """
        msg_lower = user_message.lower().strip()

        tools_to_run: set = set()
        executed_tool_data: Dict[str, Any] = {}

        # ------------------------------------------------------------------
        # 1. Intent Detection & Tool Selection
        # ------------------------------------------------------------------
        if any(w in msg_lower for w in [
            "inventory", "stock", "stockout", "product", "sku",
            "mcu", "microcontroller", "runway", "component", "parts"
        ]):
            tools_to_run.add("inventory")

        if any(w in msg_lower for w in [
            "supplier", "vendor", "abc electronics", "reliability",
            "partner", "manufacturer", "factory"
        ]):
            tools_to_run.add("suppliers")

        # Location keywords also need supplier context (e.g. "Taiwan suppliers")
        if _extract_location(msg_lower):
            tools_to_run.add("suppliers")

        if any(w in msg_lower for w in [
            "shipment", "shipments", "delay", "delayed", "freight",
            "transit", "carrier", "prioritize", "shipping", "cargo", "route"
        ]):
            tools_to_run.add("shipments")

        if any(w in msg_lower for w in [
            "risk", "risks", "critical", "problem", "threat",
            "disruption", "issue", "action", "recommend", "danger", "alert"
        ]):
            tools_to_run.add("risks")

        if any(w in msg_lower for w in [
            "weather", "rain", "rainfall", "typhoon", "storm",
            "temperature", "wind", "forecast", "climate"
        ]):
            tools_to_run.add("weather")

        if any(w in msg_lower for w in [
            "news", "event", "headline", "breaking", "article",
            "latest", "update", "current events"
        ]):
            tools_to_run.add("news")

        # Comprehensive / fallback: run all core tools
        _comprehensive = (
            len(tools_to_run) == 0
            or "microcontroller x1" in msg_lower
            or "summary" in msg_lower
            or "overall" in msg_lower
            or "what is happening" in msg_lower
            or "biggest" in msg_lower
            or "give me" in msg_lower
        )
        if _comprehensive:
            tools_to_run.update(["inventory", "suppliers", "shipments", "risks"])

        # ------------------------------------------------------------------
        # 2. Execute Selected Tools
        # ------------------------------------------------------------------
        tools_used_names: List[str] = []

        if "inventory" in tools_to_run:
            inv_res = self.tool_get_inventory(db)
            executed_tool_data["inventory"] = inv_res["data"]
            tools_used_names.append("Get inventory")

        if "suppliers" in tools_to_run:
            supp_res = self.tool_get_suppliers(db)
            executed_tool_data["suppliers"] = supp_res["data"]
            tools_used_names.append("Get supply-chain suppliers")

        if "shipments" in tools_to_run:
            shp_res = self.tool_get_shipments(db)
            executed_tool_data["shipments"] = shp_res["data"]
            tools_used_names.append("Get shipments")

        if "risks" in tools_to_run:
            risk_res = self.tool_get_risks(db)
            executed_tool_data["risks"] = risk_res["data"]
            tools_used_names.append("Get supply-chain risks")

        if "weather" in tools_to_run:
            # Extract location from message; fall back to Taiwan
            loc_query = _extract_location(msg_lower) or "Taiwan"
            weath_res = self.tool_get_weather(loc_query)
            executed_tool_data["weather"] = weath_res["data"]
            tools_used_names.append("Get live weather for a location")

        if "news" in tools_to_run:
            news_topic = _extract_news_topic(msg_lower)
            news_res = self.tool_search_news(db, news_topic)
            executed_tool_data["news"] = news_res["data"]
            tools_used_names.append("Search live global supply chain news")

        # ------------------------------------------------------------------
        # 3. Build prompt for IBM Granite
        # ------------------------------------------------------------------
        tool_context_str = json.dumps(executed_tool_data, indent=2)

        # Guard against excessively long context (rough token estimate: 1 token ≈ 4 chars)
        if len(tool_context_str) > 6000:
            tool_context_str = tool_context_str[:6000] + "\n... [truncated for brevity]"

        prompt = (
            f"User Question: \"{user_message}\"\n\n"
            f"Live AegisFlow Telemetry (tool results):\n{tool_context_str}\n\n"
            f"Instructions:\n"
            f"- Answer the user question directly and concisely using the live data above.\n"
            f"- Use clear markdown: ## headings, **bold** key values, bullet points (•), numbered lists.\n"
            f"- Include: risk level, stock runway, supplier details, shipment status, delay days, "
            f"recommended actions — wherever relevant to the question.\n"
            f"- End with a short '**Recommended Action:**' block when actionable steps exist.\n"
            f"- Do NOT reproduce raw JSON. Do NOT invent data not present in the tool results."
        )

        system_prompt = (
            "You are IBM Granite, the chief supply-chain decision intelligence assistant inside AegisFlow. "
            "Provide concise, executive, professional answers using only the live tool telemetry provided. "
            "Format responses with markdown: ## section headers, **bold** for key figures, "
            "and bullet points for lists. Never output raw JSON."
        )

        try:
            granite_res = watsonx_client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=700
            )
            response_text = granite_res.get("text", "").strip()
            if not response_text:
                response_text = (
                    "IBM Granite returned an empty response. "
                    "The model may be initializing — please try again in a moment."
                )
        except Exception as e:
            logger.error(f"Error calling IBM Granite in chatbot: {e}")
            raise

        return {
            "response": response_text,
            "tools_used": tools_used_names,
            "tool_data": executed_tool_data,
            "model": watsonx_client.model_id
        }


chatbot_service = ChatbotService()
