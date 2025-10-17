#!/usr/bin/env python3
"""
Claude Memory MCP Server
Official MCP-compliant server for persistent memory access in Claude Desktop

Based on Model Context Protocol specification
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from claude_memory_ultimate import UltimateMemorySystem
from knowledge_pipeline import KnowledgePipeline


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")


mcp = FastMCP(
    "Claude Knowledge",
    instructions="Provides unified access to persistent memory and curated knowledge base."
)

WORKSPACE = Path("/Users/yourox/AI-Workspace")
PIPELINE = KnowledgePipeline(WORKSPACE)


def load_dual_memory() -> UltimateMemorySystem:
    return UltimateMemorySystem()


def format_memory_context(limit: int = 15) -> str:
    mem = load_dual_memory()
    return mem.load_context(limit=limit)


def load_knowledge_summary(limit: int = 10) -> str:
    runs_dir = WORKSPACE / 'data' / 'pipeline_runs'
    if not runs_dir.exists():
        return "No curated knowledge runs yet."

    summaries: list[tuple[str, Dict[str, Any]]] = []

    for domain_dir in runs_dir.iterdir():
        if not domain_dir.is_dir():
            continue
        for run_dir in sorted(domain_dir.iterdir(), reverse=True):
            summary_file = run_dir / 'pipeline_summary.json'
            if summary_file.exists():
                try:
                    with open(summary_file, 'r') as fh:
                        summaries.append((domain_dir.name, json.load(fh)))
                except json.JSONDecodeError:
                    continue
            if len(summaries) >= limit:
                break

    if not summaries:
        return "No pipeline summaries available."

    lines = ["📚 Curated Knowledge Runs", "=" * 60, ""]
    for domain_key, summary in summaries[:limit]:
        lines.append(f"Domain: {domain_key}")
        lines.append(f"Run ID: {summary.get('run_id')}")
        lines.append(f"Started: {summary.get('started_at')}")
        ingestion = summary.get('ingestion', {})
        lines.append(f"Items queued: {ingestion.get('queued')} | Deduped: {ingestion.get('deduplicated')} | Mem0 stored: {ingestion.get('mem0_ingested')}")
        lines.append(f"Artifacts: {summary.get('artifact_dir')}")
        lines.append("")

    return "\n".join(lines)


@mcp.resource("memory://context")
def get_memory_context() -> str:
    return format_memory_context()


@mcp.resource("knowledge://recent_runs")
def get_recent_knowledge_runs() -> str:
    return load_knowledge_summary()


@mcp.tool()
def save_memory(text: str, memory_type: str = "conversation") -> str:
    mem = load_dual_memory()
    success, message = mem.save_memory(text, memory_type)
    if success:
        stats = mem.get_stats()
        return f"{message}\nTotal memories: {stats['total_memories']}"
    return f"Failed to save memory: {message}"


@mcp.tool()
def search_memories(query: str, limit: int = 10) -> str:
    mem = load_dual_memory()
    context = mem.load_context(query=query, limit=limit)
    return context


@mcp.tool()
def get_memory_stats() -> Dict[str, Any]:
    mem = load_dual_memory()
    stats = mem.get_stats()
    stats["dual_layer"] = True
    stats["mem0_enabled"] = mem.mem0_enabled
    return stats


@mcp.tool()
def run_pipeline(domain_key: str) -> Dict[str, Any]:
    result = PIPELINE.run(domain_key)
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
