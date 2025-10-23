#!/usr/bin/env python3
"""
Setup RSS News Database Schema

Creates tables and indexes for external content sources.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
load_dotenv('/Users/yourox/AI-Workspace/.env')

def create_schema():
    """Create RSS news database schema"""

    conn_string = os.getenv('RAILWAY_DATABASE_URL')

    print("🔧 Creating RSS News Database Schema...")
    print(f"Connecting to Railway PostgreSQL...")

    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # Read SQL file
    with open('/Users/yourox/AI-Workspace/scripts/create_rss_schema.sql', 'r') as f:
        sql = f.read()

    try:
        # Execute schema creation
        cursor.execute(sql)
        conn.commit()

        print("✅ Schema created successfully!")

        # Verify tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE 'external%' OR table_name LIKE 'content%'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()

        print("\n📊 Created tables:")
        for table in tables:
            print(f"   ✓ {table[0]}")

        # Check source count
        cursor.execute("SELECT COUNT(*) FROM external_sources")
        source_count = cursor.fetchone()[0]
        print(f"\n📰 Loaded {source_count} RSS sources")

        if source_count > 0:
            cursor.execute("""
                SELECT source_id, name, priority, base_weight
                FROM external_sources
                ORDER BY base_weight DESC
            """)
            sources = cursor.fetchall()

            print("\n   Sources:")
            for source_id, name, priority, weight in sources:
                print(f"   • {name} ({priority}, weight: {weight})")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_schema()
