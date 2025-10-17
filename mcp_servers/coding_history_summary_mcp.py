#!/usr/bin/env python3
"""
Coding History Summary MCP Server
Provides access to session summaries (not raw output)
Lightweight, fast, and intelligent
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from coding_history_summary import SummaryDB, SessionSummary, queue_event

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "Coding History Summaries",
    instructions="Access intelligent summaries of coding sessions, not raw terminal output."
)

# Initialize database
db = SummaryDB()


@mcp.resource("history://stats")
def get_history_stats() -> str:
    """Get coding history statistics"""
    stats = db.get_stats()

    lines = [
        "📊 Coding History Summary Statistics",
        "=" * 40,
        f"Total Sessions: {stats['total_sessions']}",
        f"Sessions (24h): {stats['recent_sessions_24h']}",
        f"Unique Tools: {stats['unique_tools']}",
        f"Total Errors: {stats['total_errors']}",
        f"Database Size: {stats['db_size_bytes'] / 1024:.1f} KB",
        "",
        "💡 This system stores intelligent summaries,",
        "   not raw terminal output for efficiency."
    ]

    return "\n".join(lines)


@mcp.resource("history://recent")
def get_recent_sessions() -> str:
    """Get recent coding session summaries"""
    sessions = db.search_sessions(limit=10)

    if not sessions:
        return "No recent coding sessions found."

    lines = ["📜 Recent Coding Sessions", "=" * 40, ""]

    for session in sessions:
        timestamp = datetime.fromisoformat(session['timestamp']).strftime("%Y-%m-%d %H:%M")
        lines.append(f"[{timestamp}] {session['prompt']}")
        lines.append(f"  → {session['outcome']}")

        if session['tools']:
            lines.append(f"  Tools: {', '.join(session['tools'][:5])}")

        if session['errors']:
            lines.append(f"  ⚠️  Errors: {len(session['errors'])}")

        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def search_sessions(
    query: Optional[str] = None,
    hours_ago: Optional[int] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search coding session summaries

    Args:
        query: Text to search in prompts and outcomes
        hours_ago: Search within last N hours
        limit: Maximum results to return

    Returns:
        List of session summaries with details
    """
    start_time = None
    if hours_ago:
        start_time = datetime.now() - timedelta(hours=hours_ago)

    sessions = db.search_sessions(
        query=query,
        start_time=start_time,
        limit=limit
    )

    # Format for better display
    for session in sessions:
        # Add human-readable duration
        if session.get('duration_seconds'):
            duration = session['duration_seconds']
            if duration < 60:
                session['duration_display'] = f"{duration:.0f}s"
            elif duration < 3600:
                session['duration_display'] = f"{duration/60:.1f}m"
            else:
                session['duration_display'] = f"{duration/3600:.1f}h"

        # Truncate long lists
        for field in ['actions', 'errors', 'tools', 'files']:
            if session.get(field) and len(session[field]) > 5:
                session[f'{field}_truncated'] = True
                session[field] = session[field][:5]

    return sessions


