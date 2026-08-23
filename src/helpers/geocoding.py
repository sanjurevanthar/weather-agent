"""
Geocoding: Process of converting a place into Coordinates(latitude,longitude)
"""
from dataclasses import dataclass
import httpx

from src.constants import GEOCODING_URL


class GeocodingError(Exception):
    """
    Raised when a city name cannot be resolved to coordinates
    """

@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

async def geocode_city(city: str, client: httpx.AsyncClient) -> Coordinates:

    """
    Resolve a city name to coordinates using Open-Meto API

    If the name cannot be found -> raises a GeocodingError
    """
    try:
        response = await client.get(
            GEOCODING_URL,
            params={"name": city, "count": 1}
        )

        response.raise_for_status()


    except httpx.HTTPError as e:
        raise GeocodingError(
            f"Failed to fetch geocoding service for '{city}':{e}"
        )from e

    results = response.json().get("results")

    if not results:
        raise GeocodingError(f"No location found for '{city}'")
    
    result = results[0]

    return Coordinates(latitude= result["latitude"], longitude= result["longitude"])
    
        



