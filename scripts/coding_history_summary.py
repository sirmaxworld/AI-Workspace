#!/usr/bin/env python3
"""
Lightweight Coding History Summary System
Captures session summaries, not raw terminal output
Async processing with <1ms overhead
"""

import json
import sqlite3
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from queue import Queue, Empty
from dataclasses import dataclass, asdict
import hashlib
import time

# Configuration
DATA_DIR = Path("/Users/yourox/AI-Workspace/data/coding_history")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "summaries.db"
CONFIG_PATH = DATA_DIR / "config" / "summary_settings.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Global async queue for zero-blocking capture
capture_queue = Queue(maxsize=1000)

@dataclass
class SessionSummary:
    """Represents a coding session summary"""
    session_id: str
    timestamp: datetime
    prompt: str  # What user asked for
    actions: List[str]  # Key actions taken
    outcome: str  # Result/outcome
    errors: List[str]  # Any errors encountered
    tools_used: List[str]  # Tools/commands used
    files_modified: List[str]  # Files changed
    duration_seconds: float
    metadata: Dict[str, Any]

    def to_dict(self):
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d

class SummaryDB:
    """Lightweight database for session summaries"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with self.lock:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    prompt TEXT,
                    outcome TEXT,
                    duration_seconds REAL,
                    metadata TEXT
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    action_order INTEGER,
                    action TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    error TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    tool TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    file_path TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)

            # Create indexes for fast queries
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON sessions(timestamp)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_prompt ON sessions(prompt)")

            self.conn.commit()

    def save_summary(self, summary: SessionSummary):
        """Save a session summary to database"""
        with self.lock:
            # Insert main session
            self.conn.execute("""
                INSERT OR REPLACE INTO sessions
                (session_id, timestamp, prompt, outcome, duration_seconds, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                summary.session_id,
                summary.timestamp.isoformat(),
                summary.prompt,
                summary.outcome,
                summary.duration_seconds,
                json.dumps(summary.metadata)
            ))

            # Insert actions
            for i, action in enumerate(summary.actions):
                self.conn.execute("""
                    INSERT INTO actions (session_id, action_order, action)
                    VALUES (?, ?, ?)
                """, (summary.session_id, i, action))

            # Insert errors
            for error in summary.errors:
                self.conn.execute("""
                    INSERT INTO errors (session_id, error)
                    VALUES (?, ?)
                """, (summary.session_id, error))

            # Insert tools
            for tool in summary.tools_used:
                self.conn.execute("""
                    INSERT INTO tools (session_id, tool)
                    VALUES (?, ?)
                """, (summary.session_id, tool))

            # Insert files
            for file_path in summary.files_modified:
                self.conn.execute("""
                    INSERT INTO files (session_id, file_path)
                    VALUES (?, ?)
                """, (summary.session_id, file_path))

            self.conn.commit()

    def search_sessions(
        self,
        query: Optional[str] = None,
        start_time: Optional[datetime] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Search for session summaries"""
        with self.lock:
            sql = """
                SELECT s.*,
                       GROUP_CONCAT(DISTINCT a.action) as actions,
                       GROUP_CONCAT(DISTINCT e.error) as errors,
                       GROUP_CONCAT(DISTINCT t.tool) as tools,
                       GROUP_CONCAT(DISTINCT f.file_path) as files
                FROM sessions s
                LEFT JOIN actions a ON s.session_id = a.session_id
                LEFT JOIN errors e ON s.session_id = e.session_id
                LEFT JOIN tools t ON s.session_id = t.session_id
                LEFT JOIN files f ON s.session_id = f.session_id
                WHERE 1=1
            """
            params = []

            if query:
                sql += " AND (s.prompt LIKE ? OR s.outcome LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])

            if start_time:
                sql += " AND s.timestamp >= ?"
                params.append(start_time.isoformat())

            sql += " GROUP BY s.session_id ORDER BY s.timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = self.conn.execute(sql, params)
            columns = [d[0] for d in cursor.description]

            results = []
            for row in cursor:
                result = dict(zip(columns, row))
                # Parse concatenated fields
                result['actions'] = result['actions'].split(',') if result['actions'] else []
                result['errors'] = result['errors'].split(',') if result['errors'] else []
                result['tools'] = result['tools'].split(',') if result['tools'] else []
                result['files'] = result['files'].split(',') if result['files'] else []
                results.append(result)

            return results

    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.lock:
            cursor = self.conn.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]

            cursor = self.conn.execute("""
                SELECT COUNT(*) FROM sessions
                WHERE datetime(timestamp) >= datetime('now', '-1 day')
            """)
            recent_sessions = cursor.fetchone()[0]

            cursor = self.conn.execute("SELECT COUNT(DISTINCT tool) FROM tools")
            unique_tools = cursor.fetchone()[0]

            cursor = self.conn.execute("SELECT COUNT(*) FROM errors")
            total_errors = cursor.fetchone()[0]

            return {
                'total_sessions': total_sessions,
                'recent_sessions_24h': recent_sessions,
                'unique_tools': unique_tools,
                'total_errors': total_errors,
                'db_size_bytes': DB_PATH.stat().st_size if DB_PATH.exists() else 0
            }

class AsyncSummaryProcessor:
    """Background processor for creating summaries"""

    def __init__(self):
        self.db = SummaryDB()
        self.running = False
        self.thread = None
        self.current_session = None
        self.session_start = None
        self.session_commands = []

    def start(self):
        """Start background processing thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._process_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop background processing"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _process_loop(self):
        """Main processing loop"""
        batch = []
        last_process = time.time()

        while self.running:
            try:
                # Collect items for up to 10 seconds or 20 items
                item = capture_queue.get(timeout=1)
                batch.append(item)

                if len(batch) >= 20 or (time.time() - last_process) > 10:
                    self._process_batch(batch)
                    batch = []
                    last_process = time.time()

            except Empty:
                # Process any remaining items
                if batch:
                    self._process_batch(batch)
                    batch = []
                    last_process = time.time()

    def _process_batch(self, batch: List[Dict]):
        """Process a batch of captured events into a summary"""
        if not batch:
            return

        # Group by logical session (commands within 5 minutes of each other)
        sessions = []
        current = []
        last_time = None

        for item in batch:
            item_time = item.get('time', time.time())
            if last_time and (item_time - last_time) > 300:  # 5 minute gap
                if current:
                    sessions.append(current)
                    current = []
            current.append(item)
            last_time = item_time

        if current:
            sessions.append(current)

        # Create summary for each session
        for session_items in sessions:
            summary = self._create_summary(session_items)
            if summary:
                self.db.save_summary(summary)

    def _create_summary(self, items: List[Dict]) -> Optional[SessionSummary]:
        """Create a summary from a group of commands"""
        if not items:
            return None

        # Generate session ID
        session_content = json.dumps(items, sort_keys=True)
        session_id = hashlib.sha256(session_content.encode()).hexdigest()[:12]

        # Extract information
        start_time = datetime.fromtimestamp(items[0].get('time', time.time()))
        end_time = datetime.fromtimestamp(items[-1].get('time', time.time()))
        duration = (end_time - start_time).total_seconds()

        # Analyze commands and outcomes
        commands = [item.get('cmd', '') for item in items if item.get('cmd')]
        errors = [item.get('error', '') for item in items if item.get('error')]
        tools = list(set(cmd.split()[0] for cmd in commands if cmd))

        # Infer prompt and outcome (simplified - can be enhanced)
        prompt = self._infer_prompt(commands)
        outcome = self._infer_outcome(items)
        actions = self._extract_actions(commands)
        files = self._extract_files(commands)

        return SessionSummary(
            session_id=session_id,
            timestamp=start_time,
            prompt=prompt,
            actions=actions[:10],  # Limit to 10 key actions
            outcome=outcome,
            errors=errors[:5],  # Limit to 5 errors
            tools_used=tools[:10],  # Limit to 10 tools
            files_modified=files[:10],  # Limit to 10 files
            duration_seconds=duration,
            metadata={'item_count': len(items)}
        )

    def _infer_prompt(self, commands: List[str]) -> str:
        """Infer what the user was trying to do"""
        # Simple heuristics - can be enhanced
        if any('npm install' in cmd for cmd in commands):
            return "Installing dependencies"
        elif any('git' in cmd for cmd in commands):
            return "Git operations"
        elif any('python' in cmd or 'py' in cmd for cmd in commands):
            return "Python development"
        elif any('test' in cmd for cmd in commands):
            return "Running tests"
        else:
            return "General development"

    def _infer_outcome(self, items: List[Dict]) -> str:
        """Infer the outcome of the session"""
        errors = [item for item in items if item.get('exit') != 0]
        if errors:
            return f"Completed with {len(errors)} errors"
        else:
            return "Completed successfully"

    def _extract_actions(self, commands: List[str]) -> List[str]:
        """Extract key actions from commands"""
        actions = []
        for cmd in commands:
            if 'install' in cmd:
                actions.append(f"Installed packages: {cmd}")
            elif 'git commit' in cmd:
                actions.append(f"Committed changes")
            elif 'test' in cmd:
                actions.append("Ran tests")
            elif cmd and len(actions) < 10:
                actions.append(cmd[:100])  # Truncate long commands
        return actions

    def _extract_files(self, commands: List[str]) -> List[str]:
        """Extract file paths from commands"""
        files = []
        for cmd in commands:
            parts = cmd.split()
            for part in parts:
                if '/' in part and '.' in part:
                    files.append(part)
        return list(set(files))[:10]

# Global processor instance
processor = AsyncSummaryProcessor()

def queue_event(command: str, exit_code: int = 0, error: str = None):
    """
    Ultra-lightweight function to queue an event
    Called from shell hooks - must be <1ms
    """
    try:
        capture_queue.put_nowait({
            'time': time.time(),
            'cmd': command[:500],  # Truncate for safety
            'exit': exit_code,
            'error': error[:200] if error else None
        })
    except:
        pass  # Never block the shell

def start_processor():
    """Start the background processor"""
    processor.start()

def stop_processor():
    """Stop the background processor"""
    processor.stop()

def get_queue_stats():
    """Get queue statistics"""
    return {
        'queue_size': capture_queue.qsize(),
        'queue_maxsize': capture_queue.maxsize,
        'processor_running': processor.running
    }

def clear_queue():
    """Clear the queue (for troubleshooting)"""
    while not capture_queue.empty():
        try:
            capture_queue.get_nowait()
        except Empty:
            break

# Auto-start processor when module is imported
start_processor()

if __name__ == "__main__":
    # Test the system
    print("Testing Coding History Summary System...")

    # Queue some test events
    queue_event("npm install react", 0)
    queue_event("npm test", 1, "Test failed")
    queue_event("git commit -m 'Fix tests'", 0)

    print(f"Queue stats: {get_queue_stats()}")

    # Wait for processing
    time.sleep(2)

    # Query results
    db = SummaryDB()
    stats = db.get_stats()
    print(f"Database stats: {stats}")

    sessions = db.search_sessions(limit=5)
    print(f"Recent sessions: {len(sessions)}")
    for session in sessions:
        print(f"  - {session['timestamp']}: {session['prompt']} → {session['outcome']}")

    print("✅ Test complete!")