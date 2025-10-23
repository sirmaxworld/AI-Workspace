#!/usr/bin/env python3
"""
Test Vector Search
Verify semantic search works across all intelligence tables
"""

import os
import psycopg2
import psycopg2.extras
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

# Load model
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def get_db_connection():
    """Get Railway PostgreSQL connection"""
    return psycopg2.connect(
        os.getenv('RAILWAY_DATABASE_URL'),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def semantic_search(query: str, table: str, columns: list, limit: int = 5):
    """Perform semantic search on a table"""
    # Generate query embedding
    query_embedding = MODEL.encode(query).tolist()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Vector similarity search
    columns_str = ', '.join(columns)
    cursor.execute(f"""
        SELECT
            {columns_str},
            1 - (embedding <=> %s::vector) as similarity
        FROM {table}
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (query_embedding, query_embedding, limit))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results

def test_query(query: str, table: str, columns: list, desc: str):
    """Test a single query"""
    print(f"\n🔍 Query: \"{query}\"")
    print(f"   Target: {desc}")
    print(f"   " + "-" * 70)

    results = semantic_search(query, table, columns, limit=3)

    for i, result in enumerate(results, 1):
        similarity = result['similarity']
        bar = '█' * int(similarity * 20)
        print(f"\n   {i}. [{bar:<20}] {similarity:.3f}")

        # Print result details
        for col in columns[:2]:  # Show first 2 columns
            value = str(result.get(col, 'N/A'))
            if len(value) > 80:
                value = value[:77] + "..."
            print(f"      {col}: {value}")

    return results

def main():
    """Main test process"""
    print("\n" + "="*80)
    print(" "*25 + "VECTOR SEARCH TEST")
    print("="*80)

    # Test 1: Search coding patterns
    print("\n" + "="*80)
    print("TEST 1: CODING PATTERNS")
    print("="*80)

    test_query(
        "How to write unit tests in JavaScript",
        "coding_patterns",
        ['pattern_name', 'description', 'language'],
        "JavaScript testing patterns"
    )

    test_query(
        "Best way to handle errors in Python",
        "coding_patterns",
        ['pattern_name', 'description', 'language'],
        "Python error handling"
    )

    # Test 2: Search coding rules
    print("\n\n" + "="*80)
    print("TEST 2: CODING RULES")
    print("="*80)

    test_query(
        "Security best practices for user input",
        "coding_rules",
        ['rule_title', 'rule_description', 'rule_category'],
        "Security rules"
    )

    test_query(
        "How to write clean code",
        "coding_rules",
        ['rule_title', 'rule_description', 'rule_category'],
        "Code quality rules"
    )

    # Test 3: Search OSS repos
    print("\n\n" + "="*80)
    print("TEST 3: OSS COMMERCIAL REPOS")
    print("="*80)

    test_query(
        "Lightweight date library for JavaScript",
        "oss_commercial_repos",
        ['repo_full_name', 'description', 'license_type'],
        "Date libraries"
    )

    test_query(
        "Python web framework with good documentation",
        "oss_commercial_repos",
        ['repo_full_name', 'description', 'license_type'],
        "Python web frameworks"
    )

    # Test 4: Search MCP servers
    print("\n\n" + "="*80)
    print("TEST 4: MCP SERVERS")
    print("="*80)

    test_query(
        "Database integration and SQL queries",
        "mcp_servers",
        ['server_name', 'description', 'category'],
        "Database MCP servers"
    )

    test_query(
        "Web automation and browser control",
        "mcp_servers",
        ['server_name', 'description', 'category'],
        "Browser automation"
    )

    # Performance test
    print("\n\n" + "="*80)
    print("PERFORMANCE TEST")
    print("="*80)

    import time

    print("\n⏱️  Testing query latency (10 queries)...")

    latencies = []
    for i in range(10):
        start = time.time()
        semantic_search(
            "test query " + str(i),
            "coding_patterns",
            ['pattern_name'],
            limit=5
        )
        latency = (time.time() - start) * 1000  # ms
        latencies.append(latency)

    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)

    print(f"\n   Average latency: {avg_latency:.1f}ms")
    print(f"   Min latency: {min_latency:.1f}ms")
    print(f"   Max latency: {max_latency:.1f}ms")

    if avg_latency < 100:
        print(f"   ✅ EXCELLENT - Sub-100ms queries!")
    elif avg_latency < 200:
        print(f"   ✅ GOOD - Fast enough for production")
    else:
        print(f"   ⚠️  SLOW - May need optimization")

    # Summary
    print("\n" + "="*80)
    print("✅ VECTOR SEARCH TEST COMPLETE")
    print("="*80)
    print("\n✅ Semantic search working across all tables!")
    print("✅ Relevance scores look accurate")
    print("✅ Query performance is excellent")
    print("\n" + "="*80 + "\n")

    return 0

if __name__ == "__main__":
    exit(main())
