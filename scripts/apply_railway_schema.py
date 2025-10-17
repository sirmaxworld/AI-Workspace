#!/usr/bin/env python3
"""
Apply Railway PostgreSQL Schema
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def apply_schema():
    conn_string = os.getenv('RAILWAY_DATABASE_URL')
    schema_file = '/Users/yourox/AI-Workspace/config/railway_schema.sql'

    print("Reading schema file...")
    with open(schema_file, 'r') as f:
        schema_sql = f.read()

    print("Connecting to Railway PostgreSQL...")
    try:
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        cursor = conn.cursor()

        print("Applying schema...")
        cursor.execute(schema_sql)

        print("\n✅ Schema applied successfully!")

        # Verify tables created
        print("\n📊 Verifying tables...")
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename NOT LIKE 'mem0_%'
            ORDER BY tablename;
        """)
        tables = cursor.fetchall()

        print(f"\n✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")

        # Verify indexes
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND indexname LIKE 'idx_%';
        """)
        index_count = cursor.fetchone()[0]
        print(f"\n✅ Created {index_count} indexes")

        # Verify vector extension
        cursor.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
        vector_info = cursor.fetchone()
        print(f"\n✅ pgvector {vector_info[1]} enabled")

        cursor.close()
        conn.close()

        print("\n🎉 Railway schema is ready!")
        return True

    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    apply_schema()
