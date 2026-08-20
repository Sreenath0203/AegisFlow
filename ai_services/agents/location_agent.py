import requests
from typing import Dict, Any, List


class LocationAgent:
    """
    Global location intelligence service.

    Converts supply-chain location names into geographic coordinates
    using the Open-Meteo geocoding service.
    """

    name = "Global Location Agent"

    def geocode(self, location: str) -> Dict[str, Any]:

        if not location or not str(location).strip():
            return {
                "location": location,
                "status": "INVALID"
            }

        location = str(location).strip()

        url = "https://geocoding-api.open-meteo.com/v1/search"

        params = {
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        response = requests.get(
            url,
            params=params,
            timeout=15,
            headers={
                "User-Agent": "AegisFlow-Global-Supply-Chain/1.0"
            }
        )

        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            return {
                "location": location,
                "status": "NOT_FOUND"
            }

        result = results[0]

        return {
            "location": location,
            "resolved_name": result.get("name"),
            "country": result.get("country"),
            "country_code": result.get("country_code"),
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
            "timezone": result.get("timezone"),
            "status": "FOUND"
        }

    def geocode_many(
        self,
        locations: List[str]
    ) -> List[Dict[str, Any]]:

        unique_locations = []
        seen = set()

        for location in locations:
            if not location:
                continue

            key = str(location).strip().lower()

            if key not in seen:
                seen.add(key)
                unique_locations.append(str(location).strip())

        results = []

        for location in unique_locations:
            try:
                result = self.geocode(location)
                results.append(result)
            except Exception as exc:
                results.append({
                    "location": location,
                    "status": "ERROR",
                    "error": str(exc)
                })

        return results


location_agent = LocationAgent()
