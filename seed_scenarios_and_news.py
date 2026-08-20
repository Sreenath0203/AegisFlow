"""
Seed realistic scenario and news data into AegisFlow SQLite database.
Run: python seed_scenarios_and_news.py
"""
import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = "aegisflow.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# ─────────────────────────────────────────────────────────────────────────────
# 1. SCENARIOS  (10 disruption types × 5 options = 50 rows)
#    Column: name = "DISRUPTION_TYPE:Option Name"
#    This way the backend can filter by name LIKE 'SUPPLIER_FAILURE%' etc.
# ─────────────────────────────────────────────────────────────────────────────

c.execute("DELETE FROM scenarios")

SCENARIOS = [
    # ── SUPPLIER_FAILURE ──────────────────────────────────────────────────────
    ("SUPPLIER_FAILURE:Do Nothing",
     "DO_NOTHING", 0.0, 7, 94,
     "-$220,000 Assembly Line Stop",
     False,
     "No action taken. Primary supplier (ABC Electronics, Taiwan) is offline. "
     "Assembly line halts within 7 days as buffer stock depletes. Full production loss."),

    ("SUPPLIER_FAILURE:Switch to Alternate Supplier",
     "SWITCH_SUPPLIER", 14200.0, 0, 22,
     "+$205,800 Net Saved",
     True,
     "Activate pre-qualified backup supplier in Vietnam with contracted spare capacity. "
     "Fully mitigates stoppage. Incremental cost ~14% above standard unit price."),

    ("SUPPLIER_FAILURE:Expedite Air Freight from Spot Market",
     "EXPEDITE_AIRFREIGHT", 52000.0, 1, 41,
     "+$168,000 Net Saved",
     False,
     "Air charter from spot market semiconductor vendor. High per-unit cost, "
     "but restores production within 24 hours. Suitable for short disruption windows."),

    ("SUPPLIER_FAILURE:Increase Buffer Inventory (Spot Buy)",
     "BUFFER_STOCK", 22000.0, 2, 56,
     "+$98,000 Net Saved",
     False,
     "Procure 60-day buffer stock from spot market at 35% cost premium. "
     "Provides medium-term resilience but ties up working capital."),

    ("SUPPLIER_FAILURE:Split Order Across Regional Vendors",
     "SPLIT_ORDER", 18500.0, 1, 30,
     "+$145,500 Net Saved",
     False,
     "Divide 60% / 40% order split between Vietnam and South Korea vendors. "
     "Distributes single-source dependency risk at moderate cost increment."),

    # ── PORT_STRIKE ───────────────────────────────────────────────────────────
    ("PORT_STRIKE:Do Nothing",
     "DO_NOTHING", 0.0, 14, 88,
     "-$310,000 Delayed Production",
     False,
     "Port of Kaohsiung partially closed due to labor dispute. "
     "All sea freight halted. Estimated 14-day disruption window with full delay cascade."),

    ("PORT_STRIKE:Reroute via Singapore Transshipment",
     "REROUTE_PORT", 31000.0, 3, 28,
     "+$279,000 Net Saved",
     True,
     "Redirect shipments through Port of Singapore for transshipment to Los Angeles. "
     "Adds 3 days lead time but fully bypasses the strike-affected port."),

    ("PORT_STRIKE:Charter Private Air Cargo",
     "CHARTER_AIR", 78000.0, 1, 18,
     "+$232,000 Net Saved",
     False,
     "Full air charter bypasses maritime disruption entirely. "
     "Maximum cost but minimum delay. Viable only for critical high-value components."),

    ("PORT_STRIKE:Pre-position Inventory at Inland Warehouse",
     "PREPOSITION_INV", 19500.0, 5, 45,
     "+$190,000 Net Saved",
     False,
     "Use pre-positioned safety stock at San Jose inland warehouse. "
     "Buys 5 days of production continuity while alternative routing is established."),

    ("PORT_STRIKE:Negotiate with Alternate Carrier",
     "ALT_CARRIER", 11000.0, 6, 51,
     "+$171,000 Net Saved",
     False,
     "Engage backup ocean carrier with capacity via different port of origin. "
     "Adds 6 days but reduces cost impact significantly compared to air freight."),

    # ── TYPHOON_DISRUPTION ────────────────────────────────────────────────────
    ("TYPHOON_DISRUPTION:Do Nothing",
     "DO_NOTHING", 0.0, 10, 91,
     "-$275,000 Supply Chain Halt",
     False,
     "Typhoon warning across East China Sea sea lanes. No rerouting activated. "
     "Vessels remain at anchor pending storm passage. 10-day delay expected."),

    ("TYPHOON_DISRUPTION:Preemptive Route Diversion (South)",
     "ROUTE_DIVERSION", 24000.0, 2, 19,
     "+$251,000 Net Saved",
     True,
     "Divert active vessel through southern sea lane via Luzon Strait. "
     "Adds 2 days transit time but avoids typhoon direct path and port closure risk."),

    ("TYPHOON_DISRUPTION:Expedite Pre-Storm Departure",
     "PRE_STORM_DEPART", 9500.0, 0, 33,
     "+$265,500 Net Saved",
     False,
     "Accelerate loading and depart port 36 hours ahead of typhoon arrival window. "
     "Minimal cost increase, highly effective if typhoon tracking forecast is accurate."),

    ("TYPHOON_DISRUPTION:Invoke Insurance & Delay Buffer",
     "INSURANCE_DELAY", 5000.0, 10, 61,
     "+$122,000 Net Saved (Insurance)",
     False,
     "Claim force majeure under cargo insurance. Accept delay. "
     "Financial impact partially recovered through policy but production loss is real."),

    ("TYPHOON_DISRUPTION:Activate Emergency Air Freight",
     "EMERGENCY_AIR", 64000.0, 1, 22,
     "+$211,000 Net Saved",
     False,
     "Activate standing air freight SLA with logistics partner for highest priority SKUs. "
     "Avoids line shutdown but significant cost premium. Partial shipment recommended."),

    # ── GEOPOLITICAL_TENSION ─────────────────────────────────────────────────
    ("GEOPOLITICAL_TENSION:Do Nothing",
     "DO_NOTHING", 0.0, 21, 89,
     "-$480,000 Regulatory Block",
     False,
     "Escalating trade restrictions between US and Taiwan under review. "
     "No contingency activated. Risk of sudden export control enforcement."),

    ("GEOPOLITICAL_TENSION:Dual-Source from Non-Restricted Regions",
     "DUAL_SOURCE", 35000.0, 4, 24,
     "+$445,000 Net Saved",
     True,
     "Establish dual-sourcing from Malaysia and South Korea as non-restricted alternatives. "
     "Increases supply resilience significantly at moderate cost increase of 18%."),

    ("GEOPOLITICAL_TENSION:Stockpile Critical Components (90-Day)",
     "STRATEGIC_STOCKPILE", 88000.0, 0, 29,
     "+$392,000 Net Saved",
     False,
     "Build 90-day strategic inventory buffer of top-5 critical SKUs. "
     "High working capital cost but provides longest disruption immunity window."),

    ("GEOPOLITICAL_TENSION:Qualify Near-Shore Supplier (Mexico)",
     "NEARSHORE_QUALIFY", 42000.0, 60, 37,
     "+$261,000 Net Saved (Long-Term)",
     False,
     "Invest in qualifying a near-shore supplier in Monterrey, Mexico. "
     "Long qualification lead time but permanently eliminates geopolitical exposure for key SKUs."),

    ("GEOPOLITICAL_TENSION:Accelerate Orders Before Restriction Date",
     "FRONTLOAD_ORDERS", 21000.0, 0, 44,
     "+$317,000 Net Saved",
     False,
     "Accelerate purchase orders ahead of potential trade restriction enforcement date. "
     "Uses existing supplier relationships. Creates temporary inventory surplus."),

    # ── DEMAND_SPIKE ──────────────────────────────────────────────────────────
    ("DEMAND_SPIKE:Do Nothing",
     "DO_NOTHING", 0.0, 12, 76,
     "-$195,000 Lost Revenue",
     False,
     "Unexpected 45% demand surge from key account. "
     "Current inventory insufficient. Stockout imminent in 12 days. Customer at risk."),

    ("DEMAND_SPIKE:Expedite Existing Purchase Orders",
     "EXPEDITE_PO", 18000.0, 2, 31,
     "+$177,000 Net Saved",
     True,
     "Pay expedite fee to advance scheduled PO shipments by 14 days. "
     "Covers demand gap with minimal supply chain disruption. Preferred option."),

    ("DEMAND_SPIKE:Spot Market Emergency Buy",
     "SPOT_BUY", 44000.0, 1, 25,
     "+$151,000 Net Saved",
     False,
     "Procure deficit volume from spot market at 40% cost premium. "
     "Immediate availability but significant margin erosion on incremental units."),

    ("DEMAND_SPIKE:Allocate Existing Stock by Customer Priority",
     "PRIORITY_ALLOC", 0.0, 0, 52,
     "+$90,000 Net Protected (Priority A)",
     False,
     "Tier customer allocations — serve Tier-1 customers at full volume, "
     "defer Tier-2 orders by 3 weeks. Protects key revenue but risks secondary customer relationships."),

    ("DEMAND_SPIKE:Increase Production Shift (Overtime)",
     "OVERTIME_PROD", 28000.0, 4, 38,
     "+$167,000 Net Saved",
     False,
     "Add overtime production shifts to increase output by 30%. "
     "Effective for assembly-intensive products. Higher labor cost, moderate lead time savings."),

    # ── LOGISTICS_DELAY ───────────────────────────────────────────────────────
    ("LOGISTICS_DELAY:Do Nothing",
     "DO_NOTHING", 0.0, 8, 72,
     "-$140,000 Delayed Delivery",
     False,
     "Multiple container vessels delayed at Busan port due to congestion. "
     "Average delay 8 days. No corrective action planned."),

    ("LOGISTICS_DELAY:Upgrade to Priority Express Lane",
     "PRIORITY_LANE", 12000.0, 2, 21,
     "+$128,000 Net Saved",
     True,
     "Upgrade container to priority express slot on next available departure. "
     "Reduces delay by 6 days. Standard solution for minor port congestion events."),

    ("LOGISTICS_DELAY:Split Cargo Across Multiple Carriers",
     "MULTI_CARRIER", 8500.0, 3, 34,
     "+$112,000 Net Saved",
     False,
     "Split cargo across 3 carriers on different departure windows. "
     "Reduces risk of complete delay. Moderate cost for documentation complexity."),

    ("LOGISTICS_DELAY:Inland Rail Alternative (Korea → Japan → Sea)",
     "ALT_RAIL", 16000.0, 5, 42,
     "+$96,000 Net Saved",
     False,
     "Route cargo via rail to Japan port then onward sea freight. "
     "Bypasses Busan congestion. Adds 5 days total but guarantees departure."),

    ("LOGISTICS_DELAY:Airbridge for Critical SKUs Only",
     "AIR_CRITICAL", 38000.0, 1, 27,
     "+$102,000 Net Saved",
     False,
     "Air freight only the 3 highest-criticality SKUs (Microcontroller X1, Power Module P8, Display D2). "
     "Remainder travels by sea. Balanced cost-risk profile."),

    # ── QUALITY_FAILURE ───────────────────────────────────────────────────────
    ("QUALITY_FAILURE:Do Nothing",
     "DO_NOTHING", 0.0, 0, 85,
     "-$320,000 Recall & Rework",
     False,
     "Quality audit failed for incoming batch from Apex Semiconductor AG. "
     "Non-conformance in 12% of units. Line use would trigger downstream warranty claims."),

    ("QUALITY_FAILURE:Return & Expedite Replacement Batch",
     "RETURN_REPLACE", 31000.0, 6, 38,
     "+$289,000 Net Saved",
     True,
     "Return defective batch and invoke SLA penalty clause. "
     "Request expedite replacement from backup-qualified supplier. Adds 6-day gap."),

    ("QUALITY_FAILURE:Sort & Rework In-House",
     "REWORK_INHOUSE", 18000.0, 3, 52,
     "+$202,000 Net Saved",
     False,
     "100% sort inspection and rework of incoming batch. "
     "Recovers ~85% of units at 3-day delay. Cost-effective if defect rate is below 20%."),

    ("QUALITY_FAILURE:Emergency Qualification of Alternate Supplier",
     "EMERG_QUAL", 54000.0, 14, 44,
     "+$158,000 Net Saved (Long-Term)",
     False,
     "Fast-track qualification of backup supplier. "
     "High upfront cost and long lead time but permanently reduces dependency on failed vendor."),

    ("QUALITY_FAILURE:Apply Derogation & Accept Under Restriction",
     "DEROGATION", 6000.0, 0, 67,
     "+$174,000 Net Saved (Short-Term)",
     False,
     "Apply engineering derogation to use non-conforming parts under controlled conditions. "
     "Risk mitigation: additional end-of-line testing. Valid only for safety-non-critical components."),

    # ── PRICE_SHOCK ───────────────────────────────────────────────────────────
    ("PRICE_SHOCK:Do Nothing",
     "DO_NOTHING", 0.0, 0, 61,
     "-$180,000 Margin Erosion",
     False,
     "Spot market prices for Memory Module M8 have risen 55% due to global DRAM shortage. "
     "Continuing purchases at market rates will erode product margins below threshold."),

    ("PRICE_SHOCK:Lock In Forward Contract",
     "FORWARD_CONTRACT", 22000.0, 0, 18,
     "+$158,000 Net Saved",
     True,
     "Negotiate 6-month forward purchase contract at current spot plus 8% premium. "
     "Locks in price certainty. Protects margins for full H2 production plan."),

    ("PRICE_SHOCK:Substitute with Equivalent Component",
     "COMPONENT_SUBST", 35000.0, 30, 32,
     "+$99,000 Net Saved",
     False,
     "Qualify alternative DRAM supplier offering equivalent spec at 20% below current spot. "
     "30-day engineering validation required. Strong long-term margin improvement."),

    ("PRICE_SHOCK:Reduce Order Quantity (Demand Management)",
     "REDUCE_ORDER", -15000.0, 0, 44,
     "+$75,000 Saved (Reduced Exposure)",
     False,
     "Reduce order volume by 30% and manage customer lead times accordingly. "
     "Reduces cost exposure but risks service level commitments."),

    ("PRICE_SHOCK:Source from Spot Market in Batches",
     "BATCH_SPOT", 8000.0, 0, 56,
     "+$44,000 Net Saved",
     False,
     "Purchase in smaller, more frequent spot batches to average down cost over time. "
     "Reduces overcommitment risk but provides no price certainty."),

    # ── NATURAL_DISASTER ─────────────────────────────────────────────────────
    ("NATURAL_DISASTER:Do Nothing",
     "DO_NOTHING", 0.0, 30, 97,
     "-$650,000 Extended Outage",
     False,
     "7.4 magnitude earthquake damaged Nordic Sensors AB facility in Sweden. "
     "Full capacity restoration expected in 30+ days. No contingency engaged."),

    ("NATURAL_DISASTER:Activate Tier-2 Qualified Supplier",
     "TIER2_SUPPLIER", 28000.0, 5, 19,
     "+$622,000 Net Saved",
     True,
     "Activate pre-approved Tier-2 supplier with 80% capacity match. "
     "5-day transition to first delivery. Pre-negotiated pricing ensures cost predictability."),

    ("NATURAL_DISASTER:Emergency Global Tender",
     "EMERGENCY_TENDER", 55000.0, 12, 35,
     "+$485,000 Net Saved",
     False,
     "Issue emergency global tender for sensor components. "
     "Higher procurement cost but broader supply pool. Suitable if Tier-2 cannot fully cover volume."),

    ("NATURAL_DISASTER:Redesign Around Available Component",
     "REDESIGN", 120000.0, 45, 28,
     "+$290,000 Net Saved (Long-Term)",
     False,
     "Engineering redesign to substitute affected sensor with an equivalent available globally. "
     "High NRE cost and long lead time but eliminates future single-source exposure."),

    ("NATURAL_DISASTER:Draw Down Strategic Reserve",
     "STRATEGIC_RESERVE", 0.0, 0, 48,
     "+$330,000 Net Saved (Short-Term)",
     False,
     "Draw down strategic component reserve held at Singapore warehouse. "
     "Provides 15 days of production continuity at zero incremental cost. Requires replenishment after."),

    # ── CYBER_INCIDENT ────────────────────────────────────────────────────────
    ("CYBER_INCIDENT:Do Nothing",
     "DO_NOTHING", 0.0, 5, 90,
     "-$520,000 Systems Outage",
     False,
     "Ransomware attack on supplier ERP system has disrupted order visibility and shipment tracking. "
     "No manual workaround activated. Full data loss risk in 5 days."),

    ("CYBER_INCIDENT:Activate Manual Order Tracking Protocol",
     "MANUAL_PROTOCOL", 8000.0, 1, 29,
     "+$512,000 Net Saved",
     True,
     "Switch to manual purchase order and shipment confirmation workflows. "
     "Activates paper-based and phone confirmation protocol. Minimal cost, immediate execution."),

    ("CYBER_INCIDENT:Engage Cyber Recovery Specialist",
     "CYBER_RECOVERY", 65000.0, 3, 22,
     "+$455,000 Net Saved",
     False,
     "Contract cybersecurity recovery team to restore supplier ERP systems. "
     "High cost but restores digital order visibility within 3 days."),

    ("CYBER_INCIDENT:Reroute Orders to Non-Affected Supplier System",
     "REROUTE_ORDERS", 15000.0, 2, 33,
     "+$440,000 Net Saved",
     False,
     "Temporarily redirect open purchase orders to backup supplier not affected by incident. "
     "2-day transition. Effective if backup has available capacity."),

    ("CYBER_INCIDENT:Invoke Force Majeure & Negotiate Extension",
     "FORCE_MAJEURE", 3000.0, 7, 55,
     "+$310,000 Net Saved (Delayed)",
     False,
     "Invoke force majeure clauses with customers and suppliers. "
     "Negotiate 7-day delivery extensions across affected contracts. Preserves relationships but delays revenue."),
]

