#!/usr/bin/env python3
"""
Generate Embeddings for Intelligence Data
Creates semantic embeddings using OpenAI API for vector similarity search
"""

import os
import time
import psycopg2
import psycopg2.extras
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv('/Users/yourox/AI-Workspace/.env')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Embedding model configuration
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
BATCH_SIZE = 100  # OpenAI allows batching

def get_db_connection():
    """Get Railway PostgreSQL connection"""
    return psycopg2.connect(
        os.getenv('RAILWAY_DATABASE_URL'),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text using OpenAI API"""
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"   ❌ Error generating embedding: {e}")
        return None

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts in one API call"""
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"   ❌ Error generating batch embeddings: {e}")
        return [None] * len(texts)

def embed_coding_patterns():
    """Generate embeddings for coding patterns"""
    print("\n" + "="*80)
    print("📦 EMBEDDING CODING PATTERNS")
    print("="*80)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get patterns without embeddings
    cursor.execute("""
        SELECT id, pattern_name, description, language, pattern_type
        FROM coding_patterns
        WHERE embedding IS NULL
        ORDER BY id;
    """)

    patterns = cursor.fetchall()
    total = len(patterns)

    if total == 0:
        print("\n✅ All patterns already have embeddings!")
        cursor.close()
        conn.close()
        return 0

    print(f"\n📊 Found {total} patterns to embed")

    embedded_count = 0
    start_time = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch = patterns[i:i + BATCH_SIZE]

        # Create rich text representations
        texts = []
        for p in batch:
            text = f"{p['pattern_name']} ({p['language']}, {p['pattern_type']}): {p['description']}"
            texts.append(text)

        # Generate embeddings
        embeddings = generate_embeddings_batch(texts)

        # Update database
        for j, pattern in enumerate(batch):
            if embeddings[j]:
                try:
                    cursor.execute("""
                        UPDATE coding_patterns
                        SET embedding = %s
                        WHERE id = %s;
                    """, (embeddings[j], pattern['id']))
                    embedded_count += 1
                except Exception as e:
                    print(f"   ❌ Error storing embedding for pattern {pattern['id']}: {e}")

        conn.commit()

        # Progress update
        progress = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start_time
        rate = progress / elapsed if elapsed > 0 else 0
        print(f"   Progress: {progress}/{total} ({progress/total*100:.1f}%) | Rate: {rate:.1f} items/sec")

        # Rate limiting (be nice to OpenAI API)
        time.sleep(0.5)

    elapsed = time.time() - start_time
    print(f"\n✅ Embedded {embedded_count} patterns in {elapsed:.1f} seconds")

    cursor.close()
    conn.close()
    return embedded_count

def embed_coding_rules():
    """Generate embeddings for coding rules"""
    print("\n" + "="*80)
    print("📏 EMBEDDING CODING RULES")
    print("="*80)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, rule_title, rule_description, rule_category, applies_to_languages
        FROM coding_rules
        WHERE embedding IS NULL
        ORDER BY id;
    """)

    rules = cursor.fetchall()
    total = len(rules)

    if total == 0:
        print("\n✅ All rules already have embeddings!")
        cursor.close()
        conn.close()
        return 0

    print(f"\n📊 Found {total} rules to embed")

    embedded_count = 0
    start_time = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch = rules[i:i + BATCH_SIZE]

        texts = []
        for r in batch:
            langs = ', '.join(r['applies_to_languages']) if r['applies_to_languages'] else 'general'
            text = f"{r['rule_title']} ({r['rule_category']}, {langs}): {r['rule_description']}"
            texts.append(text)

        embeddings = generate_embeddings_batch(texts)

        for j, rule in enumerate(batch):
            if embeddings[j]:
                try:
                    cursor.execute("""
                        UPDATE coding_rules
                        SET embedding = %s
                        WHERE id = %s;
                    """, (embeddings[j], rule['id']))
                    embedded_count += 1
                except Exception as e:
                    print(f"   ❌ Error storing embedding for rule {rule['id']}: {e}")

        conn.commit()

        progress = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start_time
        rate = progress / elapsed if elapsed > 0 else 0
        print(f"   Progress: {progress}/{total} ({progress/total*100:.1f}%) | Rate: {rate:.1f} items/sec")

        time.sleep(0.5)

    elapsed = time.time() - start_time
    print(f"\n✅ Embedded {embedded_count} rules in {elapsed:.1f} seconds")

    cursor.close()
    conn.close()
    return embedded_count

def embed_oss_repos():
    """Generate embeddings for OSS commercial repos"""
    print("\n" + "="*80)
    print("🔓 EMBEDDING OSS COMMERCIAL REPOS")
    print("="*80)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, repo_full_name, description, primary_language, license_type
        FROM oss_commercial_repos
        WHERE embedding IS NULL
        ORDER BY id;
    """)

    repos = cursor.fetchall()
    total = len(repos)

    if total == 0:
        print("\n✅ All OSS repos already have embeddings!")
        cursor.close()
        conn.close()
        return 0

    print(f"\n📊 Found {total} OSS repos to embed")

    embedded_count = 0
    start_time = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch = repos[i:i + BATCH_SIZE]

        texts = []
        for r in batch:
            desc = r['description'] or 'No description'
            text = f"{r['repo_full_name']} ({r['primary_language']}, {r['license_type']}): {desc}"
            texts.append(text)

        embeddings = generate_embeddings_batch(texts)

        for j, repo in enumerate(batch):
            if embeddings[j]:
                try:
                    cursor.execute("""
                        UPDATE oss_commercial_repos
                        SET embedding = %s
                        WHERE id = %s;
                    """, (embeddings[j], repo['id']))
                    embedded_count += 1
                except Exception as e:
                    print(f"   ❌ Error storing embedding for repo {repo['id']}: {e}")

        conn.commit()

        progress = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start_time
        rate = progress / elapsed if elapsed > 0 else 0
        print(f"   Progress: {progress}/{total} ({progress/total*100:.1f}%) | Rate: {rate:.1f} items/sec")

        time.sleep(0.5)

    elapsed = time.time() - start_time
    print(f"\n✅ Embedded {embedded_count} OSS repos in {elapsed:.1f} seconds")

    cursor.close()
    conn.close()
    return embedded_count

