"""Command line interface for TravelSmart."""

import asyncio
import click
from datetime import date
from typing import Optional

from .services.travel_orchestrator import TravelOrchestrator
from .models.travel_models import TravelRequest, TravelType


@click.group()
def main():
    """TravelSmart CLI - AI-powered travel planning."""
    pass


@main.command()
@click.option('--destination', required=True, help='Destination city/country')
@click.option('--departure', required=True, help='Departure city')
@click.option('--start-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]), help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, type=click.DateTime(formats=["%Y-%m-%d"]), help='End date (YYYY-MM-DD)')
@click.option('--budget', type=float, help='Budget in USD')
@click.option('--travel-type', type=click.Choice(['business', 'leisure', 'adventure', 'family', 'romantic']), default='leisure')
@click.option('--party-size', type=int, default=1, help='Number of travelers')
def plan(destination, departure, start_date, end_date, budget, travel_type, party_size):
    """Plan a trip using AI recommendations."""
    
    async def _plan():
        orchestrator = TravelOrchestrator()
        
        travel_request = TravelRequest(
            destination=destination,
            departure_city=departure,
            start_date=start_date.date(),
            end_date=end_date.date(),
            budget=budget,
            travel_type=TravelType(travel_type),
            party_size=party_size
        )
        
        click.echo(f"Planning trip to {destination}...")
        result = await orchestrator.plan_trip(travel_request)
        
        if result['status'] == 'success':
            click.echo("\n🎉 Trip Plan Generated!")
            click.echo("=" * 50)
            click.echo(result['travel_plan'])
            
            if result.get('weather_forecast'):
                click.echo("\n🌤️  Weather Forecast:")
                click.echo(str(result['weather_forecast']))
            
            if result.get('flight_options'):
                click.echo(f"\n✈️  Found {len(result['flight_options'])} flight options")
            
            if result.get('hotel_options'):
                click.echo(f"\n🏨 Found {len(result['hotel_options'])} hotel options")
        else:
            click.echo(f"❌ Error: {result.get('message', 'Unknown error')}")
    
    asyncio.run(_plan())


@main.command()
@click.option('--destination', required=True, help='Destination to get weather for')
def weather(destination):
    """Get weather forecast for a destination."""
    
    async def _weather():
        orchestrator = TravelOrchestrator()
        weather_data = await orchestrator.get_weather_data(destination, None, None)
        
        click.echo(f"\n🌤️  Weather for {destination}:")
        click.echo("=" * 30)
        click.echo(str(weather_data))
    
    asyncio.run(_weather())


@main.command()
@click.option('--destination', required=True, help='Destination to get insights for')
def insights(destination):
    """Get travel insights for a destination."""
    
    async def _insights():
        orchestrator = TravelOrchestrator()
        insights_data = await orchestrator.get_travel_insights(destination, "leisure", 1)
        
        click.echo(f"\n🌍 Travel Insights for {destination}:")
        click.echo("=" * 40)
        click.echo(str(insights_data))
    
    asyncio.run(_insights())


if __name__ == '__main__':
    main()
