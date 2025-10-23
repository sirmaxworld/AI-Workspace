#!/usr/bin/env python3
"""
Query RSS Articles from Database

Quick queries to view stored RSS articles.
"""

import os
import sys
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
load_dotenv('/Users/yourox/AI-Workspace/.env')

def query_recent_articles(limit=20):
    """Show recent articles from all sources"""

    conn_string = os.getenv('RAILWAY_DATABASE_URL')
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print(f"📰 RECENT RSS ARTICLES (Last {limit})")
    print(f"{'='*80}\n")

    cursor.execute("""
        SELECT
            ec.title,
            es.name as source,
            ec.published_at,
            ec.raw_score,
            ec.url
        FROM external_content ec
        JOIN external_sources es ON ec.source_id = es.source_id
        ORDER BY ec.fetched_at DESC
        LIMIT %s
    """, (limit,))

    articles = cursor.fetchall()

    for i, (title, source, published, score, url) in enumerate(articles, 1):
        print(f"{i}. {title[:70]}...")
        print(f"   Source: {source} | Score: {score:.2f} | Published: {published.strftime('%Y-%m-%d %H:%M')}")
        print(f"   URL: {url}")
        print()

    cursor.close()
    conn.close()

def query_by_source():
    """Show article counts by source"""

    conn_string = os.getenv('RAILWAY_DATABASE_URL')
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print(f"📊 ARTICLES BY SOURCE")
    print(f"{'='*80}\n")

    cursor.execute("""
        SELECT
            es.name,
            es.priority,
            es.base_weight,
            COUNT(ec.content_id) as article_count,
            AVG(ec.raw_score) as avg_score,
            MAX(ec.fetched_at) as last_fetch
        FROM external_sources es
        LEFT JOIN external_content ec ON es.source_id = ec.source_id
        GROUP BY es.source_id, es.name, es.priority, es.base_weight
        ORDER BY article_count DESC
    """)

    sources = cursor.fetchall()

    for name, priority, weight, count, avg_score, last_fetch in sources:
        avg_score_str = f"{avg_score:.2f}" if avg_score else "N/A"
        last_fetch_str = last_fetch.strftime('%Y-%m-%d %H:%M') if last_fetch else "Never"

        print(f"• {name}")
        print(f"  Priority: {priority} | Weight: {weight} | Articles: {count}")
        print(f"  Avg Score: {avg_score_str} | Last Fetch: {last_fetch_str}")
        print()

    cursor.close()
    conn.close()

def query_top_scored(limit=10):
    """Show highest scored articles"""

    conn_string = os.getenv('RAILWAY_DATABASE_URL')
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print(f"⭐ TOP SCORED ARTICLES")
    print(f"{'='*80}\n")

    cursor.execute("""
        SELECT
            ec.title,
            es.name as source,
            ec.raw_score,
            ec.content_length,
            ec.published_at
        FROM external_content ec
        JOIN external_sources es ON ec.source_id = es.source_id
        ORDER BY ec.raw_score DESC, ec.published_at DESC
        LIMIT %s
    """, (limit,))

    articles = cursor.fetchall()

    for i, (title, source, score, length, published) in enumerate(articles, 1):
        print(f"{i}. [{score:.2f}] {title[:65]}...")
        print(f"   {source} | {length} words | {published.strftime('%Y-%m-%d')}")
        print()

    cursor.close()
    conn.close()

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Query RSS Articles')
    parser.add_argument('--recent', type=int, default=20,
                        help='Show N recent articles')
    parser.add_argument('--by-source', action='store_true',
                        help='Show articles grouped by source')
    parser.add_argument('--top', type=int, default=10,
                        help='Show top scored articles')

    args = parser.parse_args()

    if args.by_source:
        query_by_source()
    elif args.top:
        query_top_scored(limit=args.top)
    else:
        query_recent_articles(limit=args.recent)

if __name__ == "__main__":
    main()
