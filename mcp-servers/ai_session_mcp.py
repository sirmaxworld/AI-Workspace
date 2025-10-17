#!/usr/bin/env python3
"""
AI Session Logger - MCP Server
Provides Claude Desktop access to your coding sessions, learnings, and patterns
The "coding bot that knows you better than you do"
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_session_logger_core import AISessionDB
from ai_learning_extractor import LearningExtractor
from ai_passive_capture import PassiveCapture

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "AI Session Logger",
    instructions="Access your coding history, learnings, patterns, and get personalized suggestions based on YOUR coding style."
)

# Initialize components
db = AISessionDB()
extractor = LearningExtractor()
capture = PassiveCapture()


@mcp.resource("ai-sessions://stats")
def get_stats() -> str:
    """Get overall AI session statistics"""
    stats = db.get_session_stats()

    lines = [
        "📊 Your AI Coding Intelligence",
        "=" * 50,
        f"Total Sessions: {stats['total_sessions']}",
        f"Learnings Captured: {stats['total_learnings']}",
        f"Patterns Detected: {stats['total_patterns']}",
        "",
        "Learning Breakdown:"
    ]

    for category, count in stats.get('learning_breakdown', {}).items():
        lines.append(f"  {category}: {count}")

    return "\n".join(lines)


@mcp.resource("ai-sessions://suggestions")
def get_personalized_suggestions() -> str:
    """Get personalized coding suggestions based on YOUR patterns"""
    suggestions = extractor.get_personalized_suggestions()

    lines = [
        "💡 Personalized Suggestions For You",
        "=" * 50,
        ""
    ]

    for suggestion in suggestions:
        lines.append(suggestion)
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def query_learnings(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Query your past learnings and insights

    Args:
        category: Filter by category (error-solution, decision, insight)
        search: Search in title/description
        limit: Maximum results

    Returns:
        List of learnings with context
    """
    learnings = db.get_learnings(category=category, limit=limit)

    results = []
    for l in learnings:
        learning_dict = dict(l)

        # Parse JSON fields
        if learning_dict.get("tags"):
            learning_dict["tags"] = json.loads(learning_dict["tags"])
        if learning_dict.get("context"):
            learning_dict["context"] = json.loads(learning_dict["context"])

        # Apply search filter
        if search:
            text = f"{learning_dict.get('title', '')} {learning_dict.get('description', '')}".lower()
            if search.lower() not in text:
                continue

        results.append(learning_dict)

    return results[:limit]


