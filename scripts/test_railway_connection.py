#!/usr/bin/env python3
"""
Test Railway PostgreSQL Connection
"""
import os
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

# Test with psycopg2 (if available) or psycopg
try:
    import psycopg2
    print("Using psycopg2...")

    # Build connection string
    conn_string = os.getenv('RAILWAY_DATABASE_URL')
    print(f"Connecting to: {conn_string[:30]}...{conn_string[-20:]}")

    # Connect
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"\n✅ Connection successful!")
    print(f"PostgreSQL version: {version[:80]}...")

    # Check for pgvector extension
    cursor.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector';")
    pgvector_available = cursor.fetchone()

    if pgvector_available:
        print(f"\n✅ pgvector extension available: {pgvector_available[1]}")
    else:
        print(f"\n⚠️ pgvector extension not found")

    cursor.close()
    conn.close()

except ImportError:
    print("psycopg2 not found, trying psycopg3...")
    try:
        import psycopg

        conn_string = os.getenv('RAILWAY_DATABASE_URL')
        print(f"Connecting to: {conn_string[:30]}...{conn_string[-20:]}")

        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"\n✅ Connection successful!")
                print(f"PostgreSQL version: {version[:80]}...")

                # Check for pgvector extension
                cursor.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector';")
                pgvector_available = cursor.fetchone()

                if pgvector_available:
                    print(f"\n✅ pgvector extension available: {pgvector_available[1]}")
                else:
                    print(f"\n⚠️ pgvector extension not found")

    except ImportError as e:
        print(f"\n❌ No PostgreSQL driver found. Please install:")
        print("   pip3 install psycopg2-binary")
        print("   OR")
        print("   pip3 install psycopg")
        exit(1)
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    exit(1)