@mcp.tool()
def get_error_analysis(project_path: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """
    Analyze common errors from coding sessions

    Args:
        project_path: Filter by project (if tracked)
        limit: Maximum error types to return

    Returns:
        Analysis of error patterns with frequencies
    """
    # Get all sessions with errors
    sessions = db.search_sessions(limit=100)

    error_counts = {}
    error_examples = {}

    for session in sessions:
        for error in session.get('errors', []):
            # Simple error categorization
            if 'ModuleNotFoundError' in error:
                error_type = 'ModuleNotFoundError'
            elif 'SyntaxError' in error:
                error_type = 'SyntaxError'
            elif 'TypeError' in error:
                error_type = 'TypeError'
            elif 'npm ERR' in error:
                error_type = 'NPM Error'
            elif 'git' in error.lower():
                error_type = 'Git Error'
            else:
                error_type = 'Other Error'

            error_counts[error_type] = error_counts.get(error_type, 0) + 1

            if error_type not in error_examples:
                error_examples[error_type] = error[:200]

    # Sort by frequency
    sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    return {
        'error_summary': [
            {'type': err_type, 'count': count, 'example': error_examples.get(err_type, '')}
            for err_type, count in sorted_errors
        ],
        'total_errors_analyzed': sum(error_counts.values()),
        'unique_error_types': len(error_counts)
    }


@mcp.tool()
def get_productivity_insights(days: int = 7) -> Dict[str, Any]:
    """
    Get productivity insights from coding history

    Args:
        days: Number of days to analyze

    Returns:
        Insights about coding patterns and productivity
    """
    start_time = datetime.now() - timedelta(days=days)
    sessions = db.search_sessions(start_time=start_time, limit=1000)

    if not sessions:
        return {'message': 'No sessions found in the specified period'}

    # Analyze patterns
    total_duration = sum(s.get('duration_seconds', 0) for s in sessions)
    error_sessions = [s for s in sessions if s.get('errors')]

    # Tool usage
    tool_usage = {}
    for session in sessions:
        for tool in session.get('tools', []):
            tool_usage[tool] = tool_usage.get(tool, 0) + 1

    top_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:10]

    # Time analysis
    sessions_by_hour = {}
    for session in sessions:
        hour = datetime.fromisoformat(session['timestamp']).hour
        sessions_by_hour[hour] = sessions_by_hour.get(hour, 0) + 1

    # Find most productive hours
    productive_hours = sorted(sessions_by_hour.items(), key=lambda x: x[1], reverse=True)[:3]

    insights = {
        'period_days': days,
        'total_sessions': len(sessions),
        'total_time_hours': round(total_duration / 3600, 1),
        'average_session_minutes': round(total_duration / len(sessions) / 60, 1) if sessions else 0,
        'error_rate': round(len(error_sessions) / len(sessions) * 100, 1) if sessions else 0,
        'top_tools': [{'tool': tool, 'uses': count} for tool, count in top_tools],
        'most_active_hours': [{'hour': f"{hour:02d}:00", 'sessions': count} for hour, count in productive_hours],
        'sessions_per_day': round(len(sessions) / days, 1)
    }

    return insights


@mcp.tool()
def create_session_summary(
    prompt: str,
    actions: List[str],
    outcome: str,
    errors: Optional[List[str]] = None,
    tools: Optional[List[str]] = None,
    files: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Manually create a session summary

    Args:
        prompt: What was being attempted
        actions: List of key actions taken
        outcome: Final result
        errors: Any errors encountered
        tools: Tools used
        files: Files modified

    Returns:
        Result of creating the summary
    """
    import hashlib
    import time

    # Generate session ID
    session_id = hashlib.sha256(f"{prompt}{time.time()}".encode()).hexdigest()[:12]

    summary = SessionSummary(
        session_id=session_id,
        timestamp=datetime.now(),
        prompt=prompt,
        actions=actions[:10],
        outcome=outcome,
        errors=errors or [],
        tools_used=tools or [],
        files_modified=files or [],
        duration_seconds=0,  # Manual entry
        metadata={'manual_entry': True}
    )

    db.save_summary(summary)

    return {
        'session_id': session_id,
        'status': 'created',
        'message': f"Session summary created: {prompt[:50]}..."
    }


@mcp.tool()
def export_summaries(
    days: int = 30,
    format: str = "text"
) -> str:
    """
    Export session summaries for documentation

    Args:
        days: Number of days to export
        format: Output format (text or json)

    Returns:
        Formatted export of summaries
    """
    start_time = datetime.now() - timedelta(days=days)
    sessions = db.search_sessions(start_time=start_time, limit=500)

    if not sessions:
        return "No sessions found in the specified period"

    if format == "json":
        return json.dumps({
            'exported_at': datetime.now().isoformat(),
            'period_days': days,
            'session_count': len(sessions),
            'sessions': sessions
        }, indent=2)
    else:
        lines = [
            "Coding Session Summary Export",
            "=" * 60,
            f"Exported: {datetime.now().isoformat()}",
            f"Period: Last {days} days",
            f"Total Sessions: {len(sessions)}",
            "",
        ]

        for session in sessions[:50]:  # Limit text output
            timestamp = datetime.fromisoformat(session['timestamp']).strftime("%Y-%m-%d %H:%M")
            lines.append(f"\n[{timestamp}] {session['prompt']}")
            lines.append(f"Outcome: {session['outcome']}")

            if session['actions']:
                lines.append("Actions:")
                for action in session['actions'][:3]:
                    lines.append(f"  - {action}")

            if session['tools']:
                lines.append(f"Tools: {', '.join(session['tools'])}")

            if session['errors']:
                lines.append(f"⚠️  Errors: {len(session['errors'])}")

            lines.append("-" * 40)

        return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")