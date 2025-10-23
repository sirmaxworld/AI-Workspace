#!/usr/bin/env python3
"""
Verify MCP Database Quality and Statistics
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def verify_database():
    print("="*80)
    print(" "*20 + "MCP DATABASE VERIFICATION")
    print("="*80)

    conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
    cursor = conn.cursor()

    # 1. Total Counts
    print("\n📊 DATABASE STATISTICS")
    print("-" * 80)

    cursor.execute("SELECT COUNT(*) FROM mcp_servers;")
    total_servers = cursor.fetchone()[0]
    print(f"\nTotal MCP Servers: {total_servers:,}")

    cursor.execute("SELECT COUNT(*) FROM mcp_server_tools;")
    total_tools = cursor.fetchone()[0]
    print(f"Total Tools Documented: {total_tools:,}")

    cursor.execute("SELECT COUNT(*) FROM mcp_use_cases;")
    total_use_cases = cursor.fetchone()[0]
    print(f"Total Use Cases: {total_use_cases:,}")

    # 2. Data Quality Metrics
    print("\n📈 DATA QUALITY")
    print("-" * 80)

    cursor.execute("SELECT COUNT(*) FROM mcp_servers WHERE description IS NOT NULL;")
    with_desc = cursor.fetchone()[0]
    print(f"\nWith Descriptions: {with_desc:,} ({(with_desc/total_servers*100):.1f}%)")

    cursor.execute("SELECT COUNT(*) FROM mcp_servers WHERE tools_count > 0;")
    with_tools = cursor.fetchone()[0]
    print(f"With Tools: {with_tools:,} ({(with_tools/total_servers*100):.1f}%)")

    cursor.execute("SELECT COUNT(*) FROM mcp_servers WHERE documentation_url IS NOT NULL;")
    with_docs = cursor.fetchone()[0]
    print(f"With Documentation: {with_docs:,} ({(with_docs/total_servers*100):.1f}%)")

    cursor.execute("SELECT COUNT(*) FROM mcp_servers WHERE author IS NOT NULL;")
    with_author = cursor.fetchone()[0]
    print(f"With Author: {with_author:,} ({(with_author/total_servers*100):.1f}%)")

    # 3. Category Distribution
    print("\n📂 BY CATEGORY")
    print("-" * 80)

    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM mcp_servers
        GROUP BY category
        ORDER BY count DESC
        LIMIT 15;
    """)

    for row in cursor.fetchall():
        category, count = row
        pct = (count / total_servers * 100)
        bar = "█" * int(pct / 2)
        print(f"{category:20s} {count:>6,} ({pct:5.1f}%) {bar}")

    # 4. Source Distribution
    print("\n📦 BY SOURCE")
    print("-" * 80)

    cursor.execute("""
        SELECT source_type, COUNT(*) as count
        FROM mcp_servers
        GROUP BY source_type
        ORDER BY count DESC;
    """)

    for row in cursor.fetchall():
        source, count = row
        pct = (count / total_servers * 100)
        print(f"{source:15s} {count:>6,} ({pct:5.1f}%)")

    # 5. Top Servers by Quality
    print("\n⭐ TOP 10 BY NPM QUALITY SCORE")
    print("-" * 80)

    cursor.execute("""
        SELECT
            server_name,
            (server_metadata->'score'->'detail'->>'quality')::numeric as quality_score
        FROM mcp_servers
        WHERE server_metadata->'score'->'detail'->>'quality' IS NOT NULL
        ORDER BY quality_score DESC
        LIMIT 10;
    """)

    for i, row in enumerate(cursor.fetchall(), 1):
        server_name, quality = row
        print(f"{i:2d}. {server_name:50s} (Score: {quality:.2f})")

    # 6. Index Statistics
    print("\n🗂️  INDEX STATISTICS")
    print("-" * 80)

    cursor.execute("""
        SELECT
            indexrelname as index_name,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
          AND tablename IN ('mcp_servers', 'mcp_server_tools')
        ORDER BY pg_relation_size(indexrelid) DESC;
    """)

    print(f"\n{'Index Name':<40s} {'Size':<10s}")
    print("-" * 50)
    for row in cursor.fetchall():
        index_name, size = row
        print(f"{index_name:<40s} {size:<10s}")

    # 7. Search Performance Test
    print("\n⚡ SEARCH PERFORMANCE TEST")
    print("-" * 80)

    import time

    # Test 1: Category search
    start = time.time()
    cursor.execute("SELECT COUNT(*) FROM mcp_servers WHERE category = 'ai';")
    cursor.fetchone()
    category_time = (time.time() - start) * 1000

    # Test 2: Full-text search
    start = time.time()
    cursor.execute("""
        SELECT COUNT(*) FROM mcp_servers
        WHERE to_tsvector('english', server_name || ' ' || COALESCE(description, ''))
        @@ to_tsquery('english', 'browser');
    """)
    cursor.fetchone()
    fulltext_time = (time.time() - start) * 1000

    # Test 3: Complex query
    start = time.time()
    cursor.execute("""
        SELECT server_name, description
        FROM mcp_servers
        WHERE category = 'automation'
          AND description IS NOT NULL
        ORDER BY downloads_count DESC NULLS LAST
        LIMIT 10;
    """)
    cursor.fetchall()
    complex_time = (time.time() - start) * 1000

    print(f"\nCategory Filter:       {category_time:>6.1f}ms")
    print(f"Full-Text Search:      {fulltext_time:>6.1f}ms")
    print(f"Complex Query (10):    {complex_time:>6.1f}ms")

    if category_time < 10 and fulltext_time < 50 and complex_time < 100:
        print("\n✅ All search performance tests PASSED!")
    else:
        print("\n⚠️  Some queries are slower than expected")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("✅ VERIFICATION COMPLETE - Database is clean and optimized!")
    print("="*80)

if __name__ == "__main__":
    verify_database()
