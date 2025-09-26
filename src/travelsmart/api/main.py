"""Main FastAPI application for TravelSmart."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict, Any
import uvicorn
from loguru import logger

from ..services.travel_orchestrator import TravelOrchestrator
from ..models.travel_models import TravelRequest, TravelType


app = FastAPI(
    title="TravelSmart API",
    description="AI-powered travel booking with OpenAI GPT and MCP servers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = TravelOrchestrator()


class PlanTripRequest(BaseModel):
    destination: str
    departure_city: str
    start_date: date
    end_date: date
    budget: Optional[float] = None
    travel_type: TravelType = TravelType.LEISURE
    party_size: int = 1
    preferences: Optional[Dict[str, Any]] = None
    special_requirements: Optional[str] = None


@app.get("/")
async def root():
    return {"message": "Welcome to TravelSmart API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "travelsmart-api"}


@app.post("/plan-trip")
async def plan_trip(request: PlanTripRequest):
    """Plan a trip using AI and MCP servers."""
    
    try:
        travel_request = TravelRequest(**request.dict())
        result = await orchestrator.plan_trip(travel_request)
        return result
    except Exception as e:
        logger.error(f"Error planning trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/book-trip")
async def book_trip(booking_data: Dict[str, Any]):
    """Book a trip."""
    
    try:
        result = await orchestrator.book_trip(booking_data)
        return result
    except Exception as e:
        logger.error(f"Error booking trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/destinations/{destination}/weather")
async def get_destination_weather(destination: str):
    """Get weather forecast for a destination."""
    
    try:
        weather_data = await orchestrator.get_weather_data(destination, None, None)
        return {"destination": destination, "weather": weather_data}
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/destinations/{destination}/insights")
async def get_destination_insights(destination: str, travel_type: str = "leisure"):
    """Get travel insights for a destination."""
    
    try:
        insights = await orchestrator.get_travel_insights(destination, travel_type, 1)
        return {"destination": destination, "insights": insights}
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def run():
    """Run the FastAPI server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
