"""Example usage of TravelSmart API."""

import asyncio
import httpx
from datetime import date, datetime
import json

# Example API usage
async def example_plan_trip():
    """Example of planning a trip using the API."""
    
    trip_request = {
        "destination": "Paris",
        "departure_city": "New York",
        "start_date": "2024-07-01",
        "end_date": "2024-07-07",
        "budget": 3000,
        "travel_type": "leisure",
        "party_size": 2,
        "preferences": {
            "accommodation_type": "hotel",
            "transportation": "flight",
            "activities": ["sightseeing", "museums", "dining"]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/plan-trip",
            json=trip_request,
            timeout=60.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Trip Planning Result:")
            print("=" * 50)
            print(f"Status: {result['status']}")
            print(f"\nTravel Plan:\n{result['travel_plan']}")
            
            if result.get('weather_forecast'):
                print(f"\nWeather: {result['weather_forecast']}")
            
            if result.get('flight_options'):
                print(f"\nFlights: {len(result['flight_options'])} options found")
                
            if result.get('hotel_options'):
                print(f"\nHotels: {len(result['hotel_options'])} options found")
        else:
            print(f"Error: {response.status_code} - {response.text}")


async def example_get_weather():
    """Example of getting weather for a destination."""
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/destinations/Tokyo/weather")
        
        if response.status_code == 200:
            result = response.json()
            print("\nWeather Forecast:")
            print("=" * 30)
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")


async def example_get_insights():
    """Example of getting travel insights."""
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/destinations/Rome/insights?travel_type=family")
        
        if response.status_code == 200:
            result = response.json()
            print("\nTravel Insights:")
            print("=" * 30)
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")


async def main():
    """Run all examples."""
    print("TravelSmart API Examples")
    print("=" * 50)
    
    print("\n1. Planning a trip to Paris...")
    await example_plan_trip()
    
    print("\n2. Getting weather for Tokyo...")
    await example_get_weather()
    
    print("\n3. Getting insights for Rome...")
    await example_get_insights()


if __name__ == "__main__":
    asyncio.run(main())
