"""Configuration settings for TravelSmart application."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # Application Configuration
    app_host: str = "localhost"
    app_port: int = 8000
    debug: bool = True
    log_level: str = "INFO"
    
    # Weather API Configuration
    weather_api_key: Optional[str] = None
    weather_base_url: str = "https://api.openweathermap.org/data/2.5"
    
    # Google Maps API Configuration
    google_maps_api_key: Optional[str] = None
    
    # MCP Server Configuration
    mcp_weather_port: int = 3001
    mcp_insights_port: int = 3002
    mcp_booking_port: int = 3003
    
    # Database Configuration
    database_url: str = "sqlite:///./travelsmart.db"
    
    # External APIs
    amadeus_api_key: Optional[str] = None
    amadeus_api_secret: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()