def embed_mcp_servers():
    """Generate embeddings for MCP servers"""
    print("\n" + "="*80)
    print("🔌 EMBEDDING MCP SERVERS")
    print("="*80)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, server_name, description, category
        FROM mcp_servers
        WHERE embedding IS NULL
        ORDER BY id
        LIMIT 1000;  -- Start with top 1000 for cost control
    """)

    servers = cursor.fetchall()
    total = len(servers)

    if total == 0:
        print("\n✅ All MCP servers (first 1000) already have embeddings!")
        cursor.close()
        conn.close()
        return 0

    print(f"\n📊 Found {total} MCP servers to embed (limiting to 1000 for now)")

    embedded_count = 0
    start_time = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch = servers[i:i + BATCH_SIZE]

        texts = []
        for s in batch:
            desc = s['description'] or 'No description'
            cat = s['category'] or 'general'
            text = f"{s['server_name']} ({cat}): {desc}"
            texts.append(text)

        embeddings = generate_embeddings_batch(texts)

        for j, server in enumerate(batch):
            if embeddings[j]:
                try:
                    cursor.execute("""
                        UPDATE mcp_servers
                        SET embedding = %s
                        WHERE id = %s;
                    """, (embeddings[j], server['id']))
                    embedded_count += 1
                except Exception as e:
                    print(f"   ❌ Error storing embedding for server {server['id']}: {e}")

        conn.commit()

        progress = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start_time
        rate = progress / elapsed if elapsed > 0 else 0
        print(f"   Progress: {progress}/{total} ({progress/total*100:.1f}%) | Rate: {rate:.1f} items/sec")

        time.sleep(0.5)

    elapsed = time.time() - start_time
    print(f"\n✅ Embedded {embedded_count} MCP servers in {elapsed:.1f} seconds")
    print(f"   Note: Remaining {4113 - total} servers can be embedded later")

    cursor.close()
    conn.close()
    return embedded_count

def show_summary():
    """Show final embedding statistics"""
    print("\n" + "="*80)
    print("📊 EMBEDDING GENERATION SUMMARY")
    print("="*80)

    conn = get_db_connection()
    cursor = conn.cursor()

    tables = [
        ('coding_patterns', 'Patterns'),
        ('coding_rules', 'Rules'),
        ('oss_commercial_repos', 'OSS Repos'),
        ('mcp_servers', 'MCP Servers')
    ]

    total_embedded = 0

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
        total_embedded += embedded

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")
    print(f"✅ TOTAL EMBEDDINGS GENERATED: {total_embedded:,}")
    print(f"{'='*80}")

def estimate_cost():
    """Estimate embedding generation cost"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM coding_patterns WHERE embedding IS NULL;")
    patterns_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM coding_rules WHERE embedding IS NULL;")
    rules_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM oss_commercial_repos WHERE embedding IS NULL;")
    oss_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM mcp_servers WHERE embedding IS NULL;")
    mcp_count = min(cursor.fetchone()['count'], 1000)

    cursor.close()
    conn.close()

    # Estimate tokens (average ~200 tokens per item)
    total_items = patterns_count + rules_count + oss_count + mcp_count
    estimated_tokens = total_items * 200

    # text-embedding-3-small cost: $0.00002 per 1K tokens
    estimated_cost = (estimated_tokens / 1000) * 0.00002

    print(f"\n💰 COST ESTIMATE")
    print(f"{'='*80}")
    print(f"Items to embed: {total_items:,}")
    print(f"Estimated tokens: {estimated_tokens:,}")
    print(f"Estimated cost: ${estimated_cost:.4f}")
    print(f"{'='*80}\n")

    return estimated_cost

def main():
    """Main embedding generation process"""
    print("\n" + "="*80)
    print(" "*20 + "EMBEDDING GENERATION")
    print("="*80)

    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ Error: OPENAI_API_KEY not found in environment")
        print("   Please set your OpenAI API key in .env file")
        return 1

    # Show cost estimate
    estimate_cost()

    # Ask for confirmation (skip if running non-interactively)
    import sys
    if sys.stdin.isatty():
        print("⚠️  This will use OpenAI API credits. Continue? (Press Enter to continue, Ctrl+C to cancel)")
        try:
            input()
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user")
            return 1
    else:
        print("✅ Running non-interactively, auto-confirming...")

    start_time = time.time()

    # Embed all tables
    patterns_count = embed_coding_patterns()
    rules_count = embed_coding_rules()
    oss_count = embed_oss_repos()
    mcp_count = embed_mcp_servers()

    total_time = time.time() - start_time

    # Show summary
    show_summary()

    print(f"\n⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"\n{'='*80}")
    print("✅ EMBEDDING GENERATION COMPLETE")
    print("="*80)
    print("\nNext step: Test vector search with scripts/test_vector_search.py")
    print()

    return 0

if __name__ == "__main__":
    exit(main())
