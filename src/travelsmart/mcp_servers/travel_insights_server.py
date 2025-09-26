"""Travel Insights MCP Server for providing destination insights and recommendations."""

from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
import uvicorn
from loguru import logger


class TravelInsightsServer:
    """Travel Insights MCP Server implementation."""
    
    def __init__(self):
        self.app = FastAPI(title="Travel Insights MCP Server", version="1.0.0")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "travel-insights-mcp-server"}
        
        @self.app.post("/call")
        async def call_tool(request: Dict[str, Any]):
            tool_name = request.get("tool")
            parameters = request.get("parameters", {})
            
            if tool_name == "get_destination_insights":
                return await self.get_destination_insights(parameters)
            elif tool_name == "get_attractions":
                return await self.get_attractions(parameters)
            elif tool_name == "get_restaurants":
                return await self.get_restaurants(parameters)
            elif tool_name == "get_local_tips":
                return await self.get_local_tips(parameters)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
    
    async def get_destination_insights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive destination insights."""
        
        destination = params.get("destination", "Paris")
        travel_type = params.get("travel_type", "leisure")
        
        # Mock destination data
        destinations = {
            "paris": {
                "overview": "The City of Light, famous for art, fashion, gastronomy and culture",
                "best_time_to_visit": "April-June, September-October",
                "currency": "EUR",
                "language": "French",
                "timezone": "CET",
                "safety_rating": 8.5,
                "cost_level": "High",
                "top_attractions": [
                    "Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", 
                    "Arc de Triomphe", "Sacré-Cœur"
                ],
                "local_transport": ["Metro", "Bus", "Taxi", "Vélib bikes"],
                "cultural_tips": [
                    "Learn basic French phrases",
                    "Dress elegantly",
                    "Dining etiquette is important"
                ]
            },
            "tokyo": {
                "overview": "A vibrant metropolis blending traditional culture with cutting-edge technology",
                "best_time_to_visit": "March-May, September-November",
                "currency": "JPY",
                "language": "Japanese",
                "timezone": "JST",
                "safety_rating": 9.5,
                "cost_level": "High",
                "top_attractions": [
                    "Senso-ji Temple", "Tokyo Skytree", "Shibuya Crossing",
                    "Meiji Shrine", "Tsukiji Fish Market"
                ],
                "local_transport": ["JR Lines", "Metro", "Taxi"],
                "cultural_tips": [
                    "Bow when greeting",
                    "Remove shoes indoors",
                    "Don't tip in restaurants"
                ]
            }
        }
        
        destination_key = destination.lower()
        if destination_key in destinations:
            insights = destinations[destination_key]
        else:
            # Generic insights for unknown destinations
            insights = {
                "overview": f"A wonderful destination to explore: {destination}",
                "best_time_to_visit": "Check local weather patterns",
                "currency": "Local currency",
                "language": "Local language",
                "timezone": "Local timezone",
                "safety_rating": 7.0,
                "cost_level": "Medium",
                "top_attractions": ["Historic sites", "Local markets", "Cultural centers"],
                "local_transport": ["Public transport", "Taxi", "Walking"],
                "cultural_tips": ["Respect local customs", "Learn basic phrases", "Dress appropriately"]
            }
        
        return {
            "destination": destination,
            "travel_type": travel_type,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_attractions(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get attractions for a destination."""
        
        destination = params.get("destination", "Paris")
        category = params.get("category", "all")
        
        # Mock attractions data
        attractions = [
            {
                "name": "Historic Monument",
                "category": "historical",
                "rating": 4.5,
                "price": "€15",
                "duration": "2-3 hours",
                "description": "A beautiful historic site with rich cultural significance"
            },
            {
                "name": "Art Museum",
                "category": "museum",
                "rating": 4.8,
                "price": "€20",
                "duration": "3-4 hours",
                "description": "World-class art collection spanning centuries"
            },
            {
                "name": "Central Park",
                "category": "nature",
                "rating": 4.3,
                "price": "Free",
                "duration": "1-2 hours",
                "description": "Beautiful green space in the heart of the city"
            }
        ]
        
        return attractions
    
    async def get_restaurants(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get restaurant recommendations."""
        
        destination = params.get("destination", "Paris")
        cuisine = params.get("cuisine", "local")
        budget = params.get("budget", "medium")
        
        restaurants = [
            {
                "name": "Le Petit Bistro",
                "cuisine": "French",
                "rating": 4.6,
                "price_range": "€€€",
                "specialties": ["Coq au vin", "Bouillabaisse", "Crème brûlée"],
                "atmosphere": "Cozy, traditional"
            },
            {
                "name": "Modern Fusion",
                "cuisine": "International",
                "rating": 4.4,
                "price_range": "€€€€",
                "specialties": ["Fusion dishes", "Innovative cocktails"],
                "atmosphere": "Contemporary, upscale"
            },
            {
                "name": "Street Food Market",
                "cuisine": "Various",
                "rating": 4.2,
                "price_range": "€",
                "specialties": ["Local street food", "Fresh ingredients"],
                "atmosphere": "Casual, vibrant"
            }
        ]
        
        return restaurants
    
    async def get_local_tips(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get local tips and cultural insights."""
        
        destination = params.get("destination", "Paris")
        
        tips = {
            "transportation": [
                "Buy a metro day pass for unlimited travel",
                "Download local transport apps",
                "Walking is often faster for short distances"
            ],
            "money": [
                "Carry some cash for small vendors",
                "Notify your bank about travel",
                "Check if tipping is customary"
            ],
            "safety": [
                "Keep copies of important documents",
                "Be aware of common tourist scams",
                "Stay in well-lit areas at night"
            ],
            "etiquette": [
                "Learn basic greetings in local language",
                "Respect local customs and traditions",
                "Dress appropriately for religious sites"
            ],
            "hidden_gems": [
                "Ask locals for their favorite spots",
                "Explore neighborhoods beyond tourist areas",
                "Try local markets and food halls"
            ]
        }
        
        return {
            "destination": destination,
            "tips": tips,
            "generated_at": datetime.now().isoformat()
        }
    
    def run(self, host: str = "localhost", port: int = 3002):
        """Run the travel insights server."""
        logger.info(f"Starting Travel Insights MCP Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


def main():
    """Main entry point for travel insights server."""
    server = TravelInsightsServer()
    server.run(port=3002)