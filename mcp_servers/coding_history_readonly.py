#!/usr/bin/env python3
"""
Coding History Read-Only MCP Server
Secure: Only queries database, NEVER writes
Claude Desktop can only READ your coding history
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "Coding History (Read-Only)",
    instructions="Query-only access to coding history. No write permissions."
)

DB_PATH = Path.home() / "AI-Workspace" / ".coding_history.db"


def get_connection():
    """Get read-only database connection"""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    # Open in read-only mode (sqlite3.OPEN_READONLY not available in older Python)
    # Use URI to force read-only
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.resource("history://stats")
def get_stats() -> str:
    """Get coding history statistics (read-only)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Total sessions
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total = cursor.fetchone()[0]

        # Recent (24h)
        day_ago = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM sessions WHERE timestamp > ?', (day_ago,))
        recent = cursor.fetchone()[0]

        # Latest timestamp
        cursor.execute('SELECT MAX(timestamp) FROM sessions')
        latest = cursor.fetchone()[0]

        conn.close()

        return f"""📊 Coding History Stats (Read-Only)
{'=' * 40}
Total Sessions: {total}
Recent (24h): {recent}
Latest: {latest or 'None'}
Database: {DB_PATH}
Mode: READ-ONLY (secure)"""

    except Exception as e:
        return f"Error reading stats: {e}"


@mcp.resource("history://recent")
def get_recent() -> str:
    """Get recent sessions (read-only)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT timestamp, prompt, outcome
            FROM sessions
            ORDER BY timestamp DESC
            LIMIT 10
        ''')

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "No sessions found"

        lines = ["📜 Recent Sessions", "=" * 40, ""]
        for row in rows:
            ts = datetime.fromisoformat(row['timestamp']).strftime("%Y-%m-%d %H:%M")
            lines.append(f"[{ts}] {row['prompt']}")
            if row['outcome']:
                lines.append(f"  → {row['outcome']}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error reading recent sessions: {e}"


@mcp.tool()
def search_history(query: str = None, hours_ago: int = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search coding history (read-only)

    Args:
        query: Search term in commands
        hours_ago: Only show last N hours
        limit: Maximum results

    Returns:
        List of matching sessions
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = 'SELECT id, timestamp, command, prompt, outcome FROM sessions'
        params = []
        conditions = []

        if query:
            conditions.append('command LIKE ?')
            params.append(f'%{query}%')

        if hours_ago:
            cutoff = (datetime.now() - timedelta(hours=hours_ago)).isoformat()
            conditions.append('timestamp > ?')
            params.append(cutoff)

        if conditions:
            sql += ' WHERE ' + ' AND '.join(conditions)

        sql += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'command': row['command'],
                'prompt': row['prompt'],
                'outcome': row['outcome']
            })

        return results

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_command_stats(limit: int = 10) -> Dict[str, Any]:
    """
    Get most common commands (read-only)

    Args:
        limit: Number of top commands to return

    Returns:
        Dictionary with command statistics
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                SUBSTR(command, 1, 50) as cmd,
                COUNT(*) as count
            FROM sessions
            GROUP BY SUBSTR(command, 1, 50)
            ORDER BY count DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return {
            'top_commands': [
                {'command': row['cmd'], 'count': row['count']}
                for row in rows
            ]
        }

    except Exception as e:
        return {'error': str(e)}


@mcp.tool()
def export_history(days: int = 7, format: str = "text") -> str:
    """
    Export history for documentation (read-only)

    Args:
        days: Number of days to export
        format: Output format (text or json)

    Returns:
        Formatted export
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute('''
            SELECT timestamp, command, prompt, outcome
            FROM sessions
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (cutoff,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No sessions in last {days} days"

        if format == "json":
            data = []
            for row in rows:
                data.append({
                    'timestamp': row['timestamp'],
                    'command': row['command'],
                    'prompt': row['prompt'],
                    'outcome': row['outcome']
                })
            return json.dumps(data, indent=2)

        else:  # text
            lines = [
                f"Coding History Export",
                f"Period: Last {days} days",
                f"Count: {len(rows)} sessions",
                "=" * 60,
                ""
            ]

            for row in rows:
                ts = datetime.fromisoformat(row['timestamp']).strftime("%Y-%m-%d %H:%M")
                lines.append(f"[{ts}] {row['prompt']}")
                lines.append(f"  Command: {row['command'][:80]}")
                if row['outcome']:
                    lines.append(f"  Outcome: {row['outcome']}")
                lines.append("")

            return "\n".join(lines)

    except Exception as e:
        return f"Error exporting: {e}"


if __name__ == "__main__":
    logger.info("Starting Coding History Read-Only MCP Server")
    logger.info(f"Database: {DB_PATH} (read-only mode)")
    mcp.run(transport="stdio")