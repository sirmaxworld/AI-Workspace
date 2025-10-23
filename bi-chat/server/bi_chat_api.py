#!/usr/bin/env python3
"""
BI Chat API Server
FastAPI server for intelligent BI analysis chat
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from mcp_client import MCPClientManager
from reasoning_orchestrator import ReasoningOrchestrator, ReasoningConfig

# Load environment
load_dotenv('/Users/yourox/AI-Workspace/.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
mcp_manager = MCPClientManager()
orchestrator: Optional[ReasoningOrchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    # Startup
    logger.info("Starting BI Chat API...")

    # Initialize MCP client (temporarily disabled - debugging)
    # base_path = Path("/Users/yourox/AI-Workspace")
    # await mcp_manager.initialize(base_path)

    # Initialize reasoning orchestrator
    global orchestrator
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        logger.error("OPENROUTER_API_KEY not found in environment")
        raise RuntimeError("OPENROUTER_API_KEY not set")

    orchestrator = ReasoningOrchestrator(
        openrouter_api_key=openrouter_key,
        mcp_client=None  # Temporarily None - debugging
    )

    logger.info("BI Chat API ready! (MCP connections temporarily disabled)")

    yield

    # Shutdown
    logger.info("Shutting down BI Chat API...")
    # await mcp_manager.shutdown()


# Initialize FastAPI app
app = FastAPI(
    title="BI Intelligence Chat API",
    description="Intelligent chat interface for business intelligence analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str
    model: str = "claude-sonnet-4.5"
    thinking_mode: str = "quick"
    temperature: float = 0.7
    conversation_history: Optional[List[Message]] = None


class HealthResponse(BaseModel):
    status: str
    mcp_servers: List[str]
    available_models: List[str]


class ModelsResponse(BaseModel):
    models: List[dict]


# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    available_servers = []
    try:
        if mcp_manager._initialized:
            mcp_client = mcp_manager.get_client()
            available_servers = list(mcp_client.sessions.keys())
    except:
        pass  # MCP not initialized - that's OK

    return HealthResponse(
        status="healthy",
        mcp_servers=available_servers,
        available_models=list(orchestrator.model_map.keys()) if orchestrator else []
    )


@app.get("/models", response_model=ModelsResponse)
async def get_models():
    """Get available AI models"""
    models = [
        {
            "id": "gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "provider": "OpenAI",
            "description": "Most capable GPT-4 model, great for complex reasoning"
        },
        {
            "id": "o1-preview",
            "name": "O1 Preview",
            "provider": "OpenAI",
            "description": "Advanced reasoning model with extended thinking"
        },
        {
            "id": "o1-mini",
            "name": "O1 Mini",
            "provider": "OpenAI",
            "description": "Faster reasoning model, good balance of speed and quality"
        },
        {
            "id": "claude-sonnet-4.5",
            "name": "Claude Sonnet 4.5",
            "provider": "Anthropic",
            "description": "Latest Claude model, excellent for analysis and reasoning"
        },
        {
            "id": "claude-opus",
            "name": "Claude Opus 4",
            "provider": "Anthropic",
            "description": "Most powerful Claude model for deep analysis"
        },
        {
            "id": "gemini-pro",
            "name": "Gemini Pro 1.5",
            "provider": "Google",
            "description": "Google's advanced model with large context window"
        },
        {
            "id": "gemini-flash",
            "name": "Gemini Flash 1.5",
            "provider": "Google",
            "description": "Fast and efficient Gemini model"
        },
        {
            "id": "deepseek",
            "name": "DeepSeek V2.5",
            "provider": "DeepSeek",
            "description": "Powerful open model with strong reasoning"
        }
    ]

    return ModelsResponse(models=models)


@app.get("/tools")
async def get_available_tools():
    """Get available MCP tools"""
    try:
        if mcp_manager._initialized:
            mcp_client = mcp_manager.get_client()
            tools = mcp_client.get_available_tools()

            # Format for display
            formatted_tools = {}
            for server_name, server_tools in tools.items():
                formatted_tools[server_name] = [
                    {
                        "name": tool.get("name"),
                        "description": tool.get("description"),
                        "input_schema": tool.get("inputSchema", {})
                    }
                    for tool in server_tools
                ]

            return formatted_tools
    except:
        pass

    return {}


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint - streams reasoning response
    """
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    # Validate model
    if request.model not in orchestrator.model_map:
        available = list(orchestrator.model_map.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model '{request.model}'. Available: {available}"
        )

    # Validate thinking mode
    valid_modes = ["quick", "deep", "critical"]
    if request.thinking_mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid thinking mode. Must be one of: {valid_modes}"
        )

    # Create config
    config = ReasoningConfig(
        model=request.model,
        thinking_mode=request.thinking_mode,
        temperature=request.temperature
    )

    # Convert conversation history
    history = None
    if request.conversation_history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

    # Stream reasoning response
    async def generate():
        try:
            async for chunk in orchestrator.reason(request.query, config, history):
                # Server-sent events format
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Error in chat reasoning: {e}")
            yield f"data: [Error: {str(e)}]\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/examples")
async def get_example_queries():
    """Get example queries for different use cases"""
    from prompts.reasoning_prompts import get_example_queries

    examples = get_example_queries()

    return {
        "examples": [
            {"category": cat.replace("_", " ").title(), "query": query}
            for cat, query in examples.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "bi_chat_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
