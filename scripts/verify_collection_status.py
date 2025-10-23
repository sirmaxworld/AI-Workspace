#!/usr/bin/env python3
"""
Verify Collection Status

Check database for:
1. How many sources are registered
2. How many sources have content
3. Total articles collected
4. Date range coverage
"""

import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def verify_status():
    """Check database status"""

    conn_string = os.getenv('RAILWAY_DATABASE_URL')
    if not conn_string:
        print("❌ No database URL found")
        return

    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # Count sources
    cursor.execute("SELECT COUNT(*) FROM external_sources")
    total_sources = cursor.fetchone()[0]

    # Count sources with content
    cursor.execute("""
        SELECT COUNT(DISTINCT source_id)
        FROM external_content
    """)
    sources_with_content = cursor.fetchone()[0]

    # Count total articles
    cursor.execute("SELECT COUNT(*) FROM external_content")
    total_articles = cursor.fetchone()[0]

    # Get date range
    cursor.execute("""
        SELECT
            MIN(published_at) as earliest,
            MAX(published_at) as latest
        FROM external_content
    """)
    date_range = cursor.fetchone()

    # Get articles by source
    cursor.execute("""
        SELECT
            s.name,
            s.category,
            s.priority,
            COUNT(c.content_id) as article_count,
            MIN(c.published_at) as earliest,
            MAX(c.published_at) as latest
        FROM external_sources s
        LEFT JOIN external_content c ON s.source_id = c.source_id
        GROUP BY s.source_id, s.name, s.category, s.priority
        ORDER BY article_count DESC, s.priority DESC, s.name
    """)
    sources = cursor.fetchall()

    cursor.close()
    conn.close()

    # Print summary
    print(f"\n{'='*70}")
    print(f"📊 COLLECTION STATUS SUMMARY")
    print(f"{'='*70}\n")

    print(f"📈 Overall Statistics:")
    print(f"   - Total sources registered: {total_sources}")
    print(f"   - Sources with content: {sources_with_content}")
    print(f"   - Sources without content: {total_sources - sources_with_content}")
    print(f"   - Total articles: {total_articles}")

    if date_range[0] and date_range[1]:
        earliest = date_range[0]
        latest = date_range[1]
        days_span = (latest - earliest).days
        print(f"   - Date range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
        print(f"   - Coverage: {days_span} days (~{days_span/30:.1f} months)")

    # Calculate 6-month target
    six_months_ago = datetime.now() - timedelta(days=180)
    cursor = conn = psycopg2.connect(conn_string).cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM external_content
        WHERE published_at >= %s
    """, (six_months_ago,))
    articles_last_6m = cursor.fetchone()[0]
    cursor.connection.close()

    print(f"   - Articles from last 6 months: {articles_last_6m}")

    print(f"\n{'='*70}")
    print(f"📋 SOURCES BREAKDOWN")
    print(f"{'='*70}\n")

    # Group by category
    by_category = {}
    for source in sources:
        name, category, priority, count, earliest, latest = source
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((name, count, earliest, latest))

    for category in sorted(by_category.keys()):
        sources_list = by_category[category]
        total_in_cat = sum(s[1] for s in sources_list)
        sources_with_content_cat = sum(1 for s in sources_list if s[1] > 0)

        print(f"\n📂 {category.upper()} ({sources_with_content_cat}/{len(sources_list)} sources with content, {total_in_cat} articles)")

        for name, count, earliest, latest in sources_list:
            if count > 0:
                days = (latest - earliest).days if earliest and latest else 0
                print(f"   ✅ {name}: {count} articles (last {days} days)")
            else:
                print(f"   ❌ {name}: 0 articles")

    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    verify_status()
