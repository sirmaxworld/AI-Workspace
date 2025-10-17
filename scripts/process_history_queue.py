#!/usr/bin/env python3
"""
Process coding history queue independently
Runs in background, no Claude Desktop dependency
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

DB_PATH = Path.home() / "AI-Workspace" / ".coding_history.db"
QUEUE_FILE = Path.home() / ".coding_history_queue.txt"

def init_database():
    """Initialize database schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            command TEXT NOT NULL,
            prompt TEXT,
            outcome TEXT,
            duration_seconds REAL,
            exit_code INTEGER,
            metadata TEXT
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp
        ON sessions(timestamp DESC)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_command
        ON sessions(command)
    ''')

    conn.commit()
    conn.close()

def process_queue():
    """Process queued commands from file"""
    if not QUEUE_FILE.exists():
        return 0

    # Read queue
    try:
        content = QUEUE_FILE.read_text().strip()
        if not content:
            return 0

        commands = [line for line in content.split('\n') if line.strip()]

        # Clear queue immediately (atomic)
        QUEUE_FILE.unlink()

    except Exception as e:
        print(f"Error reading queue: {e}", file=sys.stderr)
        return 0

    # Process commands
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    processed = 0
    for cmd in commands:
        if not cmd.strip():
            continue

        try:
            # Simple summary
            prompt = f"Running: {cmd[:60]}"
            if len(cmd) > 60:
                prompt += "..."

            metadata = {
                "captured_by": "terminal_independent",
                "full_command": cmd
            }

            cursor.execute('''
                INSERT INTO sessions
                (timestamp, command, prompt, outcome, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                cmd[:200],  # Limit command length
                prompt,
                "Captured",
                json.dumps(metadata)
            ))

            processed += 1

        except Exception as e:
            print(f"Error processing command: {e}", file=sys.stderr)
            continue

    conn.commit()
    conn.close()

    return processed

if __name__ == "__main__":
    try:
        count = process_queue()
        if count > 0:
            print(f"Processed {count} commands")
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)