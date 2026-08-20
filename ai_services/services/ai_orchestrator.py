import logging
from sqlalchemy.orm import Session
from backend.models.models import (
    Supplier,
    Shipment,
    InventoryItem,
    RiskItem,
    Recommendation,
    ComplianceRecord,
    NewsEvent,
    ScenarioResult
)
from ai_services.agents.news_agent import news_agent
from ai_services.agents.supplier_risk_agent import supplier_risk_agent
from ai_services.agents.compliance_agent import compliance_agent
from ai_services.agents.decision_agent import decision_agent
from typing import Dict, Any

logger = logging.getLogger("aegisflow.orchestrator")


class AIOrchestrator:
    """
    Multi-Agent Orchestrator Pipeline for AegisFlow.

    Orchestrates:
        Data Preparation
        -> News Agent
        -> Supplier Risk Agent
        -> Compliance Agent
        -> IBM watsonx / Granite
        -> Decision Agent
        -> Database Updates
    """

    def _calculate_stockout_risk(self, days_remaining: int):
        """
        Calculate a consistent human-readable risk and risk level
        from the number of days of inventory remaining.
        """

        if days_remaining <= 3:
            return "Critical", "CRITICAL"

        elif days_remaining <= 7:
            return "High", "HIGH"

        elif days_remaining <= 14:
            return "Medium", "MEDIUM"

        else:
            return "Low", "LOW"

    def run_typhoon_demo_scenario(
        self,
        db: Session
    ) -> Dict[str, Any]:

        logger.info(
            "Executing End-to-End Typhoon Weather Disruption "
            "Scenario Orchestration..."
        )

        # ---------------------------------------------------------
        # 1. GET / CREATE NEWS EVENT
        # ---------------------------------------------------------

        news_record = (
            db.query(NewsEvent)
            .filter(NewsEvent.headline.like("%Typhoon%"))
            .first()
        )

        if not news_record:

            news_record = NewsEvent(
                headline=(
                    "Super Typhoon Mawar Approaches "
                    "East Asia Maritime Hub"
                ),
                source="Global Maritime Weather Advisory",
                location="Kaohsiung Port, Taiwan",
                severity="CRITICAL",
                supply_chain_impact=(
                    "Port operations suspended for 4-5 days. "
                    "Container vessels held at anchor."
                ),
                affected_suppliers="ABC Electronics Co."
            )

            db.add(news_record)
            db.commit()
            db.refresh(news_record)

        news_input = {
    "locations": [
        "Kaohsiung",
        "Taiwan",
        "East Asia"
    ],
    "suppliers": [
        "ABC Electronics Co."
    ],
    "products": [
        "Microcontroller X1",
        "semiconductors"
    ],
    "industries": [
        "semiconductor manufacturing",
        "electronics",
        "shipping"
    ]
}

        news_report = news_agent.analyze(news_input)

        # ---------------------------------------------------------
        # 2. UPDATE ABC ELECTRONICS SUPPLIER
        # ---------------------------------------------------------

        abc_supplier = (
            db.query(Supplier)
            .filter(
                Supplier.name.like("%ABC Electronics%")
            )
            .first()
        )

        if abc_supplier:

            abc_supplier.reliability_score = 52.0
            abc_supplier.current_risk_level = "HIGH"

        # ---------------------------------------------------------
        # 3. UPDATE SHIPMENT SHP-9021
        # ---------------------------------------------------------

        shp_9021 = (
            db.query(Shipment)
            .filter(
                Shipment.shipment_code == "SHP-9021"
            )
            .first()
        )

        if shp_9021:

            shp_9021.status = "AT_RISK"
            shp_9021.delay_days = 5
            shp_9021.risk_level = "HIGH"

        # ---------------------------------------------------------
        # 4. UPDATE MICROCONTROLLER INVENTORY RISK
        # ---------------------------------------------------------

        mcu_inv = (
            db.query(InventoryItem)
            .filter(
                InventoryItem.sku == "MCU-X1-88"
            )
            .first()
        )

        if mcu_inv:

            # Calculate the risk from actual inventory runway.
            days_remaining = int(
                mcu_inv.days_remaining or 0
            )

            risk_label, risk_level = (
                self._calculate_stockout_risk(
                    days_remaining
                )
            )

            # IMPORTANT:
            # Keep both fields consistent.
            mcu_inv.stockout_risk = risk_label
            mcu_inv.stockout_risk_level = risk_level

        # Save all changes.
        db.commit()

        # ---------------------------------------------------------
        # 5. SUPPLIER RISK ANALYSIS
        # ---------------------------------------------------------

        supplier_context = {
            "name": (
                abc_supplier.name
                if abc_supplier
                else "ABC Electronics Co."
            ),
            "reliability_score": (
                abc_supplier.reliability_score
                if abc_supplier
                else 52.0
            ),
            "on_time_delivery": (
                abc_supplier.on_time_delivery
                if abc_supplier
                else 92.0
            ),
            "quality_score": (
                abc_supplier.quality_score
                if abc_supplier
                else 98.0
            )
        }

        supplier_report = supplier_risk_agent.analyze({
            "supplier": supplier_context,
            "news_report": news_report
        })

        # ---------------------------------------------------------
        # 6. COMPLIANCE ANALYSIS
        # ---------------------------------------------------------

        compliance_report = compliance_agent.analyze({
            "supplier_report": supplier_report
        })

        # ---------------------------------------------------------
        # 7. INVENTORY CONTEXT
        # ---------------------------------------------------------

        inventory_context = {
            "product_name": (
                mcu_inv.product_name
                if mcu_inv
                else "Microcontroller X1"
            ),
            "days_remaining": (
                mcu_inv.days_remaining
                if mcu_inv
                else 3
            ),
            "stockout_risk": (
                mcu_inv.stockout_risk
                if mcu_inv
                else "Critical"
            ),
            "stockout_risk_level": (
                mcu_inv.stockout_risk_level
                if mcu_inv
                else "CRITICAL"
            )
        }

        # ---------------------------------------------------------
        # 8. DECISION AGENT
        # ---------------------------------------------------------

        decision_report = decision_agent.analyze({

            "news_report": news_report,

            "supplier_report": supplier_report,

            "compliance_report": compliance_report,

            "inventory_item": inventory_context

        })

        # ---------------------------------------------------------
        # 9. CREATE / UPDATE TYHOON RISK
        # ---------------------------------------------------------

        existing_risk = (
            db.query(RiskItem)
            .filter(
                RiskItem.title.like(
                    "%Typhoon Mawar%"
                )
            )
            .first()
        )

        if not existing_risk:

            existing_risk = RiskItem(

                title=(
                    "Super Typhoon Mawar Disrupts "
                    "Kaohsiung Port & Microcontroller Supply"
                ),

                risk_score=(
                    decision_report[
                        "overall_risk_score"
                    ]
                ),

                risk_type="WEATHER",

                probability=0.95,

                severity="HIGH",

                financial_impact=180000.0,

                affected_supplier_id=(
                    abc_supplier.id
                    if abc_supplier
                    else None
                ),

                affected_shipment_id=(
                    shp_9021.id
                    if shp_9021
                    else None
                ),

                evidence="\n".join(
                    decision_report["evidence"]
                ),

                ai_explanation=(
                    decision_report[
                        "granite_reasoning"
                    ]
                ),

                status="ACTIVE"
            )

            db.add(existing_risk)
            db.commit()
            db.refresh(existing_risk)

        else:

            existing_risk.risk_score = (
                decision_report[
                    "overall_risk_score"
                ]
            )

            existing_risk.evidence = "\n".join(
                decision_report["evidence"]
            )

            existing_risk.ai_explanation = (
                decision_report[
                    "granite_reasoning"
                ]
            )

            db.commit()

        # ---------------------------------------------------------
        # 10. CREATE / UPDATE RECOMMENDATION
        # ---------------------------------------------------------

        existing_rec = (
            db.query(Recommendation)
            .filter(
                Recommendation.risk_id
                == existing_risk.id
            )
            .first()
        )

        if not existing_rec:

            existing_rec = Recommendation(

                action_title=(
                    decision_report[
                        "recommended_action"
                    ]
                ),

                reason=(
                    decision_report[
                        "reason"
                    ]
                ),

                confidence_score=(
                    decision_report[
                        "confidence_score"
                    ]
                ),

                expected_impact=(
                    decision_report[
                        "expected_business_impact"
                    ]
                ),

                financial_saving=(
                    decision_report[
                        "financial_saving"
                    ]
                ),

                delay_reduction_days=(
                    decision_report[
                        "delay_reduction_days"
                    ]
                ),

                alternative_actions=str([
                    s["scenario_name"]
                    for s in decision_report[
                        "scenarios"
                    ]
                    if not s["is_recommended"]
                ]),

                status="PROPOSED",

                risk_id=existing_risk.id
            )

            db.add(existing_rec)
            db.commit()

        else:

            existing_rec.action_title = (
                decision_report[
                    "recommended_action"
                ]
            )

            existing_rec.reason = (
                decision_report[
                    "reason"
                ]
            )

            existing_rec.confidence_score = (
                decision_report[
                    "confidence_score"
                ]
            )

            db.commit()

        # ---------------------------------------------------------
        # 11. UPDATE SCENARIO RESULTS
        # ---------------------------------------------------------

        db.query(ScenarioResult).delete()
        db.commit()

        for sc in decision_report["scenarios"]:

            db_sc = ScenarioResult(

                scenario_name=sc[
                    "scenario_name"
                ],

                option_key=sc[
                    "option_key"
                ],

                cost_delta=sc[
                    "cost_delta"
                ],

                delay_days=sc[
                    "delay_days"
                ],

                risk_score=sc[
                    "risk_score"
                ],

                net_impact=sc[
                    "net_impact"
                ],

                is_recommended=sc[
                    "is_recommended"
                ],

                details=sc[
                    "details"
                ]
            )

            db.add(db_sc)

        db.commit()

        # ---------------------------------------------------------
        # 12. FINAL RESPONSE
        # ---------------------------------------------------------

        return {

            "scenario": (
                "Super Typhoon Weather Disruption"
            ),

            "news_report": news_report,

            "supplier_report": supplier_report,

            "compliance_report": compliance_report,

            "decision_report": decision_report,

            "db_updates": {

                "supplier": (
                    "ABC Electronics Co. "
                    "(Reliability 52.0%, HIGH Risk)"
                ),

                "shipment": (
                    "SHP-9021 "
                    "(AT_RISK, +5 Days Delay)"
                ),

                "inventory": (
                    "Microcontroller X1 "
                    "(CRITICAL Stockout Risk)"
                )
            }
        }


ai_orchestrator = AIOrchestrator()