#!/usr/bin/env python3
"""
Install pgvector Extension
Enables vector similarity search in Railway PostgreSQL
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def main():
    print("\n" + "="*80)
    print(" "*25 + "PGVECTOR INSTALLATION")
    print("="*80)

    # Connect to database
    print("\n🔌 Connecting to Railway PostgreSQL...")
    conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
    conn.autocommit = True
    cursor = conn.cursor()

    # Check if extension exists
    print("\n🔍 Checking for existing pgvector extension...")
    cursor.execute("""
        SELECT * FROM pg_extension WHERE extname = 'vector';
    """)

    existing = cursor.fetchone()

    if existing:
        print("✅ pgvector extension already installed!")
    else:
        print("📦 Installing pgvector extension...")
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ pgvector extension installed successfully!")
        except Exception as e:
            print(f"❌ Error installing pgvector: {e}")
            print("\n⚠️  Note: Railway PostgreSQL might not have pgvector pre-installed.")
            print("   You may need to:")
            print("   1. Use Railway's pgvector plugin")
            print("   2. Or upgrade to a plan with pgvector support")
            cursor.close()
            conn.close()
            return 1

    # Verify installation
    print("\n🔍 Verifying installation...")
    cursor.execute("""
        SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
    """)

    result = cursor.fetchone()
    if result:
        print(f"✅ Extension: {result[0]} (version {result[1]})")

    # Test vector functionality
    print("\n🧪 Testing vector operations...")
    try:
        cursor.execute("SELECT '[1,2,3]'::vector;")
        print("✅ Vector type working!")

        cursor.execute("SELECT '[1,2,3]'::vector <-> '[4,5,6]'::vector;")
        distance = cursor.fetchone()[0]
        print(f"✅ Vector distance operation working! (test distance: {distance:.2f})")
    except Exception as e:
        print(f"❌ Vector operations failed: {e}")
        cursor.close()
        conn.close()
        return 1

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("✅ PGVECTOR INSTALLATION COMPLETE")
    print("="*80 + "\n")

    return 0

if __name__ == "__main__":
    exit(main())
