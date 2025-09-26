"""WebSocket endpoints for real-time communication."""

import asyncio
import json
from typing import Dict, List, Any
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from ..services.travel_orchestrator import TravelOrchestrator
from ..utils.cache import cache_manager


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            self.user_connections[user_id] = websocket
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
    
    async def send_personal_json(self, data: Dict[str, Any], websocket: WebSocket):
        """Send JSON data to a specific WebSocket."""
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending WebSocket JSON: {e}")
    
    async def send_to_user(self, message: str, user_id: str):
        """Send a message to a specific user."""
        if user_id in self.user_connections:
            await self.send_personal_message(message, self.user_connections[user_id])
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients."""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.active_connections.remove(connection)


class TravelWebSocketHandler:
    """Handle travel-related WebSocket communications."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.orchestrator = TravelOrchestrator()
    
    async def handle_connection(self, websocket: WebSocket, user_id: str = None):
        """Handle a new WebSocket connection."""
        await self.manager.connect(websocket, user_id)
        
        try:
            # Send welcome message
            await self.manager.send_personal_json({
                "type": "welcome",
                "message": "Connected to TravelSmart WebSocket",
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
            
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process different message types
                await self._process_message(websocket, message, user_id)
                
        except WebSocketDisconnect:
            self.manager.disconnect(websocket, user_id)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            self.manager.disconnect(websocket, user_id)
    
    async def _process_message(self, websocket: WebSocket, message: Dict[str, Any], user_id: str = None):
        """Process different types of WebSocket messages."""
        
        msg_type = message.get("type")
        
        try:
            if msg_type == "ping":
                await self._handle_ping(websocket, message)
            
            elif msg_type == "travel_query":
                await self._handle_travel_query(websocket, message, user_id)
            
            elif msg_type == "booking_status":
                await self._handle_booking_status(websocket, message, user_id)
            
            elif msg_type == "weather_request":
                await self._handle_weather_request(websocket, message)
            
            elif msg_type == "live_search":
                await self._handle_live_search(websocket, message)
            
            else:
                await self.manager.send_personal_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                }, websocket)
        
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.manager.send_personal_json({
                "type": "error",
                "message": "Error processing request"
            }, websocket)
    
    async def _handle_ping(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle ping messages."""
        await self.manager.send_personal_json({
            "type": "pong",
            "timestamp": asyncio.get_event_loop().time()
        }, websocket)
    
    async def _handle_travel_query(self, websocket: WebSocket, message: Dict[str, Any], user_id: str = None):
        """Handle travel planning queries."""
        
        query = message.get("query", "")
        
        # Send acknowledgment
        await self.manager.send_personal_json({
            "type": "query_received",
            "message": "Processing your travel query..."
        }, websocket)
        
        try:
            # Use GPT to answer the query
            response = await self.orchestrator.gpt_service.answer_travel_question(query)
            
            await self.manager.send_personal_json({
                "type": "travel_response",
                "query": query,
                "response": response,
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
            
        except Exception as e:
            logger.error(f"Error handling travel query: {e}")
            await self.manager.send_personal_json({
                "type": "error",
                "message": "Error processing travel query"
            }, websocket)
    
    async def _handle_booking_status(self, websocket: WebSocket, message: Dict[str, Any], user_id: str = None):
        """Handle booking status requests."""
        
        booking_id = message.get("booking_id")
        
        if not booking_id:
            await self.manager.send_personal_json({
                "type": "error",
                "message": "Booking ID required"
            }, websocket)
            return
        
        try:
            # Get booking status (this would normally query the database)
            status = {
                "booking_id": booking_id,
                "status": "confirmed",  # Mock status
                "last_updated": asyncio.get_event_loop().time()
            }
            
            await self.manager.send_personal_json({
                "type": "booking_status",
                "data": status
            }, websocket)
            
        except Exception as e:
            logger.error(f"Error getting booking status: {e}")
            await self.manager.send_personal_json({
                "type": "error",
                "message": "Error retrieving booking status"
            }, websocket)
    
    async def _handle_weather_request(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle real-time weather requests."""
        
        location = message.get("location")
        
        if not location:
            await self.manager.send_personal_json({
                "type": "error", 
                "message": "Location required"
            }, websocket)
            return
        
        try:
            # Get weather data
            weather_data = await self.orchestrator.get_weather_data(location, None, None)
            
            await self.manager.send_personal_json({
                "type": "weather_data",
                "location": location,
                "data": weather_data,
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            await self.manager.send_personal_json({
                "type": "error",
                "message": "Error retrieving weather data"
            }, websocket)
    
    async def _handle_live_search(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle live search requests (flights, hotels, etc.)."""
        
        search_type = message.get("search_type")  # flights, hotels, etc.
        params = message.get("params", {})
        
        if not search_type:
            await self.manager.send_personal_json({
                "type": "error",
                "message": "Search type required"
            }, websocket)
            return
        
        try:
            # Send initial response
            await self.manager.send_personal_json({
                "type": "search_started",
                "search_type": search_type,
                "message": f"Searching for {search_type}..."
            }, websocket)
            
            # Perform search based on type
            if search_type == "flights":
                results = await self._search_flights_live(params)
            elif search_type == "hotels":
                results = await self._search_hotels_live(params)
            else:
                results = []
            
            await self.manager.send_personal_json({
                "type": "search_results",
                "search_type": search_type,
                "results": results,
                "count": len(results),
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
            
        except Exception as e:
            logger.error(f"Error handling live search: {e}")
            await self.manager.send_personal_json({
                "type": "error",
                "message": "Error performing search"
            }, websocket)
    
    async def _search_flights_live(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform live flight search."""
        # This would integrate with real flight search APIs
        # For now, return mock data
        await asyncio.sleep(1)  # Simulate API delay
        
        return [
            {
                "flight_id": "FL001",
                "airline": "Demo Airlines",
                "price": 299.99,
                "departure": "10:00 AM",
                "arrival": "2:30 PM"
            }
        ]
    
    async def _search_hotels_live(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform live hotel search."""
        # This would integrate with real hotel search APIs
        # For now, return mock data
        await asyncio.sleep(1)  # Simulate API delay
        
        return [
            {
                "hotel_id": "HT001",
                "name": "Demo Hotel",
                "price": 89.99,
                "rating": 4.2,
                "location": "City Center"
            }
        ]


# Global connection manager and handler
connection_manager = ConnectionManager()
websocket_handler = TravelWebSocketHandler(connection_manager)
