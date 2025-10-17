#!/usr/bin/env python3
"""
Coding History MCP Server
Provides access to terminal output history with advanced search capabilities
"""

import sys
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from coding_history_core import (
    CodingHistoryDB, CompressionManager, CaptureConfig
)
from coding_history_capture import OutputCapture

from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP(
    "Coding History",
    instructions="""
Provides comprehensive access to coding session history with:
- Terminal output capture and storage
- Advanced search capabilities (keyword, time-based, project-based)
- Pattern recognition for errors and solutions
- Session management and progress tracking
- Configurable capture toggle

Use search_history() for general searches, get_session() for specific sessions,
and toggle_capture() to control recording.
    """
)

# Initialize components
db = CodingHistoryDB()
compression = CompressionManager()
config = CaptureConfig()
active_captures: Dict[str, OutputCapture] = {}


@mcp.resource("history://recent")
def get_recent_history() -> str:
    """Get recent coding history summary"""
    results = db.search_chunks(limit=50)

    if not results:
        return "No recent coding history found"

    lines = ["📚 RECENT CODING HISTORY", "=" * 50, ""]

    # Group by session
    sessions = {}
    for chunk in results:
        sid = chunk['session_id']
        if sid not in sessions:
            sessions[sid] = {
                'project': chunk['project_path'],
                'tool': chunk['tool_name'],
                'chunks': []
            }
        sessions[sid]['chunks'].append(chunk)

    for sid, session in list(sessions.items())[:5]:
        lines.append(f"\n🔹 Session {sid[:8]}...")
        lines.append(f"   Project: {session['project']}")
        lines.append(f"   Tool: {session['tool']}")
        lines.append(f"   Actions: {len(session['chunks'])} items")

        # Show last few chunks
        for chunk in session['chunks'][:3]:
            timestamp = chunk['timestamp'].split('T')[1][:8]
            type_icon = {
                'command': '⚡',
                'output': '📝',
                'error': '❌',
                'info': 'ℹ️'
            }.get(chunk['output_type'], '•')

            preview = ""
            if chunk['content_length'] < 100:
                # Load small content directly
                content = compression.decompress_chunk(chunk['compressed_path'])
                preview = content[:80].replace('\n', ' ')
            else:
                preview = f"[{chunk['content_length']} bytes]"

            lines.append(f"     {type_icon} [{timestamp}] {preview}")

    return "\n".join(lines)


@mcp.tool()
def search_history(
    query: Optional[str] = None,
    project_path: Optional[str] = None,
    output_type: Optional[str] = None,
    hours_ago: Optional[int] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Search coding history with multiple filters.

    Args:
        query: Text to search for
        project_path: Filter by project path
        output_type: Filter by type (command, output, error, info)
        hours_ago: Search within last N hours
        limit: Maximum results to return

    Returns:
        List of matching history entries with content
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

    # Decompress and return content for each result
    enriched_results = []
    for chunk in results:
        try:
            content = compression.decompress_chunk(chunk['compressed_path'])
            enriched_results.append({
                **chunk,
                'content': content[:1000],  # Limit content size
                'content_truncated': len(content) > 1000
            })
        except Exception as e:
            enriched_results.append({
                **chunk,
                'content': f"[Error loading content: {e}]",
                'content_truncated': False
            })

    return enriched_results


@mcp.tool()
def get_session(session_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific session.

    Args:
        session_id: Session ID (can be partial)

    Returns:
        Session details with all chunks
    """
    # Find matching session
    info = db.get_session_info(session_id)
    if not info:
        # Try partial match
        with db.lock:
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT session_id FROM sessions
                WHERE session_id LIKE ?
                LIMIT 1
            """, (f"{session_id}%",))
            row = cursor.fetchone()
            if row:
                info = db.get_session_info(row[0])

    if not info:
        return {"error": f"Session not found: {session_id}"}

    # Get all chunks for this session
    chunks = db.search_chunks(session_id=info['session_id'], limit=1000)

    # Load content for each chunk
    for chunk in chunks:
        try:
            chunk['content'] = compression.decompress_chunk(chunk['compressed_path'])
        except:
            chunk['content'] = "[Content unavailable]"

    return {
        "session": info,
        "chunks": chunks,
        "total_chunks": len(chunks)
    }


@mcp.tool()
def get_errors(
    project_path: Optional[str] = None,
    hours_ago: int = 24,
    with_solutions: bool = False
) -> List[Dict[str, Any]]:
    """
    Get recent errors from coding sessions.

    Args:
        project_path: Filter by project
        hours_ago: Look back N hours
        with_solutions: Include potential solutions

    Returns:
        List of errors with context
    """
    start_time = datetime.now() - timedelta(hours=hours_ago)

    errors = db.search_chunks(
        project_path=project_path,
        output_type="error",
        start_time=start_time,
        limit=100
    )

    results = []
    for error in errors:
        content = compression.decompress_chunk(error['compressed_path'])

        error_info = {
            "timestamp": error['timestamp'],
            "project": error['project_path'],
            "content": content,
            "session_id": error['session_id']
        }

        # Find related command (what caused this error)
        with db.lock:
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT * FROM output_chunks
                WHERE session_id = ? AND output_type = 'command'
                  AND timestamp < ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (error['session_id'], error['timestamp']))

            cmd_row = cursor.fetchone()
            if cmd_row:
                cmd_path = cmd_row[9]  # compressed_path column
                error_info['command'] = compression.decompress_chunk(cmd_path)

        if with_solutions:
            # Look for similar errors that were resolved
            # (This is a simplified version - could be enhanced with ML)
            error_keywords = content.lower().split()[:5]
            potential_solutions = []

            for keyword in error_keywords:
                solutions = db.search_chunks(
                    query=keyword,
                    output_type="output",
                    limit=5
                )
                for sol in solutions:
                    if "success" in sol.get('metadata', {}).get('tags', []):
                        potential_solutions.append(sol)

            error_info['potential_solutions'] = potential_solutions[:3]

        results.append(error_info)

    return results


