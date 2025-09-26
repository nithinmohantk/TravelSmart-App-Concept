"""Server runner for TravelSmart."""

import asyncio
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from .api.main import run as run_api
from .mcp_servers.weather_server import main as run_weather_server
from .mcp_servers.travel_insights_server import main as run_insights_server
from .mcp_servers.booking_server import main as run_booking_server


def run_server_in_background(server_func, server_name):
    """Run a server in background."""
    try:
        logger.info(f"Starting {server_name}...")
        server_func()
    except Exception as e:
        logger.error(f"Error running {server_name}: {e}")


def run():
    """Run all TravelSmart servers."""
    logger.info("Starting TravelSmart servers...")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Start MCP servers
        executor.submit(run_server_in_background, run_weather_server, "Weather MCP Server")
        executor.submit(run_server_in_background, run_insights_server, "Insights MCP Server") 
        executor.submit(run_server_in_background, run_booking_server, "Booking MCP Server")
        
        # Start main API server (blocking)
        logger.info("Starting main API server...")
        run_api()


if __name__ == "__main__":
    run()
