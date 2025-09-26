"""Tests for enhanced TravelSmart features."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date, datetime

from travelsmart.services.recommendation_engine import RecommendationEngine
from travelsmart.services.notification_service import NotificationService
from travelsmart.utils.helpers import validate_dates, generate_confirmation_number, format_currency
from travelsmart.utils.cache import CacheManager


class TestRecommendationEngine:
    """Test the recommendation engine."""
    
    @pytest.fixture
    def engine(self):
        return RecommendationEngine()
    
    @pytest.mark.asyncio
    async def test_personalized_recommendations(self, engine):
        """Test personalized recommendations generation."""
        user_preferences = {
            "activities": ["museums", "restaurants", "walking tours"],
            "accommodation": {"type": "hotel", "rating": "4+"},
            "budget": {"range": "medium", "currency": "USD"}
        }
        
        with patch.object(engine.gpt_service, 'answer_travel_question', return_value="Great recommendations") as mock_gpt:
            result = await engine.get_personalized_recommendations(user_preferences)
            
            assert result["recommendations"] == "Great recommendations"
            assert result["user_preferences"] == user_preferences
            assert "personalization_score" in result
            assert "generated_at" in result
            mock_gpt.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_similar_destinations(self, engine):
        """Test finding similar destinations."""
        liked_destination = "Paris"
        preferences = {"culture": "high", "food": "important"}
        
        with patch.object(engine.gpt_service, 'answer_travel_question', return_value="1. London\n2. Vienna") as mock_gpt:
            result = await engine.get_similar_destinations(liked_destination, preferences)
            
            assert isinstance(result, list)
            mock_gpt.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_seasonal_recommendations(self, engine):
        """Test seasonal recommendations."""
        month = 6  # June
        preferences = {"climate": "warm", "activities": ["beach", "hiking"]}
        
        with patch.object(engine.gpt_service, 'answer_travel_question', return_value="Great summer destinations") as mock_gpt:
            result = await engine.get_seasonal_recommendations(month, preferences)
            
            assert result["month"] == "June"
            assert result["recommendations"] == "Great summer destinations"
            assert result["preferences_considered"] == preferences
            mock_gpt.assert_called_once()
    
    def test_personalization_score_calculation(self, engine):
        """Test personalization score calculation."""
        # Test with minimal data
        score1 = engine._calculate_personalization_score({}, None)
        assert score1 == 0.0
        
        # Test with preferences
        preferences = {"activities": ["museums"], "budget": "medium"}
        score2 = engine._calculate_personalization_score(preferences, None)
        assert score2 > 0
        
        # Test with travel history
        travel_history = [{"destination": "Paris"}, {"destination": "London"}]
        score3 = engine._calculate_personalization_score(preferences, travel_history)
        assert score3 > score2


class TestNotificationService:
    """Test the notification service."""
    
    @pytest.fixture
    def service(self):
        return NotificationService()
    
    def test_generate_booking_email_html(self, service):
        """Test HTML email generation."""
        booking_details = {
            "confirmation_number": "TS123456",
            "destination": "Paris",
            "start_date": "2024-06-01",
            "end_date": "2024-06-07",
            "total_cost": 1500.00,
            "flights": [{"airline": "Air France", "flight_number": "AF123", "price": 600}],
            "hotels": [{"name": "Hotel Paris", "rating": 4.5, "price_per_night": 150}]
        }
        
        html = service._generate_booking_email_html(booking_details)
        
        assert "TravelSmart" in html
        assert "TS123456" in html
        assert "Paris" in html
        assert "$1500.00" in html
        assert "Air France" in html
        assert "Hotel Paris" in html
    
    def test_generate_booking_email_text(self, service):
        """Test text email generation."""
        booking_details = {
            "confirmation_number": "TS123456",
            "destination": "Paris",
            "total_cost": 1500.00
        }
        
        text = service._generate_booking_email_text(booking_details)
        
        assert "TravelSmart" in text
        assert "TS123456" in text
        assert "Paris" in text
        assert "$1500.00" in text


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_validate_dates(self):
        """Test date validation."""
        today = date.today()
        future_date = date(2024, 12, 25)
        past_date = date(2020, 1, 1)
        
        # Valid dates
        is_valid, msg = validate_dates(future_date, date(2024, 12, 31))
        assert is_valid is True
        assert msg is None
        
        # Past start date
        is_valid, msg = validate_dates(past_date, future_date)
        assert is_valid is False
        assert "past" in msg.lower()
        
        # End date before start date
        is_valid, msg = validate_dates(future_date, today)
        assert is_valid is False
        assert "after" in msg.lower()
    
    def test_generate_confirmation_number(self):
        """Test confirmation number generation."""
        conf_num1 = generate_confirmation_number()
        conf_num2 = generate_confirmation_number()
        
        assert conf_num1.startswith("TS")
        assert conf_num2.startswith("TS")
        assert len(conf_num1) == 10  # TS + 6 digits + 4 chars
        assert conf_num1 != conf_num2  # Should be unique
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(1234.56, "USD") == "$1,234.56"
        assert format_currency(1000.00, "EUR") == "€1,000.00"
        assert format_currency(999.99, "GBP") == "£999.99"
        assert format_currency(5000, "UNKNOWN") == "UNKNOWN5,000.00"


class TestCacheManager:
    """Test the cache manager."""
    
    @pytest.fixture
    def cache_manager(self):
        return CacheManager()
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, cache_manager):
        """Test basic cache operations."""
        key = "test_key"
        value = {"data": "test_value"}
        
        # Set cache
        await cache_manager.set(key, value, ttl_seconds=10)
        
        # Get cache
        cached_value = await cache_manager.get(key)
        assert cached_value == value
        
        # Get non-existent key
        missing_value = await cache_manager.get("missing_key")
        assert missing_value is None
    
    @pytest.mark.asyncio
    async def test_cache_expiry(self, cache_manager):
        """Test cache expiration."""
        key = "expiry_test"
        value = {"data": "expires_soon"}
        
        # Set cache with very short TTL
        await cache_manager.set(key, value, ttl_seconds=1)
        
        # Should be available immediately
        cached_value = await cache_manager.get(key)
        assert cached_value == value
        
        # Wait for expiration
        await asyncio.sleep(2)
        
        # Should be expired
        expired_value = await cache_manager.get(key)
        assert expired_value is None
    
    @pytest.mark.asyncio
    async def test_cache_delete_and_clear(self, cache_manager):
        """Test cache deletion and clearing."""
        # Set multiple keys
        await cache_manager.set("key1", "value1")
        await cache_manager.set("key2", "value2")
        
        # Delete one key
        await cache_manager.delete("key1")
        assert await cache_manager.get("key1") is None
        assert await cache_manager.get("key2") == "value2"
        
        # Clear all
        await cache_manager.clear()
        assert await cache_manager.get("key2") is None
    
    def test_cache_key_generation(self, cache_manager):
        """Test cache key generation methods."""
        weather_key = cache_manager.cache_key_for_weather("Paris", "2024-01-01", "2024-01-07")
        insights_key = cache_manager.cache_key_for_insights("Paris", "leisure")
        flights_key = cache_manager.cache_key_for_flights("NYC", "Paris", "2024-01-01")
        
        assert len(weather_key) == 32  # MD5 hash length
        assert len(insights_key) == 32
        assert len(flights_key) == 32
        
        # Same inputs should generate same key
        weather_key2 = cache_manager.cache_key_for_weather("Paris", "2024-01-01", "2024-01-07")
        assert weather_key == weather_key2


@pytest.mark.asyncio
async def test_integration_trip_planning():
    """Integration test for trip planning with all features."""
    from travelsmart.services.travel_orchestrator import TravelOrchestrator
    from travelsmart.models.travel_models import TravelRequest, TravelType
    
    orchestrator = TravelOrchestrator()
    
    travel_request = TravelRequest(
        destination="Paris",
        departure_city="New York",
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 7),
        budget=2000.0,
        travel_type=TravelType.LEISURE,
        party_size=2
    )
    
    # Mock all external calls
    with patch.object(orchestrator.gpt_service, 'generate_travel_plan', return_value="Mock travel plan") as mock_gpt, \
         patch.object(orchestrator, 'get_weather_data', return_value={"temp": 20}) as mock_weather, \
         patch.object(orchestrator, 'get_travel_insights', return_value={"insights": "great city"}) as mock_insights, \
         patch.object(orchestrator, 'search_flights', return_value=[{"flight": "AF001"}]) as mock_flights, \
         patch.object(orchestrator, 'search_hotels', return_value=[{"hotel": "Grand Hotel"}]) as mock_hotels:
        
        result = await orchestrator.plan_trip(travel_request)
        
        assert result["status"] == "success"
        assert result["travel_plan"] == "Mock travel plan"
        assert "weather_forecast" in result
        assert "local_insights" in result
        assert "flight_options" in result
        assert "hotel_options" in result
        
        # Verify all services were called
        mock_gpt.assert_called_once()
        mock_weather.assert_called_once()
        mock_insights.assert_called_once()
        mock_flights.assert_called_once()
        mock_hotels.assert_called_once()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