@mcp.tool()
def start_capture(
    project_path: str,
    tool_name: str = "cursor",
    tags: Optional[List[str]] = None
) -> str:
    """
    Start capturing terminal output for a project.

    Args:
        project_path: Path to the project
        tool_name: Name of the tool (cursor, vscode, terminal, etc.)
        tags: Optional tags for the session

    Returns:
        Session ID
    """
    if not config.should_capture_project(project_path):
        return f"❌ Capture disabled for project: {project_path}"

    session_id = str(uuid.uuid4())
    capture = OutputCapture(session_id, project_path, tool_name)

    # Store active capture
    active_captures[session_id] = capture

    return f"✅ Started capture session: {session_id[:8]}..."


@mcp.tool()
def stop_capture(session_id: str) -> str:
    """
    Stop a capture session.

    Args:
        session_id: Session ID (can be partial)

    Returns:
        Confirmation message
    """
    # Find matching session
    matching = None
    for sid in active_captures:
        if sid.startswith(session_id):
            matching = sid
            break

    if not matching:
        return f"❌ No active session found: {session_id}"

    capture = active_captures.pop(matching)
    capture.close()

    return f"✅ Stopped capture session: {matching[:8]}..."


@mcp.tool()
def toggle_capture(enabled: bool) -> str:
    """
    Toggle global capture on/off.

    Args:
        enabled: True to enable, False to disable

    Returns:
        Confirmation message
    """
    config.toggle_capture(enabled)

    if enabled:
        return "✅ Capture ENABLED - Terminal outputs will be recorded"
    else:
        # Stop all active captures
        for capture in active_captures.values():
            capture.close()
        active_captures.clear()

        return "⏸️ Capture DISABLED - Terminal outputs will NOT be recorded"


@mcp.tool()
def get_capture_status() -> Dict[str, Any]:
    """
    Get current capture configuration and status.

    Returns:
        Current configuration and active sessions
    """
    return {
        "capture_enabled": config.is_capture_enabled(),
        "active_sessions": [
            {
                "session_id": sid[:8],
                "project": capture.project_path,
                "tool": capture.tool_name
            }
            for sid, capture in active_captures.items()
        ],
        "configuration": config.config,
        "database_stats": {
            "total_sessions": db.conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
            "total_chunks": db.conn.execute("SELECT COUNT(*) FROM output_chunks").fetchone()[0],
            "database_size": Path(db.conn.execute("PRAGMA database_size").fetchone()[0]).stat().st_size
        }
    }


