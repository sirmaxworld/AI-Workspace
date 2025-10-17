#!/usr/bin/env python3
"""
Standalone ch_stats command - safe version
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, '/Users/yourox/AI-Workspace/scripts')

try:
    from coding_history_core import CodingHistoryDB
    from coding_history_capture_async import get_capture_manager
    from datetime import datetime, timedelta
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure coding_history_core.py exists")
    sys.exit(1)

def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f'{bytes:.1f}{unit}'
        bytes /= 1024.0
    return f'{bytes:.1f}TB'

def main():
    try:
        db = CodingHistoryDB()
        capture = get_capture_manager()

        # Get capture status
        capture_stats = capture.get_stats()

        # Calculate storage
        data_dir = Path('/Users/yourox/AI-Workspace/data/coding_history')
        db_file = data_dir / 'sessions.db'
        outputs_dir = data_dir / 'outputs'

        # Database size
        db_size = db_file.stat().st_size if db_file.exists() else 0

        # Compressed files size
        compressed_size = 0
        file_count = 0
        if outputs_dir.exists():
            for file in outputs_dir.rglob('*.zst'):
                compressed_size += file.stat().st_size
                file_count += 1

        with db.lock:
            cursor = db.conn.cursor()

            # Get session count
            cursor.execute('SELECT COUNT(*) FROM sessions')
            session_count = cursor.fetchone()[0]

            # Get active sessions
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'active'")
            active_sessions = cursor.fetchone()[0]

            # Get chunk counts
            cursor.execute('SELECT COUNT(*) FROM output_chunks')
            total_chunks = cursor.fetchone()[0]

            # Get original size
            cursor.execute('SELECT SUM(content_length) FROM output_chunks')
            uncompressed_size = cursor.fetchone()[0] or 0

            # Get counts by type
            cursor.execute("""
                SELECT output_type, COUNT(*)
                FROM output_chunks
                GROUP BY output_type
            """)
            type_counts = dict(cursor.fetchall())

            # Get time-based stats
            today = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()

            cursor.execute('SELECT COUNT(*) FROM output_chunks WHERE timestamp >= ?', (today,))
            today_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM output_chunks WHERE timestamp >= ?', (week_ago,))
            week_count = cursor.fetchone()[0]

            # Get top projects
            cursor.execute("""
                SELECT project_path, COUNT(*) as count
                FROM sessions
                GROUP BY project_path
                ORDER BY count DESC
                LIMIT 3
            """)
            top_projects = cursor.fetchall()

        # Calculate compression ratio
        compression_ratio = 0
        if uncompressed_size > 0:
            compression_ratio = (1 - (compressed_size / uncompressed_size)) * 100

        print("📊 CODING HISTORY DATABASE METRICS")
        print("==================================")
        print(f'\n💾 STORAGE:')
        print(f'  Database: {format_size(db_size)}')
        print(f'  Compressed Files: {format_size(compressed_size)} ({file_count} files)')
        print(f'  Total Used: {format_size(db_size + compressed_size)}')
        print(f'  Original Size: {format_size(uncompressed_size)}')
        print(f'  Compression: {compression_ratio:.1f}% saved')

        print(f'\n📁 SESSIONS:')
        print(f'  Total Sessions: {session_count}')
        print(f'  Active Sessions: {active_sessions}')
        print(f'  Total Entries: {total_chunks:,}')
        if type_counts:
            for type_name, count in type_counts.items():
                print(f'    {type_name}: {count:,}')

        print(f'\n📈 ACTIVITY:')
        print(f'  Today: {today_count:,} entries')
        print(f'  Last 7 Days: {week_count:,} entries')
        if week_count > 0:
            print(f'  Average/Day: {week_count // 7:,} entries')

        print(f'\n🎯 CAPTURE STATUS:')
        status = '✅ ON' if capture_stats['capture_enabled'] else '❌ OFF'
        print(f'  Status: {status}')
        print(f'  Buffered: {capture_stats["queue_size"]} items')
        print(f'  Captured: {capture_stats["captured"]:,}')
        print(f'  Deduplicated: {capture_stats["deduplicated"]:,}')

        if top_projects:
            print(f'\n📍 TOP PROJECTS:')
            for proj, count in top_projects:
                proj_short = proj.replace('/Users/yourox/', '~/')
                print(f'  {proj_short}: {count} sessions')

        print("\nCommands: ch_details (full) | ch_monitor (live) | ch_toggle (on/off)")

        db.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()