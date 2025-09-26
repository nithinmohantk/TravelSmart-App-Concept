"""Booking MCP Server for handling travel bookings."""

import uuid
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
import uvicorn
from loguru import logger


class BookingServer:
    """Booking MCP Server implementation."""
    
    def __init__(self):
        self.app = FastAPI(title="Booking MCP Server", version="1.0.0")
        self.bookings = {}
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "booking-mcp-server"}
        
        @self.app.post("/call")
        async def call_tool(request: Dict[str, Any]):
            tool_name = request.get("tool")
            parameters = request.get("parameters", {})
            
            if tool_name == "search_flights":
                return await self.search_flights(parameters)
            elif tool_name == "search_hotels":
                return await self.search_hotels(parameters)
            elif tool_name == "book_trip":
                return await self.book_trip(parameters)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
    
    async def search_flights(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        origin = params.get("origin", "New York")
        destination = params.get("destination", "Paris")
        
        flights = [
            {
                "flight_id": "FL001",
                "airline": "Air France",
                "flight_number": "AF007",
                "origin": origin,
                "destination": destination,
                "departure_time": "08:30",
                "arrival_time": "20:45",
                "duration": "8h 15m",
                "price": 650.00,
                "stops": 0
            },
            {
                "flight_id": "FL002", 
                "airline": "Delta Airlines",
                "flight_number": "DL123",
                "origin": origin,
                "destination": destination,
                "departure_time": "14:20",
                "arrival_time": "02:35+1",
                "duration": "8h 15m",
                "price": 580.00,
                "stops": 0
            }
        ]
        
        return flights
    
    async def search_hotels(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        destination = params.get("destination", "Paris")
        
        hotels = [
            {
                "hotel_id": "HT001",
                "name": "Grand Hotel Central",
                "rating": 4.5,
                "price_per_night": 180.00,
                "location": "City Center",
                "amenities": ["WiFi", "Pool", "Spa", "Restaurant"]
            },
            {
                "hotel_id": "HT002",
                "name": "Boutique Palace",
                "rating": 4.8,
                "price_per_night": 250.00,
                "location": "Historic District",
                "amenities": ["WiFi", "Concierge", "Restaurant", "Bar"]
            }
        ]
        
        return hotels
    
    async def book_trip(self, params: Dict[str, Any]) -> Dict[str, Any]:
        booking_id = str(uuid.uuid4())
        
        booking = {
            "booking_id": booking_id,
            "status": "confirmed",
            "confirmation_number": f"TS{booking_id[:8].upper()}",
            "total_cost": 1000.00,
            "booking_date": datetime.now().isoformat()
        }
        
        self.bookings[booking_id] = booking
        
        return {
            "success": True,
            "booking_id": booking_id,
            "confirmation_number": booking["confirmation_number"],
            "total_cost": 1000.00,
            "status": "confirmed"
        }
    
    def run(self, host: str = "localhost", port: int = 3003):
        logger.info(f"Starting Booking MCP Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


def main():
    server = BookingServer()
    server.run(port=3003)
