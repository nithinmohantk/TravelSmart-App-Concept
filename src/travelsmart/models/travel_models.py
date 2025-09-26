"""Data models for travel-related entities."""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TravelType(str, Enum):
    """Types of travel."""
    BUSINESS = "business"
    LEISURE = "leisure"
    ADVENTURE = "adventure"
    FAMILY = "family"
    ROMANTIC = "romantic"


class WeatherCondition(BaseModel):
    """Weather condition model."""
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    feels_like: float


class Location(BaseModel):
    """Location model."""
    city: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None


class TravelRequest(BaseModel):
    """Travel request from user."""
    destination: str
    departure_city: str
    start_date: date
    end_date: date
    budget: Optional[float] = None
    travel_type: TravelType = TravelType.LEISURE
    party_size: int = 1
    preferences: Optional[Dict[str, Any]] = None
    special_requirements: Optional[str] = None


class FlightOption(BaseModel):
    """Flight option model."""
    airline: str
    flight_number: str
    departure_time: datetime
    arrival_time: datetime
    duration: str
    price: float
    stops: int = 0
    aircraft_type: Optional[str] = None


class HotelOption(BaseModel):
    """Hotel option model."""
    name: str
    rating: float
    price_per_night: float
    location: Location
    amenities: List[str] = []
    description: Optional[str] = None
    images: List[str] = []


class Activity(BaseModel):
    """Activity/attraction model."""
    name: str
    description: str
    category: str
    location: Location
    rating: Optional[float] = None
    price: Optional[float] = None
    duration: Optional[str] = None
    opening_hours: Optional[str] = None


class TravelItinerary(BaseModel):
    """Complete travel itinerary."""
    destination: Location
    travel_dates: tuple[date, date]
    flights: List[FlightOption] = []
    hotels: List[HotelOption] = []
    activities: List[Activity] = []
    estimated_total_cost: Optional[float] = None
    weather_forecast: Optional[List[WeatherCondition]] = None
    local_insights: Optional[Dict[str, Any]] = None


class BookingRequest(BaseModel):
    """Booking request model."""
    user_id: str
    itinerary: TravelItinerary
    contact_info: Dict[str, str]
    payment_method: Optional[str] = None
    special_requests: Optional[str] = None


class BookingConfirmation(BaseModel):
    """Booking confirmation model."""
    booking_id: str
    status: str
    confirmation_number: str
    total_amount: float
    booking_details: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)