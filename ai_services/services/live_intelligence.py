from typing import Dict, Any, List

from backend.models.models import Supplier, Shipment, InventoryItem

from ai_services.agents.location_agent import location_agent
from ai_services.agents.weather_agent import weather_agent
from ai_services.agents.news_agent import news_agent


class LiveIntelligenceService:
    """
    Live external intelligence service for AegisFlow.

    Collects:
        - Supply-chain locations
        - Suppliers
        - Products
        - Real-time weather
        - Real-time global supply-chain news
    """

    def collect_locations(self, db) -> List[str]:

        locations = []

        suppliers = db.query(Supplier).all()

        for supplier in suppliers:
            if supplier.country:
                locations.append(supplier.country)

        shipments = db.query(Shipment).all()

        for shipment in shipments:
            if shipment.origin:
                locations.append(shipment.origin)

            if shipment.destination:
                locations.append(shipment.destination)

        unique_locations = []
        seen = set()

        for location in locations:

            normalized = str(location).strip().lower()

            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_locations.append(
                    str(location).strip()
                )

        return unique_locations

    def collect_suppliers(self, db) -> List[str]:

        suppliers = db.query(Supplier).all()

        names = []

        for supplier in suppliers:
            if supplier.name:
                names.append(
                    supplier.name.strip()
                )

        return list(dict.fromkeys(names))

    def collect_products(self, db) -> List[str]:

        products = []

        inventory_items = db.query(InventoryItem).all()

        for item in inventory_items:
            if item.product_name:
                products.append(
                    item.product_name.strip()
                )

        return list(dict.fromkeys(products))

    def collect_weather(
        self,
        locations: List[str]
    ) -> List[Dict[str, Any]]:

        resolved_locations = location_agent.geocode_many(
            locations
        )

        weather_results = []

        for location in resolved_locations:

            if location.get("status") != "FOUND":
                continue

            try:

                weather = weather_agent.get_weather(
                    latitude=location["latitude"],
                    longitude=location["longitude"],
                    location=location["location"]
                )

                weather_results.append(weather)

            except Exception as exc:

                weather_results.append({
                    "agent": "Weather Intelligence Agent",
                    "location": location["location"],
                    "status": "ERROR",
                    "error": str(exc)
                })

        return weather_results

    def collect_news(
        self,
        locations: List[str],
        suppliers: List[str],
        products: List[str]
    ) -> Dict[str, Any]:

        return news_agent.search(
            locations=locations,
            suppliers=suppliers,
            products=products,
            industries=[
                "supply chain",
                "logistics",
                "manufacturing",
                "semiconductor"
            ],
            max_records=20
        )

    def collect_all(
        self,
        db
    ) -> Dict[str, Any]:

        locations = self.collect_locations(db)

        suppliers = self.collect_suppliers(db)

        products = self.collect_products(db)

        weather = self.collect_weather(
            locations
        )

        news = self.collect_news(
            locations=locations,
            suppliers=suppliers,
            products=products
        )

        return {
            "locations": locations,
            "suppliers": suppliers,
            "products": products,
            "weather": weather,
            "news": news
        }


live_intelligence_service = LiveIntelligenceService()