@mcp.tool()
def capture_command(
    command: str,
    project_path: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """
    Manually capture a command execution.

    Args:
        command: The command to capture
        project_path: Project path (uses current if not specified)
        session_id: Session to add to (creates new if not specified)

    Returns:
        Confirmation message
    """
    if not config.is_capture_enabled():
        return "❌ Capture is disabled"

    # Find or create session
    if session_id and session_id in active_captures:
        capture = active_captures[session_id]
    else:
        sid = session_id or str(uuid.uuid4())
        path = project_path or "/Users/yourox/AI-Workspace"
        capture = OutputCapture(sid, path, "manual")
        active_captures[sid] = capture

    capture.capture_command(command)

    return f"✅ Captured command in session {capture.session_id[:8]}..."


@mcp.tool()
def capture_output(
    content: str,
    output_type: str = "output",
    session_id: Optional[str] = None,
    project_path: Optional[str] = None
) -> str:
    """
    Manually capture output content.

    Args:
        content: The output content
        output_type: Type (output, error, info)
        session_id: Session to add to
        project_path: Project path

    Returns:
        Confirmation message
    """
    if not config.is_capture_enabled():
        return "❌ Capture is disabled"

    # Find or create session
    if session_id and session_id in active_captures:
        capture = active_captures[session_id]
    else:
        sid = session_id or str(uuid.uuid4())
        path = project_path or "/Users/yourox/AI-Workspace"
        capture = OutputCapture(sid, path, "manual")
        active_captures[sid] = capture

    capture.capture_output(content, output_type)

    return f"✅ Captured {output_type} in session {capture.session_id[:8]}..."


@mcp.tool()
def get_project_summary(project_path: str, days: int = 7) -> Dict[str, Any]:
    """
    Get a summary of coding activity for a project.

    Args:
        project_path: Project path to analyze
        days: Number of days to look back

    Returns:
        Project activity summary
    """
    start_time = datetime.now() - timedelta(days=days)

    with db.lock:
        cursor = db.conn.cursor()

        # Get session statistics
        cursor.execute("""
            SELECT
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(DISTINCT DATE(started_at)) as active_days,
                SUM(total_commands) as total_commands,
                SUM(total_errors) as total_errors,
                SUM(total_chunks) as total_chunks
            FROM sessions
            WHERE project_path = ? AND started_at >= ?
        """, (project_path, start_time.isoformat()))

        stats = cursor.fetchone()

        # Get most common commands
        cursor.execute("""
            SELECT c.tool_used, COUNT(*) as count
            FROM output_chunks c
            JOIN sessions s ON c.session_id = s.session_id
            WHERE s.project_path = ? AND c.timestamp >= ?
              AND c.output_type = 'command'
            GROUP BY c.tool_used
            ORDER BY count DESC
            LIMIT 5
        """, (project_path, start_time.isoformat()))

        top_tools = cursor.fetchall()

        # Get error patterns
        cursor.execute("""
            SELECT COUNT(*) as error_count, DATE(c.timestamp) as date
            FROM output_chunks c
            JOIN sessions s ON c.session_id = s.session_id
            WHERE s.project_path = ? AND c.timestamp >= ?
              AND c.output_type = 'error'
            GROUP BY date
            ORDER BY date DESC
        """, (project_path, start_time.isoformat()))

        error_timeline = cursor.fetchall()

    return {
        "project": project_path,
        "period": f"Last {days} days",
        "statistics": {
            "total_sessions": stats[0] or 0,
            "active_days": stats[1] or 0,
            "total_commands": stats[2] or 0,
            "total_errors": stats[3] or 0,
            "total_chunks": stats[4] or 0
        },
        "top_tools": [
            {"tool": tool or "unknown", "count": count}
            for tool, count in top_tools
        ],
        "error_timeline": [
            {"date": date, "errors": count}
            for count, date in error_timeline
        ]
    }


@mcp.tool()
def configure_capture(
    capture_commands: Optional[bool] = None,
    capture_outputs: Optional[bool] = None,
    capture_errors: Optional[bool] = None,
    excluded_patterns: Optional[List[str]] = None,
    included_projects: Optional[List[str]] = None,
    excluded_projects: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Configure capture settings.

    Args:
        capture_commands: Whether to capture commands
        capture_outputs: Whether to capture outputs
        capture_errors: Whether to capture errors
        excluded_patterns: Patterns to exclude from capture
        included_projects: Projects to include (empty = all)
        excluded_projects: Projects to exclude

    Returns:
        Updated configuration
    """
    if capture_commands is not None:
        config.config["capture_commands"] = capture_commands

    if capture_outputs is not None:
        config.config["capture_outputs"] = capture_outputs

    if capture_errors is not None:
        config.config["capture_errors"] = capture_errors

    if excluded_patterns is not None:
        config.config["excluded_patterns"] = excluded_patterns

    if included_projects is not None:
        config.config["included_projects"] = included_projects

    if excluded_projects is not None:
        config.config["excluded_projects"] = excluded_projects

    config.save_config()

    return {
        "message": "✅ Configuration updated",
        "configuration": config.config
    }


if __name__ == "__main__":
    # Run with stdio transport for Claude Desktop/Cursor
    mcp.run(transport="stdio")