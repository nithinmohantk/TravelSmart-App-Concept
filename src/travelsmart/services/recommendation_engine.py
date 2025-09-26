"""AI-powered recommendation engine for personalized travel suggestions."""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
import json
from loguru import logger

from .gpt_service import GPTService
from ..models.travel_models import TravelRequest, TravelType
from ..utils.cache import cached_result


class RecommendationEngine:
    """AI-powered travel recommendation engine."""
    
    def __init__(self):
        self.gpt_service = GPTService()
    
    @cached_result(ttl_seconds=3600)  # Cache for 1 hour
    async def get_personalized_recommendations(
        self, 
        user_preferences: Dict[str, Any],
        travel_history: List[Dict[str, Any]] = None,
        budget_range: Tuple[float, float] = None
    ) -> Dict[str, Any]:
        """Generate personalized travel recommendations based on user data."""
        
        system_prompt = """You are an expert travel recommendation AI that analyzes user preferences, 
        travel history, and current trends to suggest personalized travel destinations and experiences. 
        Provide specific, actionable recommendations with reasoning."""
        
        user_prompt = f"""
        Generate personalized travel recommendations for a user with the following profile:
        
        Preferences: {json.dumps(user_preferences, indent=2)}
        Travel History: {json.dumps(travel_history or [], indent=2)}
        Budget Range: ${budget_range[0] if budget_range else 'No limit'} - ${budget_range[1] if budget_range else 'No limit'}
        
        Please provide:
        1. Top 5 destination recommendations with specific reasons
        2. Best travel times for each destination
        3. Recommended activities based on interests
        4. Budget breakdown for each destination
        5. Travel tips specific to their preferences
        6. Alternative options if primary choices are unavailable
        
        Format as a comprehensive recommendation report.
        """
        
        try:
            recommendations = await self.gpt_service.answer_travel_question(user_prompt, "personalized recommendations")
            
            return {
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat(),
                "user_preferences": user_preferences,
                "personalization_score": self._calculate_personalization_score(user_preferences, travel_history)
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {e}")
            raise
    
    async def get_similar_destinations(self, liked_destination: str, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find destinations similar to ones the user liked."""
        
        system_prompt = """You are a travel similarity expert. Find destinations that share similar 
        characteristics, vibes, and experiences to the given destination, considering user preferences."""
        
        user_prompt = f"""
        Find destinations similar to {liked_destination} that would appeal to someone with these preferences:
        {json.dumps(preferences, indent=2)}
        
        Consider similarities in:
        - Culture and atmosphere
        - Activities and attractions
        - Climate and geography
        - Cost and accessibility
        - Food and local experiences
        
        Provide 5-7 similar destinations with:
        - Name and country
        - Similarity score (1-10)
        - Key similarities
        - Unique differentiators
        - Best time to visit
        - Approximate budget level
        """
        
        try:
            response = await self.gpt_service.answer_travel_question(user_prompt, f"similar destinations to {liked_destination}")
            
            # Parse the response into structured data
            return self._parse_similar_destinations_response(response)
            
        except Exception as e:
            logger.error(f"Error finding similar destinations: {e}")
            return []
    
    async def get_seasonal_recommendations(self, month: int, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Get destination recommendations for a specific month."""
        
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        month_name = months[month - 1] if 1 <= month <= 12 else "Unknown"
        
        system_prompt = """You are a seasonal travel expert. Recommend destinations that are 
        ideal to visit during specific months, considering weather, events, crowds, and pricing."""
        
        user_prompt = f"""
        Recommend the best travel destinations for {month_name} considering:
        
        User Preferences: {json.dumps(preferences, indent=2)}
        
        For each recommendation, include:
        - Destination name and region
        - Why it's perfect for {month_name}
        - Weather conditions
        - Special events or seasons
        - Crowd levels and pricing
        - Recommended activities
        - What to pack
        
        Provide 5-8 destinations with variety in:
        - Geographic regions
        - Climate types
        - Activity types
        - Budget levels
        """
        
        try:
            recommendations = await self.gpt_service.answer_travel_question(user_prompt, f"seasonal travel for {month_name}")
            
            return {
                "month": month_name,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat(),
                "preferences_considered": preferences
            }
            
        except Exception as e:
            logger.error(f"Error generating seasonal recommendations: {e}")
            raise
    
    async def get_budget_optimized_suggestions(
        self, 
        destinations: List[str], 
        budget: float,
        travel_dates: Tuple[date, date],
        party_size: int = 1
    ) -> Dict[str, Any]:
        """Optimize travel suggestions based on budget constraints."""
        
        system_prompt = """You are a budget travel optimization expert. Analyze destinations 
        and provide cost-effective recommendations while maximizing travel experience value."""
        
        start_date, end_date = travel_dates
        duration = (end_date - start_date).days
        
        user_prompt = f"""
        Optimize travel recommendations for:
        
        Destinations being considered: {', '.join(destinations)}
        Total budget: ${budget}
        Travel duration: {duration} days
        Party size: {party_size}
        Travel dates: {start_date} to {end_date}
        
        For each destination, provide:
        - Estimated total cost breakdown
        - Budget optimization strategies
        - Best value accommodations
        - Free/low-cost activities
        - Money-saving tips
        - Value rating (1-10)
        
        Rank destinations by overall value considering:
        - Cost vs experience quality
        - Seasonal pricing
        - Hidden costs to avoid
        - Budget stretch opportunities
        """
        
        try:
            optimization = await self.gpt_service.answer_travel_question(user_prompt, "budget optimization")
            
            return {
                "budget_analysis": optimization,
                "total_budget": budget,
                "daily_budget": budget / duration if duration > 0 else budget,
                "per_person_budget": budget / party_size if party_size > 0 else budget,
                "destinations_analyzed": destinations,
                "optimization_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating budget optimized suggestions: {e}")
            raise
    
    async def get_activity_recommendations(
        self, 
        destination: str, 
        interests: List[str],
        travel_style: str = "balanced",
        duration_days: int = 7
    ) -> Dict[str, Any]:
        """Get activity recommendations based on interests and travel style."""
        
        system_prompt = """You are an activity curation expert. Design personalized activity 
        recommendations that match traveler interests, style, and time constraints."""
        
        user_prompt = f"""
        Create activity recommendations for:
        
        Destination: {destination}
        Interests: {', '.join(interests)}
        Travel style: {travel_style}
        Trip duration: {duration_days} days
        
        Provide a day-by-day activity plan including:
        - Must-do experiences
        - Hidden gems
        - Cultural activities
        - Outdoor adventures
        - Relaxation options
        - Local experiences
        
        For each activity include:
        - Activity name and type
        - Duration and best time
        - Cost estimate
        - Booking requirements
        - Why it matches their interests
        - Nearby activities to combine
        
        Balance the itinerary between:
        - Popular attractions and local experiences
        - Active and relaxing activities
        - Indoor and outdoor options
        - Different price points
        """
        
        try:
            activities = await self.gpt_service.answer_travel_question(user_prompt, f"activities for {destination}")
            
            return {
                "destination": destination,
                "activity_plan": activities,
                "interests_matched": interests,
                "travel_style": travel_style,
                "duration": duration_days,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating activity recommendations: {e}")
            raise
    
    def _calculate_personalization_score(
        self, 
        preferences: Dict[str, Any], 
        travel_history: Optional[List[Dict[str, Any]]]
    ) -> float:
        """Calculate how well recommendations can be personalized."""
        
        score = 0.0
        
        # Base score for having preferences
        if preferences:
            score += 30.0
            
            # Bonus for detailed preferences
            if len(preferences) > 5:
                score += 20.0
            
            # Bonus for specific interest categories
            if "activities" in preferences and preferences["activities"]:
                score += 15.0
            
            if "accommodation" in preferences:
                score += 10.0
            
            if "budget" in preferences:
                score += 10.0
        
        # Score for travel history
        if travel_history:
            score += 15.0
            
            # Bonus for extensive history
            if len(travel_history) > 3:
                score += 10.0
        
        return min(score, 100.0)  # Cap at 100
    
    def _parse_similar_destinations_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse GPT response for similar destinations into structured data."""
        
        # This is a simplified parser - in production, you'd want more robust parsing
        destinations = []
        
        # Split response by destinations (this is a basic implementation)
        lines = response.split('\n')
        current_dest = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for destination names (basic pattern matching)
            if any(keyword in line.lower() for keyword in ['destination:', 'city:', 'country:']):
                if current_dest:
                    destinations.append(current_dest)
                current_dest = {"name": line, "details": []}
            elif current_dest:
                current_dest["details"].append(line)
        
        if current_dest:
            destinations.append(current_dest)
        
        return destinations


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