@mcp.tool()
def get_error_solutions(error_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get solutions to errors you've encountered before

    Args:
        error_type: Optional filter (missing-dependency, syntax-error, etc.)

    Returns:
        List of error-solution pairs from your history
    """
    learnings = db.get_learnings(category="error-solution", limit=50)

    results = []
    for l in learnings:
        learning_dict = dict(l)
        learning_dict["tags"] = json.loads(learning_dict.get("tags", "[]"))
        learning_dict["context"] = json.loads(learning_dict.get("context", "{}"))

        # Filter by error type
        if error_type and learning_dict["context"].get("error_type") != error_type:
            continue

        results.append({
            "error_type": learning_dict["context"].get("error_type", "unknown"),
            "title": learning_dict.get("title", ""),
            "description": learning_dict.get("description", ""),
            "solution": learning_dict.get("code_snippet", ""),
            "timestamp": learning_dict.get("timestamp", "")
        })

    return results


@mcp.tool()
def get_your_patterns() -> Dict[str, Any]:
    """
    Get YOUR coding patterns and habits
    This is what makes the bot "know you better than you do"

    Returns:
        Your patterns categorized by type
    """
    patterns = db.get_patterns()

    categorized = {
        "problem-solving-approach": [],
        "code-style": [],
        "decision-making": [],
    }

    for p in patterns:
        pattern_dict = dict(p)
        pattern_dict["examples"] = json.loads(pattern_dict.get("examples", "[]"))
        pattern_dict["suggestions"] = json.loads(pattern_dict.get("suggestions", "[]"))

        pattern_type = pattern_dict.get("pattern_type", "unknown")
        if pattern_type in categorized:
            categorized[pattern_type].append(pattern_dict)

    return {
        "total_patterns": len(patterns),
        "patterns_by_type": categorized,
        "summary": f"Detected {len(patterns)} unique patterns in your coding style"
    }


@mcp.tool()
def search_similar_problems(description: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Find when you solved similar problems before

    Args:
        description: Describe the problem you're facing
        limit: Maximum results

    Returns:
        Similar sessions with solutions
    """
    similar_sessions = db.search_similar_sessions(description, limit=limit)

    results = []
    for session in similar_sessions:
        session_dict = dict(session)

        # Get learnings for this session
        learnings = db.get_learnings(category=None, limit=50)
        session_learnings = [
            l for l in learnings
            if l.get("session_id") == session_dict.get("session_id")
        ]

        results.append({
            "session_id": session_dict.get("session_id", ""),
            "summary": session_dict.get("summary", ""),
            "started_at": session_dict.get("started_at", ""),
            "learnings": session_dict.get("learnings", ""),
            "relevant_insights": [l.get("title") for l in session_learnings[:3]]
        })

    return results


@mcp.tool()
def get_recent_activity() -> Dict[str, Any]:
    """
    Get snapshot of your recent coding activity
    Useful for daily summaries and progress tracking
    """
    snapshot = capture.create_session_snapshot()
    summary = capture.generate_session_summary(snapshot)

    return {
        "timestamp": snapshot["timestamp"],
        "summary": summary,
        "git_commits_count": len(snapshot["git_commits"]),
        "files_modified_count": len(snapshot["modified_files"]),
        "recent_commits": snapshot["git_commits"][:5],
        "modified_files": snapshot["modified_files"][:10],
        "coding_activities": len(snapshot["coding_activity"])
    }


@mcp.tool()
def record_decision(
    decision: str,
    rationale: str,
    tags: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Manually record an important decision
    Great for documenting "why" you chose something

    Args:
        decision: What decision was made
        rationale: Why you made this decision
        tags: Optional tags (database, architecture, api, etc.)

    Returns:
        Confirmation with learning ID
    """
    # Create a session if none exists
    session_id = capture.start_session()

    learning = extractor.detect_decision_pattern(
        decision_description=decision,
        rationale=rationale,
        session_id=session_id
    )

    # Add custom tags
    if tags:
        learning.tags.extend(tags)

    learning_id = db.add_learning(learning)

    return {
        "learning_id": learning_id,
        "status": "recorded",
        "message": f"Decision recorded: {decision[:50]}..."
    }


@mcp.tool()
def create_daily_summary(date: Optional[str] = None) -> str:
    """
    Generate a daily summary of your coding work
    Perfect for progress tracking and reflection

    Args:
        date: Optional date (YYYY-MM-DD), defaults to today

    Returns:
        Markdown-formatted daily summary
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Get activity for the date
    activity = get_recent_activity()

    # Get learnings from today
    learnings = db.get_learnings(limit=100)
    today_learnings = [
        l for l in learnings
        if l.get("timestamp", "").startswith(date)
    ]

    lines = [
        f"# Daily Summary - {date}",
        "",
        "## 📊 Activity",
        f"- Commits: {activity['git_commits_count']}",
        f"- Files Modified: {activity['files_modified_count']}",
        f"- Coding Activities: {activity['coding_activities']}",
        "",
    ]

    if activity["recent_commits"]:
        lines.append("## 💻 Recent Commits")
        for commit in activity["recent_commits"]:
            lines.append(f"- {commit['message']}")
        lines.append("")

    if today_learnings:
        lines.append(f"## 🎓 Learnings ({len(today_learnings)})")
        for learning in today_learnings[:5]:
            lines.append(f"- **{learning.get('title', '')}**")
            lines.append(f"  {learning.get('description', '')[:100]}...")
        lines.append("")

    # Add personalized suggestions
    suggestions = extractor.get_personalized_suggestions()
    if suggestions:
        lines.append("## 💡 Suggestions")
        for suggestion in suggestions:
            lines.append(f"- {suggestion}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
