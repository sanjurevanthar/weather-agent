"""
Weather Providers: Use the coordinates to produce a weather report
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from src.constants import FORECAST_URL
from src.helpers.geocoding import Coordinates

class WeatherProviderError(Exception):
    """
    Raised when the data cannot be retrieved or processed from the API
    """

@dataclass(frozen=True)
class WeatherReport:
    temperature_c: float
    windspeed_kmh: float
    precipitation_mm: float
    is_day: bool

    def as_text_report(self, city: str) -> str:
        return (
            f"Weather in {city}: {self.temperature_c}C,"
            f"Wind {self.windspeed_kmh} km/h,"
            f"Precipitation {self.precipitation_mm} mm"
        )

class WeatherProvider(ABC):

    @abstractmethod
    async def get_current_weather(self, coordinates: Coordinates)-> WeatherReport:
        ...

class OpenMeteoProvider(WeatherProvider):
    """
    Implement the WeatherProvider interface for Open-Meteo
    """

    def __init__(self, client: httpx.AsyncClient):
        self.client = client
    
    async def get_current_weather(self, coordinates: Coordinates) -> WeatherReport:

        try:
            response = await self.client.get(
                FORECAST_URL,
                params = {
                    "latitude": coordinates.latitude,
                    "longitude": coordinates.longitude,
                    "current": (
                        "temperature_2m,is_day,precipitation,"
                        "rain,windspeed_10m,winddirection_10m"
                    ),
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise WeatherProviderError(f"Failed to reach weather service: {e}") from e
        
        result = response.json().get("current")
        if not result:
            raise WeatherProviderError("Weather service returned with no current data")
        
        return WeatherReport(
            temperature_c = result["temperature_2m"],
            windspeed_kmh= result["windspeed_10m"],
            precipitation_mm = result["precipitation"],
            is_day = bool(result["is_day"])
        )
            