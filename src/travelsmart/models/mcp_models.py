"""Models specific to MCP server interactions."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class MCPToolCall(BaseModel):
    """MCP tool call request model."""
    tool: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    """MCP server response model."""
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class WeatherRequest(BaseModel):
    """Weather API request model."""
    location: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class WeatherCondition(BaseModel):
    """Weather condition details."""
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    description: str
    wind_speed: float
    wind_direction: int
    visibility: float


class WeatherForecast(BaseModel):
    """Weather forecast model."""
    location: str
    current: WeatherCondition
    forecast: List[Dict[str, Any]] = []
    alerts: List[str] = []


class InsightsRequest(BaseModel):
    """Travel insights request model."""
    destination: str
    travel_type: str = "leisure"
    party_size: int = 1
    interests: List[str] = []


class Attraction(BaseModel):
    """Tourist attraction model."""
    name: str
    category: str
    rating: float
    price_range: str
    description: str
    location: Dict[str, float]
    opening_hours: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    duration: Optional[str] = None
    booking_required: bool = False


class Restaurant(BaseModel):
    """Restaurant recommendation model."""
    name: str
    cuisine: str
    rating: float
    price_range: str
    address: str
    specialties: List[str] = []
    atmosphere: str
    reservations: bool = False
    dietary_options: List[str] = []


class LocalTip(BaseModel):
    """Local travel tip model."""
    category: str  # transportation, etiquette, safety, etc.
    tip: str
    importance: str = "medium"  # low, medium, high
    local_context: Optional[str] = None


class DestinationInsights(BaseModel):
    """Comprehensive destination insights."""
    destination: str
    overview: str
    best_time_to_visit: str
    currency: str
    language: str
    timezone: str
    safety_rating: float
    cost_level: str
    attractions: List[Attraction] = []
    restaurants: List[Restaurant] = []
    local_tips: List[LocalTip] = []
    transportation: List[str] = []
    cultural_notes: List[str] = []


class BookingSearchRequest(BaseModel):
    """Booking search request model."""
    origin: Optional[str] = None
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    budget: Optional[float] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)


class FlightDetails(BaseModel):
    """Detailed flight information."""
    flight_id: str
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    aircraft: str
    price: float
    stops: int
    baggage_allowance: Optional[str] = None
    seat_availability: Optional[Dict[str, int]] = None
    cancellation_policy: Optional[str] = None


class HotelDetails(BaseModel):
    """Detailed hotel information."""
    hotel_id: str
    name: str
    rating: float
    price_per_night: float
    location: Dict[str, Union[str, float]]
    room_type: str
    amenities: List[str] = []
    cancellation_policy: str
    breakfast_included: bool = False
    wifi_included: bool = True
    parking_available: bool = False
    pet_friendly: bool = False
    photos: List[str] = []


class BookingDetails(BaseModel):
    """Complete booking details."""
    booking_id: str
    status: str
    confirmation_number: str
    user_info: Dict[str, str]
    flights: List[FlightDetails] = []
    hotels: List[HotelDetails] = []
    total_cost: float
    payment_status: str
    booking_date: datetime
    travel_dates: Dict[str, str]
    special_requests: Optional[str] = None