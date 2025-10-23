#!/usr/bin/env python3
"""
Add Tier 2 RSS sources to external_sources table
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
load_dotenv('/Users/yourox/AI-Workspace/.env')

# Import source configs
from scripts.rss_expanded_collector import TIER2_SOURCES

def add_tier2_sources():
    """Add all Tier 2 sources to database"""

    conn_string = os.getenv('RAILWAY_DATABASE_URL')
    if not conn_string:
        print("❌ RAILWAY_DATABASE_URL not found")
        return

    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        print(f"\n{'='*70}")
        print(f"📝 Adding {len(TIER2_SOURCES)} Tier 2 sources to database")
        print(f"{'='*70}\n")

        added = 0
        skipped = 0

        for source_id, config in TIER2_SOURCES.items():
            try:
                cursor.execute("""
                    INSERT INTO external_sources (
                        source_id, name, domain, rss_url,
                        category, source_type, extraction_method,
                        priority, base_weight,
                        rate_limit_per_day, is_active
                    ) VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        %s, %s
                    )
                    ON CONFLICT (source_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        rss_url = EXCLUDED.rss_url,
                        base_weight = EXCLUDED.base_weight
                """, (
                    source_id,
                    config['name'],
                    config['domain'],
                    config['rss_url'],
                    config['category'],
                    'rss_feed',
                    'rss',
                    config['priority'],
                    config['base_weight'],
                    config['rate_limit_per_day'],
                    True
                ))

                if cursor.rowcount > 0:
                    print(f"   ✓ {config['name']}")
                    added += 1
                else:
                    print(f"   ⟳ {config['name']} (already exists)")
                    skipped += 1

            except Exception as e:
                print(f"   ✗ {config['name']}: {e}")
                conn.rollback()
                continue

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n{'='*70}")
        print(f"✅ Added: {added} sources")
        print(f"⟳  Skipped: {skipped} sources (already exist)")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    add_tier2_sources()
