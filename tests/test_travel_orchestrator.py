"""Tests for travel orchestrator."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import date

from travelsmart.services.travel_orchestrator import TravelOrchestrator
from travelsmart.models.travel_models import TravelRequest, TravelType


@pytest.fixture
def travel_request():
    """Sample travel request for testing."""
    return TravelRequest(
        destination="Paris",
        departure_city="New York",
        start_date=date(2024, 7, 1),
        end_date=date(2024, 7, 7),
        budget=2000.0,
        travel_type=TravelType.LEISURE,
        party_size=2
    )


@pytest.fixture
def orchestrator():
    """Travel orchestrator instance."""
    return TravelOrchestrator()


@pytest.mark.asyncio
async def test_plan_trip_success(orchestrator, travel_request):
    """Test successful trip planning."""
    
    # Mock the GPT service and MCP clients
    with patch.object(orchestrator.gpt_service, 'generate_travel_plan', return_value="Great travel plan") as mock_gpt, \
         patch.object(orchestrator, 'get_weather_data', return_value={"temp": 20}) as mock_weather, \
         patch.object(orchestrator, 'get_travel_insights', return_value={"insights": "great city"}) as mock_insights, \
         patch.object(orchestrator, 'search_flights', return_value=[{"flight": "AF001"}]) as mock_flights, \
         patch.object(orchestrator, 'search_hotels', return_value=[{"hotel": "Grand Hotel"}]) as mock_hotels:
        
        result = await orchestrator.plan_trip(travel_request)
        
        assert result["status"] == "success"
        assert result["travel_plan"] == "Great travel plan"
        assert "weather_forecast" in result
        assert "local_insights" in result
        assert "flight_options" in result
        assert "hotel_options" in result
        
        mock_gpt.assert_called_once()
        mock_weather.assert_called_once()
        mock_insights.assert_called_once()


@pytest.mark.asyncio
async def test_plan_trip_with_error(orchestrator, travel_request):
    """Test trip planning with error."""
    
    # Mock GPT service to raise an exception
    with patch.object(orchestrator.gpt_service, 'generate_travel_plan', side_effect=Exception("API Error")):
        
        result = await orchestrator.plan_trip(travel_request)
        
        assert result["status"] == "error"
        assert "API Error" in result["message"]


@pytest.mark.asyncio
async def test_get_weather_data_success(orchestrator):
    """Test successful weather data retrieval."""
    
    mock_weather_data = {
        "location": "Paris",
        "forecast": [{"date": "2024-07-01", "temp": 22}]
    }
    
    with patch.object(orchestrator.weather_client, 'call_tool', return_value=mock_weather_data):
        result = await orchestrator.get_weather_data("Paris", date(2024, 7, 1), date(2024, 7, 7))
        
        assert result == mock_weather_data


@pytest.mark.asyncio 
async def test_get_travel_insights_success(orchestrator):
    """Test successful travel insights retrieval."""
    
    mock_insights = {
        "destination": "Paris",
        "insights": {"overview": "City of Light"}
    }
    
    with patch.object(orchestrator.insights_client, 'call_tool', return_value=mock_insights):
        result = await orchestrator.get_travel_insights("Paris", "leisure", 2)
        
        assert result == mock_insights


@pytest.mark.asyncio
async def test_search_flights_success(orchestrator, travel_request):
    """Test successful flight search."""
    
    mock_flights = [
        {"flight_id": "AF001", "price": 650},
        {"flight_id": "DL123", "price": 580}
    ]
    
    with patch.object(orchestrator.booking_client, 'call_tool', return_value=mock_flights):
        result = await orchestrator.search_flights(travel_request)
        
        assert result == mock_flights
        assert len(result) == 2


@pytest.mark.asyncio
async def test_search_hotels_success(orchestrator, travel_request):
    """Test successful hotel search."""
    
    mock_hotels = [
        {"hotel_id": "HT001", "price_per_night": 180},
        {"hotel_id": "HT002", "price_per_night": 250}
    ]
    
    with patch.object(orchestrator.booking_client, 'call_tool', return_value=mock_hotels):
        result = await orchestrator.search_hotels(travel_request)
        
        assert result == mock_hotels
        assert len(result) == 2


@pytest.mark.asyncio
async def test_book_trip_success(orchestrator):
    """Test successful trip booking."""
    
    booking_request = {
        "user_id": "user123",
        "flights": [{"flight_id": "AF001"}],
        "hotels": [{"hotel_id": "HT001"}]
    }
    
    mock_booking = {
        "success": True,
        "booking_id": "booking123",
        "status": "confirmed"
    }
    
    with patch.object(orchestrator.booking_client, 'call_tool', return_value=mock_booking):
        result = await orchestrator.book_trip(booking_request)
        
        assert result == mock_booking
        assert result["success"] is True
