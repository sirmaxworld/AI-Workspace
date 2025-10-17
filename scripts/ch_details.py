#!/usr/bin/env python3
"""
Detailed Coding History Statistics
Shows comprehensive information about captured history
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from coding_history_core import CodingHistoryDB, CompressionManager
from coding_history_capture_async import get_capture_manager


def format_size(bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024.0
    return f"{bytes:.1f}TB"


def main():
    db = CodingHistoryDB()
    compression = CompressionManager()
    capture = get_capture_manager()

    print("\n" + "=" * 60)
    print("📊 CODING HISTORY DETAILED STATISTICS")
    print("=" * 60)

    # Get capture status
    capture_stats = capture.get_stats()
    print(f"\n🔴 Capture Status: {'✅ ENABLED' if capture_stats['capture_enabled'] else '❌ DISABLED'}")
    print(f"Queue: {capture_stats['queue_size']}/1000")
    print(f"Session: {capture_stats.get('session_id', 'None')[:8] if capture_stats.get('session_id') else 'None'}")

    with db.lock:
        cursor = db.conn.cursor()

        # Overall statistics
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM output_chunks")
        total_chunks = cursor.fetchone()[0]

        cursor.execute("""
            SELECT
                COUNT(CASE WHEN output_type = 'command' THEN 1 END) as commands,
                COUNT(CASE WHEN output_type = 'output' THEN 1 END) as outputs,
                COUNT(CASE WHEN output_type = 'error' THEN 1 END) as errors,
                COUNT(CASE WHEN output_type = 'info' THEN 1 END) as info
            FROM output_chunks
        """)
        type_counts = cursor.fetchone()

        print(f"\n📈 DATABASE TOTALS:")
        print(f"  Sessions: {total_sessions:,}")
        print(f"  Total Entries: {total_chunks:,}")
        print(f"    Commands: {type_counts[0]:,}")
        print(f"    Outputs: {type_counts[1]:,}")
        print(f"    Errors: {type_counts[2]:,}")
        print(f"    Info: {type_counts[3]:,}")

        # Time-based statistics
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0).isoformat()
        week_ago = (now - timedelta(days=7)).isoformat()
        hour_ago = (now - timedelta(hours=1)).isoformat()

        cursor.execute("SELECT COUNT(*) FROM output_chunks WHERE timestamp >= ?", (today_start,))
        today_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM output_chunks WHERE timestamp >= ?", (week_ago,))
        week_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM output_chunks WHERE timestamp >= ?", (hour_ago,))
        hour_count = cursor.fetchone()[0]

        print(f"\n⏰ TIME-BASED ACTIVITY:")
        print(f"  Last Hour: {hour_count:,} entries")
        print(f"  Today: {today_count:,} entries")
        print(f"  Last 7 Days: {week_count:,} entries")
        print(f"  Average/Day: {week_count // 7:,} entries")

        # Project statistics
        cursor.execute("""
            SELECT
                s.project_path,
                COUNT(DISTINCT s.session_id) as sessions,
                COUNT(c.chunk_id) as chunks,
                MAX(c.timestamp) as last_activity
            FROM sessions s
            LEFT JOIN output_chunks c ON s.session_id = c.session_id
            GROUP BY s.project_path
            ORDER BY chunks DESC
            LIMIT 5
        """)
        projects = cursor.fetchall()

        if projects:
            print(f"\n📁 TOP PROJECTS:")
            for proj in projects:
                path = proj[0].replace('/Users/yourox/', '~/')
                last = datetime.fromisoformat(proj[3]).strftime('%Y-%m-%d %H:%M')
                print(f"  {path}")
                print(f"    {proj[2]:,} entries | {proj[1]} sessions | Last: {last}")

        # Tool usage
        cursor.execute("""
            SELECT tool_used, COUNT(*) as count
            FROM output_chunks
            WHERE tool_used IS NOT NULL
            GROUP BY tool_used
            ORDER BY count DESC
            LIMIT 5
        """)
        tools = cursor.fetchall()

        if tools:
            print(f"\n🔧 TOP TOOLS:")
            for tool, count in tools:
                print(f"  {tool}: {count:,} uses")

        # Recent entries with preview
        cursor.execute("""
            SELECT
                c.timestamp,
                c.output_type,
                c.tool_used,
                c.content_length,
                s.project_path,
                c.compressed_path,
                c.exit_code
            FROM output_chunks c
            JOIN sessions s ON c.session_id = s.session_id
            ORDER BY c.timestamp DESC
            LIMIT 10
        """)
        recent = cursor.fetchall()

        if recent:
            print(f"\n📜 LAST 10 ENTRIES:")
            print("-" * 60)
            for row in recent:
                timestamp = datetime.fromisoformat(row[0]).strftime('%Y-%m-%d %H:%M:%S')
                output_type = row[1].upper()
                tool = row[2] or 'shell'
                size = row[3]
                project = row[4].replace('/Users/yourox/', '~/')
                exit_code = row[6]

                print(f"{timestamp} [{output_type:7}] {tool:10}")
                print(f"  Size: {size:,} bytes | Project: {project}")

                # Try to show preview for small entries
                if size < 200 and row[5]:
                    try:
                        content = compression.decompress_chunk(row[5])
                        preview = content[:100].replace('\n', ' ')
                        if len(preview) > 80:
                            preview = preview[:80] + "..."
                        print(f"  Preview: {preview}")
                    except:
                        pass

                if exit_code is not None and exit_code != 0:
                    print(f"  Exit Code: {exit_code} ⚠️")
                print("-" * 60)

        # Storage statistics
        cursor.execute("SELECT SUM(content_length) FROM output_chunks")
        total_uncompressed = cursor.fetchone()[0] or 0

    # Calculate storage
    data_dir = Path("/Users/yourox/AI-Workspace/data/coding_history")
    outputs_dir = data_dir / "outputs"
    db_file = data_dir / "sessions.db"

    compressed_size = 0
    if outputs_dir.exists():
        for file in outputs_dir.rglob("*.zst"):
            compressed_size += file.stat().st_size

    db_size = db_file.stat().st_size if db_file.exists() else 0

    print(f"\n💾 STORAGE:")
    print(f"  Original Size: {format_size(total_uncompressed)}")
    print(f"  Compressed: {format_size(compressed_size)}")
    print(f"  Database: {format_size(db_size)}")
    print(f"  Total Used: {format_size(compressed_size + db_size)}")

    if total_uncompressed > 0:
        compression_ratio = (1 - (compressed_size / total_uncompressed)) * 100
        print(f"  Compression: {compression_ratio:.1f}% saved")

    print("\n" + "=" * 60)
    print("Use 'ch_toggle' to control | 'python3 ch_details.py' for this view")
    print("=" * 60 + "\n")

    db.close()


if __name__ == "__main__":
    main()