#!/usr/bin/env python3
"""
AI Passive Capture System
SAFE: Reads data passively, no terminal hooks, no blocking
Monitors git commits, file changes, and coding history
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set
import hashlib

from ai_session_logger_core import AISessionDB, AISession, generate_id


class PassiveCapture:
    """
    Safely captures coding activity without interfering with terminal
    READS: Git logs, file modifications, existing coding history DB
    NEVER: Hooks into shell, blocks commands, or modifies system
    """

    def __init__(self, project_path: str = "/Users/yourox/AI-Workspace"):
        self.project_path = Path(project_path)
        self.db = AISessionDB()
        self.current_session_id = None

    def start_session(self, tool: str = "claude-code") -> str:
        """Start tracking a new session"""
        session_id = generate_id("session", datetime.now().isoformat(), tool)

        session = AISession(
            session_id=session_id,
            started_at=datetime.now(),
            ended_at=None,
            project_path=str(self.project_path),
            tool=tool,
            total_interactions=0,
            files_modified=[],
            git_commits=[],
            summary=None,
            status="active"
        )

        self.db.create_session(session)
        self.current_session_id = session_id
        return session_id

    def get_recent_git_commits(self, since_minutes: int = 60) -> List[Dict[str, str]]:
        """
        Get recent git commits (passive, read-only)
        SAFE: Just reads git log, no modifications
        """
        try:
            # Get commits from last N minutes
            result = subprocess.run(
                [
                    "git", "log",
                    f"--since={since_minutes} minutes ago",
                    "--pretty=format:%H|%s|%an|%aI",
                    "--no-merges"
                ],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('|')
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0][:8],
                        "message": parts[1],
                        "author": parts[2],
                        "timestamp": parts[3]
                    })

            return commits

        except Exception as e:
            print(f"Warning: Could not read git commits: {e}")
            return []

    def get_modified_files(self, since_minutes: int = 60) -> Set[str]:
        """
        Get files modified recently (passive)
        SAFE: Just reads git diff, no modifications
        """
        try:
            # Get uncommitted changes
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            files = set()
            if result.returncode == 0:
                files.update(result.stdout.strip().split('\n'))

            # Get recently committed changes
            result = subprocess.run(
                [
                    "git", "diff", "--name-only",
                    f"@{{{since_minutes} minutes ago}}",
                    "HEAD"
                ],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                files.update(result.stdout.strip().split('\n'))

            return {f for f in files if f and not f.startswith('.')}

        except Exception as e:
            print(f"Warning: Could not read modified files: {e}")
            return set()

    def read_coding_history(self, hours: int = 24) -> List[Dict]:
        """
        Read from existing coding history database (passive)
        SAFE: Just queries existing database, no modifications
        """
        try:
            import sqlite3
            from datetime import timedelta

            history_db = "/Users/yourox/AI-Workspace/data/coding_history/summaries.db"

            if not Path(history_db).exists():
                return []

            conn = sqlite3.connect(history_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            since = (datetime.now() - timedelta(hours=hours)).isoformat()

            cursor.execute("""
                SELECT s.session_id, s.timestamp, s.prompt, s.outcome,
                       GROUP_CONCAT(a.action, '; ') as actions
                FROM sessions s
                LEFT JOIN actions a ON s.session_id = a.session_id
                WHERE s.timestamp >= ?
                GROUP BY s.session_id
                ORDER BY s.timestamp DESC
            """, (since,))

            activities = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return activities

        except Exception as e:
            print(f"Warning: Could not read coding history: {e}")
            return []

    def create_session_snapshot(self) -> Dict:
        """
        Create a snapshot of current session (passive, read-only)
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "git_commits": self.get_recent_git_commits(since_minutes=60),
            "modified_files": list(self.get_modified_files(since_minutes=60)),
            "coding_activity": self.read_coding_history(hours=24)
        }

    def generate_session_summary(self, snapshot: Dict) -> str:
        """Generate a human-readable summary of the session"""
        lines = []

        if snapshot["git_commits"]:
            lines.append(f"Made {len(snapshot['git_commits'])} commits:")
            for commit in snapshot["git_commits"][:5]:
                lines.append(f"  - {commit['message']}")

        if snapshot["modified_files"]:
            lines.append(f"\nModified {len(snapshot['modified_files'])} files:")
            for f in list(snapshot["modified_files"])[:10]:
                lines.append(f"  - {f}")

        if snapshot["coding_activity"]:
            lines.append(f"\nCoding activity: {len(snapshot['coding_activity'])} actions")

        return "\n".join(lines) if lines else "No significant activity detected"


if __name__ == "__main__":
    # Test passive capture
    capture = PassiveCapture()

    print("🔍 Testing passive capture (read-only, safe)...")
    print()

    print("📊 Recent commits:")
    commits = capture.get_recent_git_commits(since_minutes=240)
    if commits:
        for c in commits[:3]:
            print(f"  {c['hash']} - {c['message']}")
    else:
        print("  No recent commits")

    print("\n📝 Modified files:")
    files = capture.get_modified_files(since_minutes=240)
    if files:
        for f in list(files)[:5]:
            print(f"  {f}")
    else:
        print("  No recent modifications")

    print("\n💻 Coding history:")
    history = capture.read_coding_history(hours=24)
    print(f"  {len(history)} activities in last 24 hours")

    print("\n✅ Passive capture working safely!")
