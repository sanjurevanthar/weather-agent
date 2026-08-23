"""
This MCP server exposes only a single tool

1. get_weather -> gives weather report for a city 

Failures comes as readable sentence 
"""

from asyncio import coroutines
import httpx
from fastmcp import FastMCP

from src.helpers.weather_provider import OpenMeteoProvider, WeatherProviderError
from src.helpers.geocoding import geocode_city, GeocodingError

mcp = FastMCP("rev-weather-server")


_http_client = httpx.AsyncClient(timeout=10)
_provider = OpenMeteoProvider(_http_client)

@mcp.tool()
async def get_weather(city: str):

    try:
        coordinates = await geocode_city(city, _http_client)
        report = await _provider.get_current_weather(coordinates)
    
    except(GeocodingError, WeatherProviderError) as e:
        return f"Failed to get weather for '{city}': {e}"
    
    return report.as_text_report(city)

if __name__ == "__main__":
    mcp.run(transport="stdio")
        
