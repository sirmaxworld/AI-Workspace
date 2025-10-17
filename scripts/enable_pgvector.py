#!/usr/bin/env python3
"""
Enable pgvector extension on Railway PostgreSQL
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def enable_pgvector():
    conn_string = os.getenv('RAILWAY_DATABASE_URL')
    print(f"Connecting to Railway PostgreSQL...")

    try:
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        cursor = conn.cursor()

        # Enable pgvector extension
        print("Enabling pgvector extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅ pgvector extension enabled")

        # Verify installation
        cursor.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
        result = cursor.fetchone()

        if result:
            print(f"✅ pgvector {result[1]} is active")
        else:
            print("❌ pgvector not found after installation")

        # Test vector operations
        print("\nTesting vector operations...")
        cursor.execute("SELECT '[1,2,3]'::vector;")
        test_vector = cursor.fetchone()[0]
        print(f"✅ Vector test successful: {test_vector}")

        cursor.close()
        conn.close()

        print("\n🎉 pgvector is ready for use!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    enable_pgvector()
