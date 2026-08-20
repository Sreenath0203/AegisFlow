import requests
from datetime import datetime, timezone


class WeatherAgent:
    """
    Live weather intelligence agent.

    Gets real current and forecast weather for any latitude/longitude.
    The location is supplied dynamically by the supply-chain network.
    """

    name = "Weather Intelligence Agent"

    def get_weather(
        self,
        latitude: float,
        longitude: float,
        location: str = "Unknown"
    ) -> dict:

        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "wind_speed_10m,"
                "wind_gusts_10m"
            ),
            "hourly": (
                "precipitation_probability,"
                "wind_speed_10m,"
                "wind_gusts_10m"
            ),
            "forecast_days": 3,
            "timezone": "auto"
        }

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})

        wind = float(current.get("wind_speed_10m") or 0)
        gusts = float(current.get("wind_gusts_10m") or 0)
        rain = float(current.get("precipitation") or 0)

        if gusts >= 100 or wind >= 75:
            risk = "CRITICAL"
        elif gusts >= 75 or wind >= 50:
            risk = "HIGH"
        elif gusts >= 40 or rain >= 20:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "agent": self.name,
            "source": "Open-Meteo",
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "observed_at": current.get("time"),
            "temperature_c": current.get("temperature_2m"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "precipitation_mm": rain,
            "wind_speed_kmh": wind,
            "wind_gusts_kmh": gusts,
            "weather_risk_level": risk,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }


weather_agent = WeatherAgent()
