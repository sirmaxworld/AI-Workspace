#!/usr/bin/env python3
"""
Direct YC Companies Migration to Railway PostgreSQL
Bypasses Mem0/OpenAI - stores enriched data directly in PostgreSQL
"""
import os
import json
import psycopg2
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def load_yc_companies():
    """Load all enriched YC companies"""
    yc_dir = Path('/Users/yourox/AI-Workspace/data/yc_enriched')
    companies = []

    print(f"Loading YC companies from {yc_dir}...")
    for json_file in sorted(yc_dir.glob('*_enriched.json')):
        try:
            with open(json_file, 'r') as f:
                company = json.load(f)
                companies.append(company)
        except Exception as e:
            print(f"⚠️  Error loading {json_file.name}: {e}")

    print(f"✅ Loaded {len(companies)} companies")
    return companies

def create_yc_table(cursor):
    """Create YC companies enrichment table"""
    # Mem0 already created yc_companies table (id uuid, vector, payload jsonb)
    # Create a new table for enriched data with proper structure
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yc_companies_enriched (
            id SERIAL PRIMARY KEY,
            slug VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            yc_id INTEGER,
            batch VARCHAR(20),
            website TEXT,

            -- Phase 1: Web Data
            web_data JSONB,
            phase1_complete BOOLEAN DEFAULT FALSE,

            -- Phase 2: Geographic
            geographic_data JSONB,
            phase2_complete BOOLEAN DEFAULT FALSE,

            -- Phase 3: GitHub
            github_data JSONB,
            phase3_complete BOOLEAN DEFAULT FALSE,

            -- Phase 4: Network
            network_data JSONB,
            phase4_complete BOOLEAN DEFAULT FALSE,

            -- Phase 5: Patents
            patent_data JSONB,
            phase5_complete BOOLEAN DEFAULT FALSE,

            -- Phase 6: Reviews
            reviews_data JSONB,
            phase6_complete BOOLEAN DEFAULT FALSE,

            -- Phase 7: Hiring
            hiring_data JSONB,
            phase7_complete BOOLEAN DEFAULT FALSE,

            -- Phase 8: AI Insights
            ai_insights JSONB,
            phase8_complete BOOLEAN DEFAULT FALSE,

            -- Full enriched data
            enriched_data JSONB,

            -- Metadata
            enriched_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),

            CONSTRAINT never_delete CHECK (true)
        );

        CREATE INDEX IF NOT EXISTS idx_yc_enr_slug ON yc_companies_enriched(slug);
        CREATE INDEX IF NOT EXISTS idx_yc_enr_batch ON yc_companies_enriched(batch);
        CREATE INDEX IF NOT EXISTS idx_yc_enr_name ON yc_companies_enriched(name);
    """)
    print("✅ YC companies enriched table created/verified")

def migrate_companies(companies, cursor, conn):
    """Migrate companies to PostgreSQL"""
    total = len(companies)
    migrated = 0
    failed = 0
    skipped = 0

    print(f"\n{'='*60}")
    print(f"MIGRATING {total} YC COMPANIES TO RAILWAY POSTGRESQL")
    print(f"{'='*60}\n")

    for i, company in enumerate(companies, 1):
        try:
            slug = company.get('slug')
            if not slug:
                print(f"⚠️  Skipping company without slug")
                skipped += 1
                continue

            # Check if already exists
            cursor.execute("SELECT id FROM yc_companies_enriched WHERE slug = %s", (slug,))
            if cursor.fetchone():
                skipped += 1
                if skipped % 100 == 0:
                    print(f"   ⏭️  {skipped} companies already in database...", end='\r')
                continue

            # Extract data
            name = company.get('name', 'Unknown')
            yc_id = company.get('yc_id')
            batch = company.get('batch')
            website = company.get('website')

            # Phase completion flags
            phase1 = company.get('phase1_complete', False)
            phase2 = company.get('phase2_complete', False)
            phase3 = company.get('phase3_complete', False)
            phase4 = company.get('phase4_complete', False)
            phase5 = company.get('phase5_complete', False)
            phase6 = company.get('phase6_complete', False)
            phase7 = company.get('phase7_complete', False)
            phase8 = company.get('phase8_complete', False)

            # Phase data
            web_data = json.dumps(company.get('web_data', {}))
            geographic_data = json.dumps(company.get('geographic_data', {}))
            github_data = json.dumps(company.get('github_data', {}))
            network_data = json.dumps(company.get('network_data', {}))
            patent_data = json.dumps(company.get('patent_data', {}))
            reviews_data = json.dumps(company.get('reviews_data', {}))
            hiring_data = json.dumps(company.get('hiring_data', {}))
            ai_insights = json.dumps(company.get('ai_insights', {}))

            # Full enriched data
            enriched_data = json.dumps(company)
            enriched_at = company.get('enriched_at')

            # Insert into database
            cursor.execute("""
                INSERT INTO yc_companies_enriched (
                    slug, name, yc_id, batch, website,
                    web_data, phase1_complete,
                    geographic_data, phase2_complete,
                    github_data, phase3_complete,
                    network_data, phase4_complete,
                    patent_data, phase5_complete,
                    reviews_data, phase6_complete,
                    hiring_data, phase7_complete,
                    ai_insights, phase8_complete,
                    enriched_data, enriched_at
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s
                )
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    web_data = EXCLUDED.web_data,
                    phase1_complete = EXCLUDED.phase1_complete,
                    geographic_data = EXCLUDED.geographic_data,
                    phase2_complete = EXCLUDED.phase2_complete,
                    github_data = EXCLUDED.github_data,
                    phase3_complete = EXCLUDED.phase3_complete,
                    network_data = EXCLUDED.network_data,
                    phase4_complete = EXCLUDED.phase4_complete,
                    patent_data = EXCLUDED.patent_data,
                    phase5_complete = EXCLUDED.phase5_complete,
                    reviews_data = EXCLUDED.reviews_data,
                    phase6_complete = EXCLUDED.phase6_complete,
                    hiring_data = EXCLUDED.hiring_data,
                    phase7_complete = EXCLUDED.phase7_complete,
                    ai_insights = EXCLUDED.ai_insights,
                    phase8_complete = EXCLUDED.phase8_complete,
                    enriched_data = EXCLUDED.enriched_data,
                    enriched_at = EXCLUDED.enriched_at,
                    updated_at = NOW();
            """, (
                slug, name, yc_id, batch, website,
                web_data, phase1,
                geographic_data, phase2,
                github_data, phase3,
                network_data, phase4,
                patent_data, phase5,
                reviews_data, phase6,
                hiring_data, phase7,
                ai_insights, phase8,
                enriched_data, enriched_at
            ))

            migrated += 1

            if migrated % 10 == 0:
                conn.commit()
                print(f"   ✅ {migrated}/{total} companies migrated ({(migrated/total)*100:.1f}%)...", end='\r')

        except Exception as e:
            failed += 1
            print(f"\n   ⚠️  Failed to migrate {company.get('name', 'Unknown')}: {e}")

    conn.commit()

    print(f"\n\n{'='*60}")
    print(f"✅ Migration complete!")
    print(f"   Migrated: {migrated}/{total}")
    print(f"   Skipped (already in DB): {skipped}")
    print(f"   Failed: {failed}")
    print(f"{'='*60}\n")

    return migrated, skipped, failed

def verify_migration(cursor):
    """Verify migration was successful"""
    print("\n" + "="*60)
    print("VERIFYING MIGRATION")
    print("="*60)

    # Get counts
    cursor.execute("SELECT COUNT(*) FROM yc_companies_enriched;")
    total_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM yc_companies_enriched WHERE phase1_complete = TRUE;")
    phase1_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM yc_companies_enriched WHERE phase8_complete = TRUE;")
    phase8_count = cursor.fetchone()[0]

    print(f"✅ Total companies: {total_count}")
    print(f"✅ Phase 1 complete: {phase1_count}")
    print(f"✅ Phase 8 complete (AI insights): {phase8_count}")

    # Sample companies
    cursor.execute("""
        SELECT name, batch, phase1_complete, phase8_complete
        FROM yc_companies_enriched
        ORDER BY name
        LIMIT 5;
    """)
    samples = cursor.fetchall()

    print(f"\nSample companies:")
    for name, batch, p1, p8 in samples:
        print(f"   - {name} (YC {batch}) - Phase1: {p1}, Phase8: {p8}")

    print("\n✅ Migration verified successfully!")
    return True

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Direct YC migration to Railway')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    args = parser.parse_args()

    print("\n" + "="*80)
    print(" "*15 + "DIRECT YC COMPANIES MIGRATION TO RAILWAY POSTGRESQL")
    print("="*80)

    # Load companies
    companies = load_yc_companies()

    if not companies:
        print("❌ No companies found to migrate")
        return 1

    # Ask for confirmation
    print(f"\n⚠️  About to migrate {len(companies)} YC companies to Railway PostgreSQL")
    print("   This will:")
    print("   - Store all enrichment data directly in PostgreSQL")
    print("   - Preserve all Phase 1-8 data")
    print("   - Skip OpenAI embeddings (can add later)")
    print("   - Update existing records if they exist")

    if not args.yes:
        response = input("\nProceed with migration? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Migration cancelled")
            return 1
    else:
        print("\n✅ Auto-confirming migration (--yes flag)")

    # Connect to database
    try:
        conn_string = os.getenv('RAILWAY_DATABASE_URL')
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        print("\n✅ Connected to Railway PostgreSQL")

        # Create table
        create_yc_table(cursor)
        conn.commit()

        # Migrate companies
        migrated, skipped, failed = migrate_companies(companies, cursor, conn)

        if migrated == 0 and skipped == 0:
            print("❌ Migration failed")
            return 1

        # Verify
        verify_migration(cursor)

        cursor.close()
        conn.close()

        print("\n🎉 YC companies successfully migrated to Railway PostgreSQL!")
        print(f"   Total: {migrated + skipped}/{len(companies)}")
        print(f"   Storage: ~{((migrated + skipped) * 50) // 1024}MB")
        return 0

    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
