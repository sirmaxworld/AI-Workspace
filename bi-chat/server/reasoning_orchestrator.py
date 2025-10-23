#!/usr/bin/env python3
"""
Reasoning Orchestrator
Coordinates AI model calls with MCP tool usage
"""

import json
import logging
from typing import Any, Dict, List, Optional, AsyncIterator
from dataclasses import dataclass

import httpx

from mcp_client import MCPClient
from prompts.reasoning_prompts import (
    get_system_prompt,
    get_builder_context_prompt,
    format_tool_results_for_context
)

logger = logging.getLogger(__name__)


@dataclass
class ReasoningConfig:
    model: str
    thinking_mode: str
    temperature: float = 0.7
    max_tokens: int = 8000


class ReasoningOrchestrator:
    """Orchestrates AI reasoning with MCP tool access"""

    def __init__(self, openrouter_api_key: str, mcp_client: MCPClient):
        self.api_key = openrouter_api_key
        self.mcp_client = mcp_client
        self.base_url = "https://openrouter.ai/api/v1"

        # Model mappings
        self.model_map = {
            "gpt-4-turbo": "openai/gpt-4-turbo",
            "gpt-4": "openai/gpt-4",
            "o1-preview": "openai/o1-preview",
            "o1-mini": "openai/o1-mini",
            "claude-sonnet-4.5": "anthropic/claude-3.5-sonnet",
            "claude-sonnet-3.5": "anthropic/claude-3.5-sonnet",
            "claude-opus": "anthropic/claude-opus-4",
            "gemini-pro": "google/gemini-pro-1.5",
            "gemini-flash": "google/gemini-flash-1.5",
            "deepseek": "deepseek/deepseek-chat"
        }

    async def reason(
        self,
        query: str,
        config: ReasoningConfig,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterator[str]:
        """
        Main reasoning method - coordinates AI model with MCP tools
        Streams response back
        """

        # Build system prompt
        system_prompt = get_system_prompt(config.thinking_mode)

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current query
        messages.append({"role": "user", "content": query})

        # Get model identifier
        model_id = self.model_map.get(config.model, config.model)

        # Always use single-pass reasoning - let the LLM handle complexity naturally
        async for chunk in self._single_pass_reasoning(messages, model_id, config):
            yield chunk

    async def _single_pass_reasoning(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        config: ReasoningConfig
    ) -> AsyncIterator[str]:
        """Single-pass reasoning with streaming"""

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_id,
                        "messages": messages,
                        "temperature": config.temperature,
                        "max_tokens": config.max_tokens,
                        "stream": True
                    }
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break

                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue

            except Exception as e:
                logger.error(f"Error in single-pass reasoning: {e}")
                yield f"\n\n[Error: {str(e)}]"

    async def _multi_pass_reasoning(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        config: ReasoningConfig
    ) -> AsyncIterator[str]:
        """
        Multi-pass reasoning:
        1. First pass: Plan what MCP tools to call
        2. Execute MCP calls
        3. Second pass: Reason with MCP results
        """

        # Pass 1: Planning phase (silent - no verbose output)
        planning_messages = messages.copy()
        planning_messages.append({
            "role": "system",
            "content": """Before answering, first think about:
1. What specific data do you need from the MCP tools?
2. Which MCP tools should you call?
3. What arguments should you pass?

Format your plan as:
**Data Needed:**
- ...

**MCP Tool Calls:**
1. Tool: <tool_name>, Server: <server>, Args: {...}
2. ...

Then proceed with the analysis."""
        })

        # Get plan from model (non-streaming for parsing)
        plan_response = await self._get_completion(planning_messages, model_id, config)

        # Parse tool calls from plan (simplified - in production, use function calling)
        tool_calls = self._parse_tool_calls_from_plan(plan_response)

        if tool_calls and self.mcp_client:
            # Execute MCP tool calls silently
            tool_results = {}
            for i, tool_call in enumerate(tool_calls, 1):
                try:
                    result = await self.mcp_client.call_tool(
                        tool_call["server"],
                        tool_call["tool"],
                        tool_call["args"]
                    )
                    tool_results[f"{tool_call['server']}.{tool_call['tool']}"] = result
                except Exception as e:
                    logger.error(f"Error calling {tool_call}: {e}")

            # Pass 2: Reasoning with data
            reasoning_messages = messages.copy()
            reasoning_messages.append({
                "role": "system",
                "content": f"""Here is the data retrieved from MCP tools:

{format_tool_results_for_context(tool_results)}

Now provide your comprehensive analysis using this data."""
            })

            async for chunk in self._single_pass_reasoning(reasoning_messages, model_id, config):
                yield chunk
        else:
            # No tool calls needed, proceed with direct reasoning
            async for chunk in self._single_pass_reasoning(messages, model_id, config):
                yield chunk

    def _parse_tool_calls_from_plan(self, plan_text: str) -> List[Dict[str, Any]]:
        """Parse MCP tool calls from planning text"""
        # Simplified parsing - in production, use structured function calling
        tool_calls = []

        # Look for common patterns in the plan
        patterns = {
            "trends": {"server": "bi-vault", "tool": "search_trends", "args": {"query": ""}},
            "opportunities": {"server": "bi-vault", "tool": "search_startup_ideas", "args": {"query": ""}},
            "problems": {"server": "bi-vault", "tool": "search_problems", "args": {"query": ""}},
            "products": {"server": "bi-vault", "tool": "search_products", "args": {"query": ""}},
            "yc companies": {"server": "railway-postgres", "tool": "search_yc_companies", "args": {"query": ""}},
        }

        plan_lower = plan_text.lower()
        for keyword, template in patterns.items():
            if keyword in plan_lower:
                tool_calls.append(template)

        return tool_calls if tool_calls else []

    async def _get_completion(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        config: ReasoningConfig
    ) -> str:
        """Get non-streaming completion"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_id,
                        "messages": messages,
                        "temperature": config.temperature,
                        "max_tokens": config.max_tokens,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"Error getting completion: {e}")
                return f"[Error: {str(e)}]"

    def _format_available_tools(self) -> str:
        """Format available MCP tools for context"""
        if not self.mcp_client:
            return "No MCP tools currently available (direct API mode)"

        tools = self.mcp_client.get_available_tools()

        lines = []
        for server_name, server_tools in tools.items():
            lines.append(f"\n**{server_name}:**")
            for tool in server_tools:
                tool_name = tool.get("name", "unknown")
                tool_desc = tool.get("description", "No description")
                lines.append(f"- {tool_name}: {tool_desc}")

        return "\n".join(lines)
