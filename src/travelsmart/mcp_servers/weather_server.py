"""Weather MCP Server for providing weather data and forecasts."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from loguru import logger

from ..config import settings


class WeatherRequest(BaseModel):
    location: str
    start_date: str
    end_date: str


class WeatherServer:
    """Weather MCP Server implementation."""
    
    def __init__(self):
        self.app = FastAPI(title="Weather MCP Server", version="1.0.0")
        self.api_key = settings.weather_api_key or "demo_key"
        self.base_url = settings.weather_base_url
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "weather-mcp-server"}
        
        @self.app.post("/call")
        async def call_tool(request: Dict[str, Any]):
            tool_name = request.get("tool")
            parameters = request.get("parameters", {})
            
            if tool_name == "get_weather_forecast":
                return await self.get_weather_forecast(parameters)
            elif tool_name == "get_current_weather":
                return await self.get_current_weather(parameters)
            elif tool_name == "get_weather_alerts":
                return await self.get_weather_alerts(parameters)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
    
    async def get_weather_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather forecast for a location and date range."""
        
        location = params.get("location")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        
        if not location:
            raise HTTPException(status_code=400, detail="Location is required")
        
        try:
            # Get coordinates for the location
            coords = await self._get_coordinates(location)
            if not coords:
                return self._generate_mock_weather_forecast(location, start_date, end_date)
            
            # Get weather forecast
            forecast = await self._fetch_weather_forecast(coords, start_date, end_date)
            
            return {
                "location": location,
                "coordinates": coords,
                "forecast": forecast,
                "start_date": start_date,
                "end_date": end_date
            }
            
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            # Return mock data on error
            return self._generate_mock_weather_forecast(location, start_date, end_date)
    
    async def get_current_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current weather for a location."""
        
        location = params.get("location")
        if not location:
            raise HTTPException(status_code=400, detail="Location is required")
        
        try:
            coords = await self._get_coordinates(location)
            if not coords:
                return self._generate_mock_current_weather(location)
            
            current = await self._fetch_current_weather(coords)
            
            return {
                "location": location,
                "coordinates": coords,
                "current_weather": current
            }
            
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return self._generate_mock_current_weather(location)
    
    async def get_weather_alerts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather alerts for a location."""
        
        location = params.get("location")
        if not location:
            raise HTTPException(status_code=400, detail="Location is required")
        
        return {
            "location": location,
            "alerts": [],  # Mock implementation
            "message": "No active weather alerts"
        }
    
    async def _get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a location using geocoding API."""
        
        if self.api_key == "demo_key":
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://api.openweathermap.org/geo/1.0/direct"
                params = {
                    "q": location,
                    "limit": 1,
                    "appid": self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:
                            return {
                                "lat": data[0]["lat"],
                                "lon": data[0]["lon"]
                            }
            return None
            
        except Exception as e:
            logger.error(f"Error getting coordinates: {e}")
            return None
    
    async def _fetch_weather_forecast(self, coords: Dict[str, float], start_date: str, end_date: str) -> List[Dict]:
        """Fetch weather forecast from API."""
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/forecast"
                params = {
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_forecast_data(data)
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return []
    
    async def _fetch_current_weather(self, coords: Dict[str, float]) -> Dict:
        """Fetch current weather from API."""
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/weather"
                params = {
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_current_weather_data(data)
            
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return {}
    
    def _process_forecast_data(self, data: Dict) -> List[Dict]:
        """Process forecast data from API response."""
        
        forecast = []
        for item in data.get("list", [])[:5]:  # Limit to 5 days
            forecast.append({
                "date": item["dt_txt"],
                "temperature": {
                    "current": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "min": item["main"]["temp_min"],
                    "max": item["main"]["temp_max"]
                },
                "humidity": item["main"]["humidity"],
                "weather": {
                    "main": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"]
                },
                "wind": {
                    "speed": item["wind"]["speed"],
                    "direction": item["wind"].get("deg", 0)
                }
            })
        
        return forecast
    
    def _process_current_weather_data(self, data: Dict) -> Dict:
        """Process current weather data from API response."""
        
        return {
            "temperature": {
                "current": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "min": data["main"]["temp_min"],
                "max": data["main"]["temp_max"]
            },
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "weather": {
                "main": data["weather"][0]["main"],
                "description": data["weather"][0]["description"]
            },
            "wind": {
                "speed": data["wind"]["speed"],
                "direction": data["wind"].get("deg", 0)
            },
            "visibility": data.get("visibility", 0) / 1000,  # Convert to km
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_mock_weather_forecast(self, location: str, start_date: str, end_date: str) -> List[Dict]:
        """Generate mock weather forecast data."""
        
        forecast = []
        base_temp = 20  # Base temperature in Celsius
        
        for i in range(5):
            date = datetime.now() + timedelta(days=i)
            temp = base_temp + (i * 2) - 5  # Vary temperature
            
            forecast.append({
                "date": date.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": {
                    "current": temp,
                    "feels_like": temp - 2,
                    "min": temp - 5,
                    "max": temp + 5
                },
                "humidity": 60 + (i * 5),
                "weather": {
                    "main": "Clear" if i % 2 == 0 else "Cloudy",
                    "description": "Clear sky" if i % 2 == 0 else "Partly cloudy"
                },
                "wind": {
                    "speed": 5 + i,
                    "direction": 180
                }
            })
        
        return forecast
    
    def _generate_mock_current_weather(self, location: str) -> Dict:
        """Generate mock current weather data."""
        
        return {
            "temperature": {
                "current": 22,
                "feels_like": 20,
                "min": 18,
                "max": 26
            },
            "humidity": 65,
            "pressure": 1013,
            "weather": {
                "main": "Clear",
                "description": "Clear sky"
            },
            "wind": {
                "speed": 3.5,
                "direction": 180
            },
            "visibility": 10,
            "timestamp": datetime.now().isoformat()
        }
    
    def run(self, host: str = "localhost", port: int = 3001):
        """Run the weather server."""
        logger.info(f"Starting Weather MCP Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


def main():
    """Main entry point for weather server."""
    server = WeatherServer()
    server.run(port=settings.mcp_weather_port)


if __name__ == "__main__":
    main()