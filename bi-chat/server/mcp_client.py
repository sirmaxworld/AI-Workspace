#!/usr/bin/env python3
"""
MCP Client for bi-chat
Handles connections to MCP servers and tool calling
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for connecting to and calling MCP servers"""

    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.tools_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.stdio_contexts: Dict[str, Any] = {}  # Store stdio context managers

    async def connect_server(self, server_name: str, server_path: Path):
        """Connect to an MCP server"""
        try:
            server_params = StdioServerParameters(
                command="python3",
                args=[str(server_path)],
                env=None
            )

            # Create and store the context manager
            stdio_ctx = stdio_client(server_params)
            self.stdio_contexts[server_name] = stdio_ctx

            # Enter the context
            read_stream, write_stream = await stdio_ctx.__aenter__()

            # Initialize session
            session = ClientSession(read_stream, write_stream)
            await session.initialize()

            self.sessions[server_name] = session

            # Cache available tools
            tools_result = await session.list_tools()
            self.tools_cache[server_name] = tools_result.tools

            logger.info(f"Connected to {server_name} - {len(tools_result.tools)} tools available")

        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {e}")
            # Clean up the context if it was stored
            if server_name in self.stdio_contexts:
                try:
                    await self.stdio_contexts[server_name].__aexit__(None, None, None)
                except:
                    pass
                del self.stdio_contexts[server_name]
            return False

        return True

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call a tool on an MCP server"""
        if server_name not in self.sessions:
            raise ValueError(f"Server {server_name} not connected")

        session = self.sessions[server_name]

        try:
            result = await session.call_tool(tool_name, arguments)

            # Parse result content
            if hasattr(result, 'content') and result.content:
                # Handle different content types
                if isinstance(result.content, list) and len(result.content) > 0:
                    first_content = result.content[0]
                    if hasattr(first_content, 'text'):
                        return first_content.text
                    return str(first_content)
                return str(result.content)

            return str(result)

        except Exception as e:
            logger.error(f"Error calling {tool_name} on {server_name}: {e}")
            raise

    def get_available_tools(self, server_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get available tools from all servers or a specific server"""
        if server_name:
            return {server_name: self.tools_cache.get(server_name, [])}
        return self.tools_cache

    async def disconnect_all(self):
        """Disconnect from all servers"""
        for server_name, session in self.sessions.items():
            try:
                logger.info(f"Disconnecting from {server_name}")
                # Properly exit the stdio context
                if server_name in self.stdio_contexts:
                    await self.stdio_contexts[server_name].__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error disconnecting from {server_name}: {e}")

        # Clear all stored contexts
        self.stdio_contexts.clear()
        self.sessions.clear()
        self.tools_cache.clear()


class MCPClientManager:
    """Singleton manager for MCP client"""

    _instance: Optional['MCPClientManager'] = None
    _client: Optional[MCPClient] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self, base_path: Path):
        """Initialize MCP client and connect to servers"""
        if self._initialized:
            return

        self._client = MCPClient()

        # Define server paths (only connect to bi-vault for now)
        servers = {
            "bi-vault": base_path / "mcp-servers" / "bi-vault" / "server.py",
            # Temporarily disable other servers to avoid issues
            # "railway-postgres": base_path / "mcp-servers" / "railway-postgres" / "server.py",
            # "coding-brain": base_path / "mcp-servers" / "coding-brain" / "server.py"
        }

        # Connect to each server
        connected_count = 0
        for server_name, server_path in servers.items():
            if server_path.exists():
                logger.info(f"Attempting to connect to {server_name}...")
                success = await self._client.connect_server(server_name, server_path)
                if success:
                    connected_count += 1
            else:
                logger.warning(f"Server not found: {server_path}")

        self._initialized = True
        logger.info(f"MCP Client Manager initialized - {connected_count}/{len(servers)} servers connected")

    def get_client(self) -> MCPClient:
        """Get the MCP client instance"""
        if not self._initialized or not self._client:
            raise RuntimeError("MCPClientManager not initialized. Call initialize() first.")
        return self._client

    async def shutdown(self):
        """Shutdown MCP client"""
        if self._client:
            await self._client.disconnect_all()
            self._initialized = False
