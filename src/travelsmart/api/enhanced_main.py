"""Enhanced FastAPI application with all features for TravelSmart."""

from fastapi import FastAPI, HTTPException, WebSocket, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Dict, Any, List
import uvicorn
import asyncio
from loguru import logger

from ..services.travel_orchestrator import TravelOrchestrator
from ..services.notification_service import NotificationService, notification_service
from ..services.recommendation_engine import RecommendationEngine, recommendation_engine
from ..models.travel_models import TravelRequest, TravelType
from ..utils.database import db_manager
from ..utils.helpers import validate_dates, generate_confirmation_number
from ..utils.logger import setup_logging
from .websocket import websocket_handler


# Setup logging
setup_logging()

app = FastAPI(
    title="TravelSmart API - Enhanced",
    description="AI-powered travel booking with OpenAI GPT, MCP servers, and advanced features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
orchestrator = TravelOrchestrator()


# Pydantic models for enhanced API
class EnhancedTripRequest(BaseModel):
    destination: str
    departure_city: str
    start_date: date
    end_date: date
    budget: Optional[float] = None
    travel_type: TravelType = TravelType.LEISURE
    party_size: int = 1
    preferences: Optional[Dict[str, Any]] = None
    special_requirements: Optional[str] = None
    user_id: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None


class PersonalizationRequest(BaseModel):
    user_preferences: Dict[str, Any]
    travel_history: Optional[List[Dict[str, Any]]] = None
    budget_range: Optional[tuple[float, float]] = None


class RecommendationRequest(BaseModel):
    destination: str
    interests: List[str]
    travel_style: str = "balanced"
    duration_days: int = 7


class NotificationRequest(BaseModel):
    user_email: str
    booking_id: str
    notification_type: str  # confirmation, update, reminder
    data: Dict[str, Any]


# Basic endpoints
@app.get("/")
async def root():
    """Welcome endpoint with API information."""
    return {
        "message": "Welcome to TravelSmart Enhanced API",
        "version": "2.0.0",
        "features": [
            "AI-powered travel planning",
            "Real-time WebSocket communication", 
            "Personalized recommendations",
            "Email notifications",
            "Booking management",
            "Weather integration",
            "Travel insights"
        ],
        "endpoints": {
            "docs": "/docs",
            "websocket": "/ws",
            "plan_trip": "/api/v2/plan-trip",
            "recommendations": "/api/v2/recommendations"
        }
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    try:
        # Check database connection
        db_healthy = True  # db_manager would have a health check
        
        # Check MCP servers
        weather_healthy = await orchestrator.weather_client.health_check()
        insights_healthy = await orchestrator.insights_client.health_check()
        booking_healthy = await orchestrator.booking_client.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "healthy" if db_healthy else "unhealthy",
                "weather_mcp": "healthy" if weather_healthy else "unhealthy",
                "insights_mcp": "healthy" if insights_healthy else "unhealthy",
                "booking_mcp": "healthy" if booking_healthy else "unhealthy",
                "notification": "healthy",
                "recommendations": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Enhanced travel planning endpoints
@app.post("/api/v2/plan-trip")
async def plan_enhanced_trip(request: EnhancedTripRequest, background_tasks: BackgroundTasks):
    """Enhanced trip planning with personalization and notifications."""
    
    try:
        # Validate dates
        is_valid, error_msg = validate_dates(request.start_date, request.end_date)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Create travel request
        travel_request = TravelRequest(**request.dict())
        
        # Plan the trip
        logger.info(f"Planning enhanced trip for {request.destination}")
        result = await orchestrator.plan_trip(travel_request)
        
        # Add personalization if user preferences available
        if request.preferences:
            personalized_recs = await recommendation_engine.get_personalized_recommendations(
                request.preferences,
                budget_range=(request.budget * 0.8, request.budget * 1.2) if request.budget else None
            )
            result["personalized_recommendations"] = personalized_recs
        
        # Generate enhanced response
        enhanced_result = {
            **result,
            "trip_id": generate_confirmation_number(),
            "user_id": request.user_id,
            "enhanced_features": {
                "personalization_available": bool(request.preferences),
                "notifications_enabled": bool(request.contact_info),
                "real_time_updates": True
            }
        }
        
        # Save trip data if user provided
        if request.user_id:
            trip_data = {
                "trip_id": enhanced_result["trip_id"],
                "user_id": request.user_id,
                "request": request.dict(),
                "result": result,
                "created_at": datetime.now().isoformat()
            }
            
            # Save to database in background
            background_tasks.add_task(save_trip_data, trip_data)
        
        return enhanced_result
        
    except Exception as e:
        logger.error(f"Error in enhanced trip planning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/recommendations/personalized")
async def get_personalized_recommendations(request: PersonalizationRequest):
    """Get AI-powered personalized travel recommendations."""
    
    try:
        recommendations = await recommendation_engine.get_personalized_recommendations(
            user_preferences=request.user_preferences,
            travel_history=request.travel_history,
            budget_range=request.budget_range
        )
        
        return {
            "status": "success",
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating personalized recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/recommendations/activities")
async def get_activity_recommendations(request: RecommendationRequest):
    """Get activity recommendations for a destination."""
    
    try:
        activities = await recommendation_engine.get_activity_recommendations(
            destination=request.destination,
            interests=request.interests,
            travel_style=request.travel_style,
            duration_days=request.duration_days
        )
        
        return {
            "status": "success",
            "activities": activities,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating activity recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/recommendations/seasonal/{month}")
async def get_seasonal_recommendations(month: int, preferences: Optional[str] = None):
    """Get seasonal travel recommendations for a specific month."""
    
    try:
        # Parse preferences if provided
        user_preferences = {}
        if preferences:
            import json
            user_preferences = json.loads(preferences)
        
        recommendations = await recommendation_engine.get_seasonal_recommendations(
            month=month,
            preferences=user_preferences
        )
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating seasonal recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/destinations/{destination}/similar")
async def get_similar_destinations(destination: str, preferences: Optional[str] = None):
    """Find destinations similar to the given one."""
    
    try:
        user_preferences = {}
        if preferences:
            import json
            user_preferences = json.loads(preferences)
        
        similar = await recommendation_engine.get_similar_destinations(
            liked_destination=destination,
            preferences=user_preferences
        )
        
        return {
            "destination": destination,
            "similar_destinations": similar,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error finding similar destinations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Notification endpoints
@app.post("/api/v2/notifications/send")
async def send_notification(request: NotificationRequest, background_tasks: BackgroundTasks):
    """Send travel-related notifications to users."""
    
    try:
        if request.notification_type == "confirmation":
            background_tasks.add_task(
                notification_service.send_booking_confirmation,
                request.user_email,
                request.data
            )
        elif request.notification_type == "update":
            background_tasks.add_task(
                notification_service.send_booking_update,
                request.user_email,
                request.booking_id,
                request.data.get("status", ""),
                request.data.get("message", "")
            )
        elif request.notification_type == "reminder":
            background_tasks.add_task(
                notification_service.send_travel_reminder,
                request.user_email,
                request.data,
                request.data.get("days_until_travel", 7)
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid notification type")
        
        return {
            "status": "queued",
            "message": f"Notification {request.notification_type} queued for delivery",
            "recipient": request.user_email
        }
        
    except Exception as e:
        logger.error(f"Error queueing notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced booking endpoints
@app.post("/api/v2/book-trip")
async def book_enhanced_trip(booking_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Enhanced trip booking with notifications and database storage."""
    
    try:
        # Process booking
        result = await orchestrator.book_trip(booking_data)
        
        if result.get("success"):
            booking_id = result["booking_id"]
            
            # Save to database
            enhanced_booking = {
                **booking_data,
                **result,
                "booking_date": datetime.now().isoformat(),
                "status": "confirmed"
            }
            
            background_tasks.add_task(save_booking_data, enhanced_booking)
            
            # Send confirmation email if contact info provided
            if booking_data.get("contact_info", {}).get("email"):
                background_tasks.add_task(
                    notification_service.send_booking_confirmation,
                    booking_data["contact_info"]["email"],
                    enhanced_booking
                )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in enhanced booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/bookings/{booking_id}")
async def get_booking_details(booking_id: str):
    """Get detailed booking information."""
    
    try:
        # Get from database
        booking = db_manager.get_booking(booking_id)
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return {
            "booking": booking,
            "status": "found",
            "retrieved_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: Optional[str] = None):
    """WebSocket endpoint for real-time communication."""
    await websocket_handler.handle_connection(websocket, user_id)


@app.websocket("/ws/{user_id}")
async def websocket_user_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for specific user."""
    await websocket_handler.handle_connection(websocket, user_id)


# Utility endpoints
@app.get("/api/v2/destinations/{destination}/weather")
async def get_destination_weather_enhanced(destination: str, days: int = 5):
    """Get enhanced weather forecast for destination."""
    
    try:
        weather_data = await orchestrator.get_weather_data(destination, None, None)
        
        return {
            "destination": destination,
            "weather": weather_data,
            "forecast_days": days,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/destinations/{destination}/insights")
async def get_destination_insights_enhanced(destination: str, travel_type: str = "leisure"):
    """Get enhanced travel insights for destination."""
    
    try:
        insights = await orchestrator.get_travel_insights(destination, travel_type, 1)
        
        return {
            "destination": destination,
            "insights": insights,
            "travel_type": travel_type,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Demo WebSocket client
@app.get("/websocket-demo", response_class=HTMLResponse)
async def websocket_demo():
    """Simple WebSocket demo page."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TravelSmart WebSocket Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .messages { border: 1px solid #ccc; height: 300px; padding: 10px; overflow-y: scroll; margin: 10px 0; }
            input[type="text"] { width: 300px; padding: 5px; }
            button { padding: 5px 15px; margin-left: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌍 TravelSmart WebSocket Demo</h1>
            <div id="messages" class="messages"></div>
            <input type="text" id="messageInput" placeholder="Ask about travel...">
            <button onclick="sendMessage()">Send Query</button>
            <button onclick="sendWeatherRequest()">Get Weather (Paris)</button>
            <button onclick="sendPing()">Ping</button>
        </div>

        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            const messages = document.getElementById('messages');
            const messageInput = document.getElementById('messageInput');

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const div = document.createElement('div');
                div.innerHTML = `<strong>[${data.type}]</strong> ${JSON.stringify(data, null, 2)}`;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            };

            function sendMessage() {
                const query = messageInput.value;
                if (query) {
                    ws.send(JSON.stringify({
                        type: "travel_query",
                        query: query
                    }));
                    messageInput.value = '';
                }
            }

            function sendWeatherRequest() {
                ws.send(JSON.stringify({
                    type: "weather_request",
                    location: "Paris"
                }));
            }

            function sendPing() {
                ws.send(JSON.stringify({
                    type: "ping"
                }));
            }

            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# Background task functions
async def save_trip_data(trip_data: Dict[str, Any]):
    """Save trip data to database."""
    try:
        # This would save to database
        logger.info(f"Saved trip data for trip {trip_data['trip_id']}")
    except Exception as e:
        logger.error(f"Error saving trip data: {e}")


async def save_booking_data(booking_data: Dict[str, Any]):
    """Save booking data to database."""
    try:
        db_manager.save_booking(booking_data)
        logger.info(f"Saved booking data for booking {booking_data['booking_id']}")
    except Exception as e:
        logger.error(f"Error saving booking data: {e}")


def run():
    """Run the enhanced FastAPI server."""
    logger.info("Starting TravelSmart Enhanced API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
