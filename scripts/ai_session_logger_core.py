#!/usr/bin/env python3
"""
AI Session Logger - Core Components
SAFE: Read-only, no terminal hooks, passive monitoring
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading


BASE_DIR = Path("/Users/yourox/AI-Workspace/data/ai_sessions")
BASE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class AISession:
    """Represents a single AI coding session"""
    session_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    project_path: str
    tool: str  # claude-code, cursor, etc
    total_interactions: int
    files_modified: List[str]
    git_commits: List[str]
    summary: Optional[str]
    status: str  # active, completed, error


@dataclass
class Learning:
    """Represents a captured learning/insight"""
    learning_id: str
    session_id: str
    timestamp: datetime
    category: str  # error-solution, decision, insight, pattern
    title: str
    description: str
    code_snippet: Optional[str]
    tags: List[str]
    context: Dict[str, Any]
    confidence: float  # 0-1, how confident we are this is useful


@dataclass
class CodingPattern:
    """Represents detected coding pattern/habit"""
    pattern_id: str
    pattern_type: str  # problem-solving-approach, code-style, decision-making
    description: str
    frequency: int
    first_seen: datetime
    last_seen: datetime
    examples: List[str]  # session_ids
    is_beneficial: Optional[bool]  # None = unknown, True = good, False = bad
    suggestions: List[str]


class AISessionDB:
    """
    Thread-safe database for AI sessions
    SAFE: Read-only access, no terminal interaction
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(BASE_DIR / "sessions" / "ai_sessions.db")

        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.lock = threading.RLock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with self.lock:
            cursor = self.conn.cursor()

            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    project_path TEXT NOT NULL,
                    tool TEXT NOT NULL,
                    total_interactions INTEGER DEFAULT 0,
                    files_modified TEXT,  -- JSON array
                    git_commits TEXT,     -- JSON array
                    summary TEXT,
                    status TEXT DEFAULT 'active',
                    metadata TEXT         -- JSON for extensibility
                )
            """)

            # Learnings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learnings (
                    learning_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    code_snippet TEXT,
                    tags TEXT,            -- JSON array
                    context TEXT,         -- JSON object
                    confidence REAL DEFAULT 0.8,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)

            # Patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    examples TEXT,        -- JSON array of session_ids
                    is_beneficial INTEGER,  -- NULL=unknown, 1=good, 0=bad
                    suggestions TEXT      -- JSON array
                )
            """)

            # Interactions table (for detailed logging)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    interaction_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    type TEXT NOT NULL,  -- question, answer, error, solution, edit
                    content TEXT NOT NULL,
                    file_path TEXT,
                    code_before TEXT,
                    code_after TEXT,
                    metadata TEXT,        -- JSON
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_learnings_category ON learnings(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_learnings_timestamp ON learnings(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id)")

            self.conn.commit()

    def create_session(self, session: AISession) -> str:
        """Create a new session"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sessions
                (session_id, started_at, ended_at, project_path, tool,
                 total_interactions, files_modified, git_commits, summary, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.started_at.isoformat(),
                session.ended_at.isoformat() if session.ended_at else None,
                session.project_path,
                session.tool,
                session.total_interactions,
                json.dumps(session.files_modified),
                json.dumps(session.git_commits),
                session.summary,
                session.status
            ))
            self.conn.commit()
            return session.session_id

    def add_learning(self, learning: Learning) -> str:
        """Record a learning/insight"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO learnings
                (learning_id, session_id, timestamp, category, title, description,
                 code_snippet, tags, context, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                learning.learning_id,
                learning.session_id,
                learning.timestamp.isoformat(),
                learning.category,
                learning.title,
                learning.description,
                learning.code_snippet,
                json.dumps(learning.tags),
                json.dumps(learning.context),
                learning.confidence
            ))
            self.conn.commit()
            return learning.learning_id

    def record_pattern(self, pattern: CodingPattern):
        """Record or update a coding pattern"""
        with self.lock:
            cursor = self.conn.cursor()

            # Check if pattern exists
            cursor.execute(
                "SELECT pattern_id, frequency FROM patterns WHERE pattern_id = ?",
                (pattern.pattern_id,)
            )
            existing = cursor.fetchone()

            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE patterns
                    SET frequency = frequency + 1,
                        last_seen = ?,
                        examples = ?,
                        is_beneficial = ?,
                        suggestions = ?
                    WHERE pattern_id = ?
                """, (
                    pattern.last_seen.isoformat(),
                    json.dumps(pattern.examples),
                    pattern.is_beneficial,
                    json.dumps(pattern.suggestions),
                    pattern.pattern_id
                ))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO patterns
                    (pattern_id, pattern_type, description, frequency, first_seen,
                     last_seen, examples, is_beneficial, suggestions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id,
                    pattern.pattern_type,
                    pattern.description,
                    pattern.frequency,
                    pattern.first_seen.isoformat(),
                    pattern.last_seen.isoformat(),
                    json.dumps(pattern.examples),
                    pattern.is_beneficial,
                    json.dumps(pattern.suggestions)
                ))

            self.conn.commit()

    def get_learnings(self,
                      category: Optional[str] = None,
                      limit: int = 50) -> List[Dict]:
        """Retrieve learnings, optionally filtered by category"""
        with self.lock:
            cursor = self.conn.cursor()

            if category:
                cursor.execute("""
                    SELECT * FROM learnings
                    WHERE category = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT * FROM learnings
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def get_patterns(self, pattern_type: Optional[str] = None) -> List[Dict]:
        """Get all patterns, optionally filtered by type"""
        with self.lock:
            cursor = self.conn.cursor()

            if pattern_type:
                cursor.execute("""
                    SELECT * FROM patterns
                    WHERE pattern_type = ?
                    ORDER BY frequency DESC
                """, (pattern_type,))
            else:
                cursor.execute("""
                    SELECT * FROM patterns
                    ORDER BY frequency DESC
                """)

            return [dict(row) for row in cursor.fetchall()]

    def search_similar_sessions(self,
                                 description: str,
                                 limit: int = 10) -> List[Dict]:
        """Search for sessions with similar problems/solutions"""
        with self.lock:
            cursor = self.conn.cursor()

            # Simple text search (can be enhanced with embeddings later)
            cursor.execute("""
                SELECT s.*,
                       GROUP_CONCAT(l.title, ', ') as learnings
                FROM sessions s
                LEFT JOIN learnings l ON s.session_id = l.session_id
                WHERE s.summary LIKE ? OR l.description LIKE ?
                GROUP BY s.session_id
                ORDER BY s.started_at DESC
                LIMIT ?
            """, (f"%{description}%", f"%{description}%", limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_session_stats(self) -> Dict[str, Any]:
        """Get overall statistics"""
        with self.lock:
            cursor = self.conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM learnings")
            total_learnings = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM patterns")
            total_patterns = cursor.fetchone()[0]

            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM learnings
                GROUP BY category
                ORDER BY count DESC
            """)
            learning_breakdown = dict(cursor.fetchall())

            return {
                "total_sessions": total_sessions,
                "total_learnings": total_learnings,
                "total_patterns": total_patterns,
                "learning_breakdown": learning_breakdown
            }


def generate_id(prefix: str, *components) -> str:
    """Generate a unique ID"""
    content = "-".join(str(c) for c in components)
    hash_part = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"{prefix}_{hash_part}"


if __name__ == "__main__":
    # Test the database
    db = AISessionDB()
    print("✅ AI Session Database initialized")
    print(f"📊 Stats: {db.get_session_stats()}")