assert len(SCENARIOS) == 50, f"Expected 50 scenarios, got {len(SCENARIOS)}"

c.executemany(
    """INSERT INTO scenarios
       (name, option_key, cost_delta, delay_days, risk_score, net_impact, is_recommended, details)
       VALUES (?,?,?,?,?,?,?,?)""",
    SCENARIOS
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. NEWS EVENTS  (18 realistic articles)
# ─────────────────────────────────────────────────────────────────────────────

c.execute("DELETE FROM events")

base_dt = datetime(2025, 6, 1, 9, 0, 0)

NEWS = [
    (
        "Super Typhoon Mawar Approaches East Asia Maritime Hub",
        "Reuters", "Taiwan Strait / South China Sea", "CRITICAL",
        "Category 4 typhoon on direct path to Taiwan Strait. "
        "Kaohsiung and Keelung ports issuing 72-hour closure notices. "
        "Vessel diversions increasing transit times by 5–8 days.",
        "Direct disruption to semiconductor exports from Taiwan. "
        "ABC Electronics Co. and all Taiwan-origin shipments at high delay risk.",
        "ABC Electronics Co., Global Tech Modules",
        base_dt - timedelta(hours=2)
    ),
    (
        "Taiwan Semiconductor Export Controls Tightened Under New Trade Policy",
        "Wall Street Journal", "Taipei, Taiwan", "HIGH",
        "US Department of Commerce expands Entity List controls on advanced semiconductor exports. "
        "Affects chips below 7nm process node. Compliance review required for all active orders.",
        "Microcontroller X1 and Display Controller D2 procurement from ABC Electronics may require "
        "end-use certification. Expected 2–3 week compliance review delay on affected SKUs.",
        "ABC Electronics Co.",
        base_dt - timedelta(days=1)
    ),
    (
        "Port of Busan Dock Worker Strike Enters Third Week",
        "Lloyd's List", "Busan, South Korea", "HIGH",
        "Korean Confederation of Trade Unions maintains picket lines at Busan container terminal. "
        "Container throughput down 65%. Vessels anchoring offshore awaiting berth allocation.",
        "Apex Semiconductor AG shipments via Busan port facing 10–14 day delays. "
        "Power Regulator P1 and Memory Module M8 inbound shipments affected.",
        "Apex Semiconductor AG",
        base_dt - timedelta(days=2)
    ),
    (
        "Flash Flooding Disrupts Ho Chi Minh City Logistics Corridor",
        "Vietnam News Agency", "Ho Chi Minh City, Vietnam", "HIGH",
        "Unprecedented 72-hour rainfall event caused flooding across Cat Lai port access roads. "
        "Trucks unable to access container terminal. Rail alternative under assessment.",
        "Supplier XYZ Logistics Vietnam operations affected. "
        "Estimated 5–7 day delay on all outbound containers from Southern Vietnam warehouse.",
        "Supplier XYZ Logistics",
        base_dt - timedelta(days=3)
    ),
    (
        "Malaysia Electricity Rationing Impacts Penang Industrial Zone",
        "The Edge Malaysia", "Penang, Malaysia", "MEDIUM",
        "Tenaga Nasional Berhad implements 4-hour daily rolling blackouts across Penang Free Industrial Zone "
        "due to grid capacity constraints. Semiconductor fabs operating at reduced throughput.",
        "Global Tech Modules Penang facility reporting 15% capacity reduction. "
        "Delivery schedules for Memory Module M8 and LCD components pushed back 3–5 days.",
        "Global Tech Modules",
        base_dt - timedelta(days=3, hours=4)
    ),
    (
        "TSMC Advanced Packaging Facility Fire Causes Production Halt",
        "Nikkei Asia", "Hsinchu, Taiwan", "CRITICAL",
        "Electrical fire in TSMC CoWoS packaging facility caused 18-hour production halt. "
        "No casualties reported. Clean-room contamination assessment underway. "
        "Customer allocation reductions likely across Q3 wafer orders.",
        "TSMC is upstream supplier to ABC Electronics Co. "
        "Microcontroller X1 and Display Controller D2 lead times expected to extend by 2–3 weeks.",
        "ABC Electronics Co.",
        base_dt - timedelta(days=4)
    ),
    (
        "Red Sea Shipping Disruptions Persist as Houthi Threat Continues",
        "Maritime Executive", "Red Sea / Gulf of Aden", "HIGH",
        "Ongoing Houthi-attributed drone and missile attacks force continued Suez Canal avoidance. "
        "Vessels rerouting via Cape of Good Hope adding 12–16 days to Europe-Asia routes.",
        "European bound shipments from Nordic Sensors AB and reverse logistics flows impacted. "
        "Transit times from Sweden to Singapore hub extended by 14 days.",
        "Nordic Sensors AB",
        base_dt - timedelta(days=5)
    ),
    (
        "DRAM Memory Spot Prices Surge 40% on AI Demand Acceleration",
        "DRAMeXchange", "Global / Taiwan DRAM Market", "HIGH",
        "SK Hynix and Samsung report allocation tightening as hyperscaler AI server demand "
        "accelerates through H2 2025. DRAM spot prices up 40% MoM. Contract negotiations under pressure.",
        "Memory Module M8 procurement costs facing 35-40% increase. "
        "Current contracted pricing effective through Q3. Renewal negotiations at risk.",
        "Apex Semiconductor AG, Global Tech Modules",
        base_dt - timedelta(days=5, hours=6)
    ),
    (
        "Vietnam US Trade Deal Uncertainty Creates Tariff Risk",
        "Financial Times", "Hanoi, Vietnam", "MEDIUM",
        "US-Vietnam trade negotiations stalled over IP enforcement requirements. "
        "Section 301 tariff investigation initiated. Decision expected within 60 days.",
        "Supplier XYZ Logistics in Vietnam potentially subject to additional 15–25% tariff on "
        "electronics components. Cost delta modeling underway. Alternate sourcing evaluation advised.",
        "Supplier XYZ Logistics",
        base_dt - timedelta(days=6)
    ),
    (
        "Stockholm-Arlanda Airport Cargo Handlers Labor Dispute",
        "SvD Näringsliv", "Stockholm, Sweden", "MEDIUM",
        "IF Metall union cargo handlers at Stockholm-Arlanda Airport begin work-to-rule action. "
        "Air freight clearance times extended from 4 hours to 24+ hours. Backlog accumulating.",
        "Nordic Sensors AB air freight shipments affected. Temperature-sensitive sensor components "
        "require express handling. Alternative routing via Copenhagen assessed.",
        "Nordic Sensors AB",
        base_dt - timedelta(days=7)
    ),
    (
        "South Korea Announces Semiconductor R&D Export Licensing Requirements",
        "Korea Herald", "Seoul, South Korea", "MEDIUM",
        "Ministry of Trade, Industry and Energy issues new Technology Export Control guidance "
        "on advanced packaging techniques. Dual-use classification review for 14nm and below.",
        "Apex Semiconductor AG Power Regulator P1 components subject to new licensing review. "
        "Estimated 3-week delay per shipment for affected product lines until guidance is clarified.",
        "Apex Semiconductor AG",
        base_dt - timedelta(days=8)
    ),
    (
        "Pacific Container Shortage Drives 60-Day Lead Time Extensions",
        "Freightos Baltic Index", "Trans-Pacific Shipping Lanes", "MEDIUM",
        "Empty container imbalance persists across trans-Pacific trade lanes. "
        "Equipment availability in Kaohsiung, Ho Chi Minh City, and Penang severely constrained. "
        "Lead times for ocean freight have extended from 28 to 60+ days on average.",
        "All five primary suppliers affected by container availability constraints. "
        "Recommend switching critical SKU orders to air freight or pre-booking containers 90 days in advance.",
        "ABC Electronics Co., Supplier XYZ Logistics, Apex Semiconductor AG, Global Tech Modules",
        base_dt - timedelta(days=9)
    ),
    (
        "EUDR Regulation Deadline Forces Compliance Audit Across Supply Chain",
        "Reuters ESG", "Brussels, Belgium / Global", "LOW",
        "EU Deforestation Regulation enters enforcement phase. "
        "All products containing regulated materials require supply chain due diligence documentation. "
        "Non-compliant shipments face EU customs hold and penalty.",
        "Packaging materials for AegisFlow product lines may include regulated substrates. "
        "Compliance audit of Tier-1 and Tier-2 suppliers recommended within 30 days.",
        "Global Tech Modules, Nordic Sensors AB",
        base_dt - timedelta(days=10)
    ),
    (
        "Logistics Provider DHL Reports Cyberattack on Tracking Platform",
        "Cybersecurity Dive", "Global / Frankfurt, Germany", "HIGH",
        "DHL's global shipment tracking and customs clearance platform suffered targeted ransomware attack. "
        "System partially restored but real-time tracking unavailable for 48+ hours. "
        "Manual confirmation workflows activated across 120 countries.",
        "5 active AegisFlow shipments routed through DHL at risk of visibility blackout. "
        "Supplier XYZ Logistics and Apex Semiconductor AG primary shipping partners via DHL affected.",
        "Supplier XYZ Logistics, Apex Semiconductor AG",
        base_dt - timedelta(days=11)
    ),
    (
        "Japan Earthquake M6.8 Disrupts Osaka Semiconductor Subcomponent Cluster",
        "NHK World", "Osaka, Japan", "CRITICAL",
        "Magnitude 6.8 earthquake struck Osaka Bay area. Multiple industrial facilities reporting structural "
        "assessment shutdowns. Yodogawa industrial park — key wafer substrate production cluster — offline.",
        "ABC Electronics Co. and Apex Semiconductor AG both source substrate components from Osaka cluster. "
        "Upstream supply disruption likely to cascade into 3–4 week production delays.",
        "ABC Electronics Co., Apex Semiconductor AG",
        base_dt - timedelta(days=12)
    ),
    (
        "US Customs CBP Increases Forced Labor Compliance Inspections",
        "JOC.com", "Los Angeles, USA", "MEDIUM",
        "US Customs and Border Protection activated enhanced Uyghur Forced Labor Prevention Act "
        "inspections at Los Angeles and Long Beach ports. Detention notices issued to 47 importers. "
        "Average clearance delay: 18 business days.",
        "AegisFlow inbound shipments at LA/LB ports may face customs holds. "
        "Supply chain transparency documentation for all Taiwan and China-origin components required.",
        "ABC Electronics Co., Global Tech Modules",
        base_dt - timedelta(days=13)
    ),
    (
        "Fuel Price Spike Drives Emergency Freight Surcharges on Asia-Pacific Routes",
        "Platts Shipping", "Singapore / Hong Kong", "LOW",
        "Brent crude oil price increase of 28% over 30 days triggers emergency fuel surcharges "
        "from Maersk, Evergreen, and Cosco. BAF surcharge of $420/TEU effective immediately on all routes.",
        "Freight cost increase across all 5 primary supplier shipments. "
        "Estimated $85,000 additional annual logistics cost at current shipment volume.",
        "ABC Electronics Co., Supplier XYZ Logistics, Apex Semiconductor AG, Global Tech Modules, Nordic Sensors AB",
        base_dt - timedelta(days=14)
    ),
    (
        "Nordic Sensors AB Plant Maintenance Shutdown Delays Q3 Sensor Deliveries",
        "Elektroniktidningen", "Gothenburg, Sweden", "LOW",
        "Nordic Sensors AB annual planned maintenance window extended by 9 days due to "
        "unexpected robotic assembly line calibration issue. Q3 production schedule impacted.",
        "Temperature and pressure sensor deliveries from Nordic Sensors AB delayed by 9 days. "
        "Affect on AegisFlow smart monitoring module production: moderate. Buffer stock covers 6 days.",
        "Nordic Sensors AB",
        base_dt - timedelta(days=16)
    ),
]

assert len(NEWS) == 18, f"Expected 18 news, got {len(NEWS)}"

c.executemany(
    """INSERT INTO events
       (headline, source, location, severity, impact, supply_chain_impact, affected_suppliers, created_at)
       VALUES (?,?,?,?,?,?,?,?)""",
    NEWS
)

conn.commit()
conn.close()

print(f"✅ Seeded {len(SCENARIOS)} scenario rows across 10 disruption types.")
print(f"✅ Seeded {len(NEWS)} supply chain news events.")
print("Done.")
