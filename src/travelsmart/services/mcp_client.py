"""MCP Client for communicating with MCP servers."""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from loguru import logger


class MCPClient:
    """Client for communicating with MCP servers."""
    
    def __init__(self, server_name: str, host: str = "localhost", port: int = 3000):
        self.server_name = server_name
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        
        session = await self._get_session()
        
        payload = {
            "tool": tool_name,
            "parameters": parameters
        }
        
        try:
            async with session.post(
                f"{self.base_url}/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.debug(f"MCP {self.server_name} call successful: {tool_name}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"MCP {self.server_name} error: {response.status} - {error_text}")
                    raise Exception(f"MCP server error: {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling MCP {self.server_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling MCP {self.server_name}: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if the MCP server is healthy."""
        
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed for MCP {self.server_name}: {e}")
            return False
    
    async def close(self):
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()