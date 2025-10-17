#!/usr/bin/env python3
"""
Coding History MCP Server
Provides MCP-compliant access to terminal output history and coding sessions
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from coding_history_core import (
    CodingHistoryDB,
    CompressionManager,
    CaptureConfig,
    SessionInfo,
    OutputChunk
)

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "Coding History",
    instructions="Access and search your terminal output history and coding sessions."
)

# Initialize components
db = CodingHistoryDB()
compression = CompressionManager()
config = CaptureConfig()


@mcp.resource("history://stats")
def get_history_stats() -> str:
    """Get coding history statistics"""
    with db.lock:
        cursor = db.conn.cursor()

        # Get overall stats
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM output_chunks")
        total_chunks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'active'")
        active_sessions = cursor.fetchone()[0]

        # Get recent activity
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM output_chunks WHERE timestamp >= ?",
            (week_ago,)
        )
        recent_chunks = cursor.fetchone()[0]

        # Get project statistics
        cursor.execute("""
            SELECT project_path, COUNT(*) as session_count
            FROM sessions
            GROUP BY project_path
            ORDER BY session_count DESC
            LIMIT 5
        """)
        top_projects = cursor.fetchall()

        # Format response
        lines = [
            "📊 Coding History Statistics",
            "=" * 40,
            f"Total Sessions: {total_sessions}",
            f"Active Sessions: {active_sessions}",
            f"Total Output Chunks: {total_chunks}",
            f"Recent Chunks (7 days): {recent_chunks}",
            f"Capture Enabled: {config.is_capture_enabled()}",
            "",
            "Top Projects:",
        ]

        for project, count in top_projects:
            lines.append(f"  - {project}: {count} sessions")

        return "\n".join(lines)


@mcp.resource("history://recent")
def get_recent_history() -> str:
    """Get recent coding history"""
    results = db.search_chunks(limit=20)

    if not results:
        return "No recent coding history found."

    lines = ["📜 Recent Coding History", "=" * 40, ""]

    for chunk in results:
        timestamp = datetime.fromisoformat(chunk['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"[{timestamp}] {chunk['output_type'].upper()}")
        lines.append(f"Project: {chunk['project_path']}")
        if chunk['tool_used']:
            lines.append(f"Tool: {chunk['tool_used']}")
        lines.append(f"Size: {chunk['content_length']} bytes")
        lines.append("-" * 30)

    return "\n".join(lines)


@mcp.tool()
def search_history(
    query: Optional[str] = None,
    project_path: Optional[str] = None,
    output_type: Optional[str] = None,
    hours_ago: Optional[int] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search coding history with filters

    Args:
        query: Text to search for in outputs
        project_path: Filter by project path
        output_type: Filter by type (command, output, error, info)
        hours_ago: Search within last N hours
        limit: Maximum results to return

    Returns:
        List of matching history chunks with metadata
    """
    start_time = None
    if hours_ago:
        start_time = datetime.now() - timedelta(hours=hours_ago)

    results = db.search_chunks(
        query=query,
        project_path=project_path,
        output_type=output_type,
        start_time=start_time,
        limit=limit
    )

    # Add decompressed content for first few results
    detailed_results = []
    for i, chunk in enumerate(results):
        if i < 5:  # Decompress first 5 for detail
            try:
                content = compression.decompress_chunk(chunk['compressed_path'])
                chunk['content_preview'] = content[:500] + ("..." if len(content) > 500 else "")
            except Exception as e:
                chunk['content_preview'] = f"[Error decompressing: {e}]"
        detailed_results.append(chunk)

    return detailed_results


