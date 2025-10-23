#!/usr/bin/env python3
"""
Add Vector Columns to Intelligence Tables
Prepares tables for semantic embeddings
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def main():
    print("\n" + "="*80)
    print(" "*20 + "ADD VECTOR COLUMNS TO TABLES")
    print("="*80)

    conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
    conn.autocommit = True
    cursor = conn.cursor()

    # Tables to add embeddings to
    tables = [
        ('coding_patterns', 'Pattern descriptions and code examples'),
        ('coding_rules', 'Rule descriptions and best practices'),
        ('oss_commercial_repos', 'Repository descriptions and metadata'),
        ('mcp_servers', 'Server descriptions and capabilities')
    ]

    print("\n📊 Adding vector columns to tables...")

    for table_name, description in tables:
        print(f"\n🔧 Processing: {table_name}")
        print(f"   Purpose: {description}")

        # Check if column already exists
        cursor.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}' AND column_name = 'embedding';
        """)

        if cursor.fetchone():
            print(f"   ✅ Vector column already exists")
        else:
            try:
                # Add vector column (1536 dimensions for text-embedding-3-small)
                cursor.execute(f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN embedding vector(1536);
                """)
                print(f"   ✅ Added vector(1536) column")
            except Exception as e:
                print(f"   ❌ Error adding column: {e}")
                continue

        # Create HNSW index for fast similarity search
        index_name = f"{table_name}_embedding_idx"

        # Check if index exists
        cursor.execute(f"""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = '{table_name}' AND indexname = '{index_name}';
        """)

        if cursor.fetchone():
            print(f"   ✅ HNSW index already exists")
        else:
            try:
                print(f"   🔨 Creating HNSW index (this may take a moment)...")
                cursor.execute(f"""
                    CREATE INDEX {index_name}
                    ON {table_name}
                    USING hnsw (embedding vector_cosine_ops);
                """)
                print(f"   ✅ HNSW index created for fast similarity search")
            except Exception as e:
                print(f"   ⚠️  Index creation skipped (will create after embeddings): {e}")

    # Verify setup
    print("\n" + "="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)

    for table_name, _ in tables:
        # Check column exists
        cursor.execute(f"""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_name = '{table_name}' AND column_name = 'embedding';
        """)
        has_column = cursor.fetchone()[0] > 0

        # Check row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]

        # Check embeddings count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE embedding IS NOT NULL;")
        embedding_count = cursor.fetchone()[0]

        status = "✅" if has_column else "❌"
        print(f"\n{status} {table_name}")
        print(f"   Rows: {row_count:,}")
        print(f"   Embeddings: {embedding_count:,} ({embedding_count/row_count*100:.1f}%)" if row_count > 0 else "   Embeddings: 0")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("✅ VECTOR COLUMNS SETUP COMPLETE")
    print("="*80)
    print("\nNext step: Generate embeddings with scripts/generate_embeddings.py")
    print()

    return 0

if __name__ == "__main__":
    exit(main())
