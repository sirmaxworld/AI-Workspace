#!/usr/bin/env python3
"""
Generate Embeddings Using Local Sentence Transformers
FREE, fast, and private - no external API calls!
"""

import os
import time
import psycopg2
import psycopg2.extras
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv('/Users/yourox/AI-Workspace/.env')

# Load model once (cached after first load)
print("\n📦 Loading sentence-transformers model...")
MODEL = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded! (all-MiniLM-L6-v2, 384 dimensions)")

BATCH_SIZE = 50  # Process in batches for efficiency

def get_db_connection():
    """Get Railway PostgreSQL connection"""
    return psycopg2.connect(
        os.getenv('RAILWAY_DATABASE_URL'),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def embed_table(table_name: str, text_columns: List[str], desc: str):
    """Generate embeddings for a table"""
    print(f"\n{'='*80}")
    print(f"📦 EMBEDDING {desc}")
    print(f"{'='*80}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get rows without embeddings
    cursor.execute(f"""
        SELECT id, {', '.join(text_columns)}
        FROM {table_name}
        WHERE embedding IS NULL
        ORDER BY id;
    """)

    rows = cursor.fetchall()
    total = len(rows)

    if total == 0:
        print(f"\n✅ All rows already have embeddings!")
        cursor.close()
        conn.close()
        return 0

    print(f"\n📊 Found {total:,} rows to embed")

    embedded_count = 0
    start_time = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]

        # Create text representations
        texts = []
        for row in batch:
            # Combine text columns
            parts = [str(row[col]) if row[col] else '' for col in text_columns]
            text = ' | '.join([p for p in parts if p])
            texts.append(text)

        # Generate embeddings (fast!)
        embeddings = MODEL.encode(texts, show_progress_bar=False)

        # Update database
        for j, row in enumerate(batch):
            try:
                embedding_list = embeddings[j].tolist()
                cursor.execute(f"""
                    UPDATE {table_name}
                    SET embedding = %s
                    WHERE id = %s;
                """, (embedding_list, row['id']))
                embedded_count += 1
            except Exception as e:
                print(f"   ❌ Error storing embedding for row {row['id']}: {e}")

        conn.commit()

        # Progress update
        progress = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start_time
        rate = progress / elapsed if elapsed > 0 else 0
        eta = (total - progress) / rate if rate > 0 else 0

        print(f"   Progress: {progress:,}/{total:,} ({progress/total*100:.1f}%) | "
              f"Rate: {rate:.1f}/s | ETA: {eta:.0f}s")

    elapsed = time.time() - start_time
    print(f"\n✅ Embedded {embedded_count:,} rows in {elapsed:.1f}s")
    print(f"   Average: {elapsed/embedded_count:.3f}s per row")

    cursor.close()
    conn.close()
    return embedded_count

def main():
    """Main embedding generation process"""
    print("\n" + "="*80)
    print(" "*15 + "LOCAL EMBEDDING GENERATION (FREE!)")
    print("="*80)

    start_time = time.time()

    # Embed all tables
    tables_config = [
        {
            'table': 'coding_patterns',
            'columns': ['pattern_name', 'description', 'language', 'pattern_type'],
            'desc': 'CODING PATTERNS'
        },
        {
            'table': 'coding_rules',
            'columns': ['rule_title', 'rule_description', 'rule_category'],
            'desc': 'CODING RULES'
        },
        {
            'table': 'oss_commercial_repos',
            'columns': ['repo_full_name', 'description', 'primary_language', 'license_type'],
            'desc': 'OSS COMMERCIAL REPOS'
        },
        {
            'table': 'mcp_servers',
            'columns': ['server_name', 'description', 'category'],
            'desc': 'MCP SERVERS (first 1000)'
        }
    ]

    total_embedded = 0

    for config in tables_config:
        try:
            count = embed_table(config['table'], config['columns'], config['desc'])
            total_embedded += count
        except Exception as e:
            print(f"\n❌ Error embedding {config['table']}: {e}")
            continue

    total_time = time.time() - start_time

    # Summary
    print(f"\n{'='*80}")
    print("📊 EMBEDDING GENERATION SUMMARY")
    print(f"{'='*80}")

    conn = get_db_connection()
    cursor = conn.cursor()

    tables = [
        ('coding_patterns', 'Patterns'),
        ('coding_rules', 'Rules'),
        ('oss_commercial_repos', 'OSS Repos'),
        ('mcp_servers', 'MCP Servers')
    ]

    for table_name, label in tables:
        cursor.execute(f"""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE embedding IS NOT NULL) as embedded
            FROM {table_name};
        """)

        result = cursor.fetchone()
        total = result['total']
        embedded = result['embedded']
        percentage = (embedded / total * 100) if total > 0 else 0

        print(f"\n✅ {label:20} {embedded:5,} / {total:5,} ({percentage:5.1f}%)")

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")
    print(f"✅ TOTAL EMBEDDINGS GENERATED: {total_embedded:,}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"💰 Cost: $0.00 (FREE!)")
    print(f"🔒 Privacy: All local, no external APIs")
    print(f"{'='*80}\n")

    return 0

if __name__ == "__main__":
    exit(main())
