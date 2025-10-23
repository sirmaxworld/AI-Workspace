#!/usr/bin/env python3
"""
Expand to Complete 76-Source Catalog

Phase 1: Add all new sources to database
Phase 2: Collect 6 months from RSS feeds
Phase 3: Build targeted scrapers for non-RSS sources
"""

import os
import sys
import psycopg2
from datetime import datetime

sys.path.append('/Users/yourox/AI-Workspace')
from dotenv import load_dotenv
load_dotenv('/Users/yourox/AI-Workspace/.env')

from scripts.rss_complete_catalog import (
    ALL_SOURCES_COMPLETE,
    MEDITATION_SOURCES,
    QUANTUM_SOURCES,
    HUMOR_SOURCES,
    SME_SOURCES,
    BUSINESS_ADDITIONAL
)

def add_sources_to_database():
    """Add all new sources to external_sources table"""

    conn_string = os.getenv('RAILWAY_DATABASE_URL')
    if not conn_string:
        print("❌ No Railway database URL found")
        return

    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # Check existing sources
    cursor.execute("SELECT source_id FROM external_sources")
    existing_ids = {row[0] for row in cursor.fetchall()}

    print(f"\n📊 Database Status:")
    print(f"   - Existing sources: {len(existing_ids)}")
    print(f"   - Total in catalog: {len(ALL_SOURCES_COMPLETE)}")
    print(f"   - New sources to add: {len(ALL_SOURCES_COMPLETE) - len(existing_ids)}\n")

    added_count = 0

    for source_id, config in ALL_SOURCES_COMPLETE.items():
        if source_id in existing_ids:
            continue

        try:
            cursor.execute("""
                INSERT INTO external_sources (
                    source_id, name, domain, category,
                    source_type, priority, base_weight,
                    rss_url, is_active, added_at
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
            """, (
                source_id,
                config['name'],
                config['domain'],
                config['category'],
                'rss' if config.get('rss_url') else 'scraping',
                config['priority'],
                config['base_weight'],
                config.get('rss_url'),
                True,
                datetime.now()
            ))

            added_count += 1
            print(f"   ✓ Added: {config['name']} ({source_id})")

        except Exception as e:
            print(f"   ❌ Error adding {source_id}: {e}")
            conn.rollback()
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✅ Added {added_count} new sources to database\n")

def collect_from_new_rss_feeds():
    """Collect from all RSS feeds in new categories"""

    print(f"\n{'='*70}")
    print(f"🚀 COLLECTING FROM NEW RSS FEEDS")
    print(f"{'='*70}\n")

    # Import collector
    from scripts.rss_expanded_collector import ExpandedRSSCollector

    # Combine all new sources with RSS feeds
    new_rss_sources = {}

    for source_dict in [MEDITATION_SOURCES, QUANTUM_SOURCES, HUMOR_SOURCES, SME_SOURCES, BUSINESS_ADDITIONAL]:
        for source_id, config in source_dict.items():
            if config.get('rss_url'):
                new_rss_sources[source_id] = config

    print(f"📰 Found {len(new_rss_sources)} RSS feeds to collect from:")
    for sid, conf in new_rss_sources.items():
        print(f"   - {conf['name']} ({conf['category']})")

    print(f"\n{'='*70}\n")

    # Initialize collector with new sources
    collector = ExpandedRSSCollector(sources_config=new_rss_sources)

    # Collect from all new RSS sources
    results = collector.collect_all_sources(limit_per_source=100, max_age_days=180, verbose=True)

    # Summary
    print(f"\n{'='*70}")
    print(f"📊 COLLECTION SUMMARY")
    print(f"{'='*70}\n")

    total_articles = 0
    successful_sources = 0

    for source_id, count in results.items():
        source_name = new_rss_sources[source_id]['name']
        if count > 0:
            print(f"   ✓ {source_name}: {count} articles")
            successful_sources += 1
            total_articles += count
        else:
            print(f"   ❌ {source_name}: 0 articles")

    print(f"\n   TOTAL: {total_articles} articles from {successful_sources}/{len(new_rss_sources)} sources")
    print(f"{'='*70}\n")

    return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Expand to complete 76-source catalog')
    parser.add_argument('--add-sources', action='store_true',
                        help='Add new sources to database')
    parser.add_argument('--collect-rss', action='store_true',
                        help='Collect from all new RSS feeds')
    parser.add_argument('--all', action='store_true',
                        help='Run all phases')

    args = parser.parse_args()

    if args.all or args.add_sources:
        print("\n🔧 PHASE 1: Adding sources to database...")
        add_sources_to_database()

    if args.all or args.collect_rss:
        print("\n📰 PHASE 2: Collecting from RSS feeds...")
        collect_from_new_rss_feeds()

    if not (args.add_sources or args.collect_rss or args.all):
        parser.print_help()
