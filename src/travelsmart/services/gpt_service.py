"""OpenAI GPT service for travel recommendations and planning."""

import asyncio
from typing import Dict, List, Any, Optional
import json
from openai import AsyncOpenAI
from loguru import logger

from ..config import settings
from ..models.travel_models import TravelRequest, TravelItinerary, Location


class GPTService:
    """Service for OpenAI GPT interactions."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def generate_travel_plan(
        self, 
        travel_request: TravelRequest,
        weather_data: Optional[Dict] = None,
        local_insights: Optional[Dict] = None
    ) -> str:
        """Generate a comprehensive travel plan using GPT."""
        
        system_prompt = """You are an expert travel advisor with deep knowledge of global destinations, 
        weather patterns, local customs, and travel logistics. Create comprehensive, personalized travel 
        recommendations based on user preferences, weather conditions, and local insights."""
        
        user_prompt = f"""
        Create a detailed travel plan for:
        - Destination: {travel_request.destination}
        - Departure from: {travel_request.departure_city}
        - Travel dates: {travel_request.start_date} to {travel_request.end_date}
        - Budget: ${travel_request.budget if travel_request.budget else 'Not specified'}
        - Travel type: {travel_request.travel_type}
        - Party size: {travel_request.party_size}
        - Preferences: {travel_request.preferences or 'None specified'}
        - Special requirements: {travel_request.special_requirements or 'None'}
        
        Weather information: {weather_data if weather_data else 'Not available'}
        Local insights: {local_insights if local_insights else 'Not available'}
        
        Please provide:
        1. Best time to visit and weather considerations
        2. Recommended activities and attractions
        3. Suggested accommodation areas
        4. Local transportation options
        5. Cultural tips and local customs
        6. Food recommendations
        7. Packing suggestions based on weather
        8. Budget breakdown estimate
        9. Safety considerations
        10. Hidden gems and local favorites
        
        Format the response as a comprehensive travel guide.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating travel plan: {e}")
            raise
    
    async def optimize_itinerary(
        self,
        itinerary: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> str:
        """Optimize an existing itinerary based on constraints."""
        
        system_prompt = """You are a travel optimization expert. Analyze and improve travel itineraries 
        for better efficiency, cost-effectiveness, and enjoyment while considering user constraints."""
        
        user_prompt = f"""
        Optimize this travel itinerary:
        {json.dumps(itinerary, indent=2, default=str)}
        
        Constraints: {constraints or 'None specified'}
        
        Please provide:
        1. Suggested improvements for time management
        2. Cost optimization opportunities
        3. Better routing between activities
        4. Alternative options for activities/accommodations
        5. Tips for avoiding crowds and long waits
        6. Seasonal considerations and timing advice
        
        Format as specific, actionable recommendations.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error optimizing itinerary: {e}")
            raise
    
    async def answer_travel_question(self, question: str, context: Optional[str] = None) -> str:
        """Answer specific travel-related questions."""
        
        system_prompt = """You are a knowledgeable travel assistant. Provide accurate, helpful, 
        and practical answers to travel-related questions."""
        
        user_prompt = f"""
        Question: {question}
        Context: {context or 'No additional context'}
        
        Please provide a comprehensive, accurate answer with practical advice and specific recommendations where applicable.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error answering travel question: {e}")
            raise
    
    async def generate_packing_list(
        self, 
        destination: str, 
        travel_dates: tuple, 
        weather_forecast: Optional[Dict] = None,
        activities: Optional[List[str]] = None
    ) -> str:
        """Generate a personalized packing list."""
        
        system_prompt = """You are a travel packing expert. Create comprehensive, practical packing 
        lists based on destination, weather, and planned activities."""
        
        user_prompt = f"""
        Generate a packing list for:
        - Destination: {destination}
        - Travel dates: {travel_dates[0]} to {travel_dates[1]}
        - Weather forecast: {weather_forecast or 'Not available'}
        - Planned activities: {activities or 'General tourism'}
        
        Organize the list by categories:
        1. Clothing (by weather and activities)
        2. Toiletries and personal care
        3. Electronics and gadgets
        4. Documents and money
        5. Health and safety items
        6. Activity-specific gear
        7. Miscellaneous essentials
        
        Include quantity suggestions and priority levels (essential/recommended/optional).
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating packing list: {e}")
            raise