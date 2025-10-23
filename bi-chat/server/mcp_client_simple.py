#!/usr/bin/env python3
"""
Simplified MCP Client using direct subprocess communication
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import subprocess

logger = logging.getLogger(__name__)


class SimpleMCPClient:
    """Simplified MCP client using subprocess for stdio communication"""

    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.tools_cache: Dict[str, List[Dict[str, Any]]] = {}

    async def connect_server(self, server_name: str, server_path: Path):
        """Connect to an MCP server using subprocess"""
        try:
            # Start the MCP server as a subprocess
            process = subprocess.Popen(
                ["python3", str(server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            self.processes[server_name] = process

            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "bi-chat-client",
                        "version": "1.0.0"
                    }
                }
            }

            # Write to stdin
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()

            # Read response (with timeout)
            try:
                response_line = await asyncio.wait_for(
                    asyncio.to_thread(process.stdout.readline),
                    timeout=5.0
                )
                response = json.loads(response_line)
                logger.info(f"Connected to {server_name}: {response}")

                # List tools
                list_tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }

                process.stdin.write(json.dumps(list_tools_request) + "\n")
                process.stdin.flush()

                tools_response_line = await asyncio.wait_for(
                    asyncio.to_thread(process.stdout.readline),
                    timeout=5.0
                )
                tools_response = json.loads(tools_response_line)

                if "result" in tools_response:
                    self.tools_cache[server_name] = tools_response["result"].get("tools", [])
                    logger.info(f"Loaded {len(self.tools_cache[server_name])} tools from {server_name}")

                return True

            except asyncio.TimeoutError:
                logger.error(f"Timeout connecting to {server_name}")
                process.kill()
                return False

        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {e}")
            return False

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call a tool on an MCP server"""
        if server_name not in self.processes:
            raise ValueError(f"Server {server_name} not connected")

        process = self.processes[server_name]

        try:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()

            response_line = await asyncio.wait_for(
                asyncio.to_thread(process.stdout.readline),
                timeout=10.0
            )
            response = json.loads(response_line)

            if "result" in response:
                return response["result"].get("content", [{}])[0].get("text", "")
            else:
                logger.error(f"Error calling {tool_name}: {response.get('error')}")
                return None

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
        for server_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=3)
                logger.info(f"Disconnected from {server_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {server_name}: {e}")
                try:
                    process.kill()
                except:
                    pass


class SimpleMCPClientManager:
    """Singleton manager for simple MCP client"""

    _instance: Optional['SimpleMCPClientManager'] = None
    _client: Optional[SimpleMCPClient] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self, base_path: Path):
        """Initialize MCP client and connect to servers"""
        if self._initialized:
            return

        self._client = SimpleMCPClient()

        # Define server paths
        servers = {
            "bi-vault": base_path / "mcp-servers" / "bi-vault" / "server.py",
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
        logger.info(f"Simple MCP Client Manager initialized - {connected_count}/{len(servers)} servers connected")

    def get_client(self) -> SimpleMCPClient:
        """Get the MCP client instance"""
        if not self._initialized or not self._client:
            raise RuntimeError("SimpleMCPClientManager not initialized. Call initialize() first.")
        return self._client

    async def shutdown(self):
        """Shutdown MCP client"""
        if self._client:
            await self._client.disconnect_all()
            self._initialized = False
