"""Travel orchestrator that coordinates all MCP servers and GPT service."""

import asyncio
from typing import Dict, List, Any, Optional
from loguru import logger

from .gpt_service import GPTService
from .mcp_client import MCPClient
from ..models.travel_models import TravelRequest, TravelItinerary


class TravelOrchestrator:
    """Orchestrates travel planning across all services."""
    
    def __init__(self):
        self.gpt_service = GPTService()
        self.weather_client = MCPClient("weather", port=3001)
        self.insights_client = MCPClient("travel-insights", port=3002)
        self.booking_client = MCPClient("booking", port=3003)
    
    async def plan_trip(self, travel_request: TravelRequest) -> Dict[str, Any]:
        """Plan a complete trip using all available services."""
        
        logger.info(f"Starting trip planning for {travel_request.destination}")
        
        try:
            # Gather data from all MCP servers concurrently
            weather_task = self.get_weather_data(
                travel_request.destination, 
                travel_request.start_date, 
                travel_request.end_date
            )
            
            insights_task = self.get_travel_insights(
                travel_request.destination,
                travel_request.travel_type,
                travel_request.party_size
            )
            
            # Wait for all data collection tasks
            weather_data, insights_data = await asyncio.gather(
                weather_task, insights_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(weather_data, Exception):
                logger.error(f"Weather data error: {weather_data}")
                weather_data = None
                
            if isinstance(insights_data, Exception):
                logger.error(f"Insights data error: {insights_data}")
                insights_data = None
            
            # Generate travel plan using GPT
            travel_plan = await self.gpt_service.generate_travel_plan(
                travel_request, weather_data, insights_data
            )
            
            # Get flight and hotel options
            flights = await self.search_flights(travel_request)
            hotels = await self.search_hotels(travel_request)
            
            return {
                "status": "success",
                "travel_plan": travel_plan,
                "weather_forecast": weather_data,
                "local_insights": insights_data,
                "flight_options": flights,
                "hotel_options": hotels,
                "request": travel_request.dict()
            }
            
        except Exception as e:
            logger.error(f"Error planning trip: {e}")
            return {
                "status": "error",
                "message": str(e),
                "request": travel_request.dict()
            }
    
    async def get_weather_data(
        self, 
        destination: str, 
        start_date, 
        end_date
    ) -> Optional[Dict]:
        """Get weather data from weather MCP server."""
        
        try:
            return await self.weather_client.call_tool(
                "get_weather_forecast",
                {
                    "location": destination,
                    "start_date": str(start_date),
                    "end_date": str(end_date)
                }
            )
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return None
    
    async def get_travel_insights(
        self, 
        destination: str, 
        travel_type: str, 
        party_size: int
    ) -> Optional[Dict]:
        """Get travel insights from insights MCP server."""
        
        try:
            return await self.insights_client.call_tool(
                "get_destination_insights",
                {
                    "destination": destination,
                    "travel_type": travel_type,
                    "party_size": party_size
                }
            )
        except Exception as e:
            logger.error(f"Error getting travel insights: {e}")
            return None
    
    async def search_flights(self, travel_request: TravelRequest) -> List[Dict]:
        """Search for flight options."""
        
        try:
            return await self.booking_client.call_tool(
                "search_flights",
                {
                    "origin": travel_request.departure_city,
                    "destination": travel_request.destination,
                    "departure_date": str(travel_request.start_date),
                    "return_date": str(travel_request.end_date),
                    "passengers": travel_request.party_size,
                    "budget": travel_request.budget
                }
            )
        except Exception as e:
            logger.error(f"Error searching flights: {e}")
            return []
    
    async def search_hotels(self, travel_request: TravelRequest) -> List[Dict]:
        """Search for hotel options."""
        
        try:
            return await self.booking_client.call_tool(
                "search_hotels",
                {
                    "destination": travel_request.destination,
                    "check_in": str(travel_request.start_date),
                    "check_out": str(travel_request.end_date),
                    "guests": travel_request.party_size,
                    "budget": travel_request.budget
                }
            )
        except Exception as e:
            logger.error(f"Error searching hotels: {e}")
            return []
    
    async def book_trip(self, booking_request: Dict[str, Any]) -> Dict[str, Any]:
        """Book a complete trip."""
        
        logger.info("Starting trip booking process")
        
        try:
            return await self.booking_client.call_tool(
                "book_trip",
                booking_request
            )
        except Exception as e:
            logger.error(f"Error booking trip: {e}")
            return {
                "status": "error",
                "message": str(e)
            }