@mcp.tool()
def get_session_details(session_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific session

    Args:
        session_id: The session ID to retrieve

    Returns:
        Session details including metadata and statistics
    """
    session = db.get_session_info(session_id)
    if not session:
        return {"error": f"Session {session_id} not found"}

    # Get chunks for this session
    chunks = db.search_chunks(session_id=session_id, limit=100)

    # Add chunk summary
    session['chunk_count'] = len(chunks)
    session['chunk_types'] = {}
    for chunk in chunks:
        chunk_type = chunk['output_type']
        session['chunk_types'][chunk_type] = session['chunk_types'].get(chunk_type, 0) + 1

    return session


@mcp.tool()
def toggle_capture(enabled: bool) -> str:
    """
    Toggle coding history capture on/off

    Args:
        enabled: True to enable capture, False to disable

    Returns:
        Status message
    """
    config.toggle_capture(enabled)
    status = "enabled" if enabled else "disabled"
    return f"Coding history capture {status}"


@mcp.tool()
def get_error_patterns(project_path: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get common error patterns from history

    Args:
        project_path: Filter by project
        limit: Maximum patterns to return

    Returns:
        List of error patterns with frequency and solutions
    """
    # Search for error chunks
    error_chunks = db.search_chunks(
        project_path=project_path,
        output_type="error",
        limit=100
    )

    # Analyze patterns (simplified for now)
    patterns = []
    error_counts = {}

    for chunk in error_chunks:
        # Try to decompress and extract error type
        try:
            content = compression.decompress_chunk(chunk['compressed_path'])
            # Simple pattern extraction (can be enhanced)
            if "ModuleNotFoundError" in content:
                error_type = "ModuleNotFoundError"
            elif "SyntaxError" in content:
                error_type = "SyntaxError"
            elif "TypeError" in content:
                error_type = "TypeError"
            elif "AttributeError" in content:
                error_type = "AttributeError"
            else:
                error_type = "Other"

            if error_type not in error_counts:
                error_counts[error_type] = {
                    "type": error_type,
                    "count": 0,
                    "last_seen": chunk['timestamp'],
                    "example": content[:200]
                }
            error_counts[error_type]["count"] += 1

        except Exception:
            continue

    # Convert to list and sort by frequency
    patterns = sorted(error_counts.values(), key=lambda x: x["count"], reverse=True)

    return patterns[:limit]


@mcp.tool()
def export_session_history(
    session_id: Optional[str] = None,
    project_path: Optional[str] = None,
    format: str = "text"
) -> str:
    """
    Export session history to readable format

    Args:
        session_id: Specific session to export
        project_path: Export all sessions for project
        format: Output format (text or json)

    Returns:
        Formatted history export
    """
    # Get chunks based on filters
    chunks = db.search_chunks(
        session_id=session_id,
        project_path=project_path,
        limit=1000
    )

    if not chunks:
        return "No history found for export"

    if format == "json":
        # Return JSON format
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "chunk_count": len(chunks),
            "chunks": []
        }

        for chunk in chunks[:100]:  # Limit decompression
            try:
                content = compression.decompress_chunk(chunk['compressed_path'])
                chunk['content'] = content
                export_data['chunks'].append(chunk)
            except Exception as e:
                chunk['content'] = f"[Decompression error: {e}]"
                export_data['chunks'].append(chunk)

        return json.dumps(export_data, indent=2)

    else:
        # Text format
        lines = [
            "Coding History Export",
            "=" * 60,
            f"Exported: {datetime.now().isoformat()}",
            f"Total chunks: {len(chunks)}",
            "",
        ]

        for chunk in chunks[:50]:  # Limit for text format
            timestamp = datetime.fromisoformat(chunk['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"\n[{timestamp}] {chunk['output_type'].upper()}")
            lines.append(f"Project: {chunk['project_path']}")

            if chunk['tool_used']:
                lines.append(f"Tool: {chunk['tool_used']}")

            if chunk['exit_code'] is not None:
                lines.append(f"Exit Code: {chunk['exit_code']}")

            try:
                content = compression.decompress_chunk(chunk['compressed_path'])
                lines.append("-" * 40)
                lines.append(content[:500] + ("..." if len(content) > 500 else ""))
                lines.append("-" * 40)
            except Exception as e:
                lines.append(f"[Content unavailable: {e}]")

        return "\n".join(lines)


@mcp.tool()
def create_session(
    project_path: str,
    tool_name: str = "claude",
    tags: Optional[List[str]] = None,
    context: Optional[str] = None
) -> Dict[str, str]:
    """
    Create a new coding history session

    Args:
        project_path: Path to the project
        tool_name: Name of the tool (claude, cursor, vscode, etc.)
        tags: Optional tags for the session
        context: Optional context description

    Returns:
        Session creation result with session_id
    """
    import uuid

    session = SessionInfo(
        session_id=str(uuid.uuid4()),
        project_path=project_path,
        cursor_context=context,
        started_at=datetime.now(),
        ended_at=None,
        tool_name=tool_name,
        tags=tags or [],
        status="active"
    )

    session_id = db.create_session(session)

    return {
        "session_id": session_id,
        "status": "created",
        "message": f"Session {session_id[:8]}... created for {project_path}"
    }


@mcp.tool()
def add_output(
    session_id: str,
    content: str,
    output_type: str = "output",
    tool_used: Optional[str] = None,
    exit_code: Optional[int] = None
) -> Dict[str, str]:
    """
    Add output to a coding history session

    Args:
        session_id: Session to add output to
        content: The output content
        output_type: Type of output (command, output, error, info)
        tool_used: Tool that generated output
        exit_code: Exit code if applicable

    Returns:
        Result of adding the output
    """
    import uuid

    chunk = OutputChunk(
        chunk_id=str(uuid.uuid4()),
        session_id=session_id,
        timestamp=datetime.now(),
        output_type=output_type,
        content=content,
        tool_used=tool_used,
        exit_code=exit_code,
        duration_ms=None,
        metadata={}
    )

    compressed_path, content_hash = compression.compress_chunk(chunk)
    chunk_id = db.add_chunk(chunk, compressed_path, content_hash)

    return {
        "chunk_id": chunk_id,
        "status": "added",
        "compressed_size": len(compressed_path),
        "content_hash": content_hash[:8] + "..."
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")