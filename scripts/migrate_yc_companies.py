#!/usr/bin/env python3
"""
Migrate YC Companies from JSON to Railway PostgreSQL + Mem0 pgvector

This script:
1. Reads enriched YC companies from /data/yc_enriched/*.json
2. Stores in Mem0 pgvector collection for semantic search
3. No direct Railway tables needed - Mem0 handles pgvector storage

Run this AFTER user completes YC enrichment phase.
"""
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
from config.mem0_collections import get_mem0_config

load_dotenv('/Users/yourox/AI-Workspace/.env')

def load_yc_companies():
    """Load all enriched YC companies from JSON files"""
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

def migrate_to_mem0(companies, batch_size=50):
    """
    Migrate companies to Mem0 pgvector collection

    Args:
        companies: List of company dicts
        batch_size: Process in batches to avoid memory issues
    """
    print("\n" + "="*60)
    print("MIGRATING YC COMPANIES TO MEM0 PGVECTOR")
    print("="*60)

    try:
        from mem0 import Memory

        # Temporarily unset OPENROUTER_API_KEY to force Mem0 to use OpenAI
        openrouter_key = os.environ.pop('OPENROUTER_API_KEY', None)
        if openrouter_key:
            print("✅ Temporarily disabled OpenRouter (using OpenAI directly)")

        # Initialize Mem0 with pgvector backend
        config = get_mem0_config("yc_companies")
        m = Memory.from_config(config)
        print("✅ Mem0 connection established")

        # Migrate in batches
        total = len(companies)
        migrated = 0
        failed = 0

        for i in range(0, total, batch_size):
            batch = companies[i:i+batch_size]
            print(f"\n📦 Processing batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, total)} of {total})...")

            for company in batch:
                try:
                    # Create searchable text from company data
                    name = company.get('name', 'Unknown')
                    website = company.get('website', '')
                    batch = company.get('batch', '')

                    # Extract web data if available
                    web_data = company.get('web_data', {})
                    social_links = web_data.get('social_links', {})
                    domain_info = web_data.get('domain_info', {})

                    # Create rich text for embedding
                    company_text = f"{name} (YC {batch})"
                    if website:
                        company_text += f" - {website}"

                    # Add social links
                    socials = []
                    if social_links.get('twitter'):
                        socials.append(f"Twitter: {social_links['twitter']}")
                    if social_links.get('github'):
                        socials.append(f"GitHub: {social_links['github']}")
                    if socials:
                        company_text += " | " + ", ".join(socials)

                    # Add domain info
                    if domain_info.get('domain'):
                        company_text += f" | Domain: {domain_info['domain']}"

                    # Store in Mem0 with full metadata
                    result = m.add(
                        company_text,
                        user_id="yc_batch_groups",
                        metadata={
                            "slug": company.get('slug'),
                            "name": name,
                            "yc_id": company.get('yc_id'),
                            "batch": batch,
                            "website": website,
                            "enriched_at": company.get('enriched_at'),
                            "phase1_complete": company.get('phase1_complete', False),
                            "domain": domain_info.get('domain'),
                            "domain_age_years": domain_info.get('domain_age_years'),
                            "twitter": social_links.get('twitter'),
                            "github": social_links.get('github'),
                            "source": "yc_enriched"
                        }
                    )

                    migrated += 1

                    if migrated % 10 == 0:
                        print(f"   ✅ {migrated}/{total} companies migrated...", end='\r')

                except Exception as e:
                    failed += 1
                    print(f"   ⚠️  Failed to migrate {company.get('name', 'Unknown')}: {e}")

        print(f"\n\n{'='*60}")
        print(f"✅ Migration complete!")
        print(f"   Migrated: {migrated}/{total}")
        print(f"   Failed: {failed}")
        print(f"{'='*60}\n")

        return migrated, failed

    except ImportError:
        print("❌ mem0 library not installed. Install with:")
        print("   pip3 install mem0ai")
        return 0, 0

    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

def verify_migration():
    """Verify migration was successful"""
    print("\n" + "="*60)
    print("VERIFYING MIGRATION")
    print("="*60)

    try:
        from mem0 import Memory

        config = get_mem0_config("yc_companies")
        m = Memory.from_config(config)

        # Get sample companies
        results = m.get_all(user_id="yc_batch_groups", limit=5)

        print(f"✅ Found {len(results)} companies in Mem0")
        print("\nSample companies:")
        for i, result in enumerate(results[:3], 1):
            metadata = result.get('metadata', {})
            print(f"   {i}. {metadata.get('name')} (YC {metadata.get('batch')})")

        # Test semantic search
        print("\n🔍 Testing semantic search...")
        search_results = m.search("AI developer tools", user_id="yc_batch_groups", limit=3)

        print(f"✅ Search returned {len(search_results)} results")
        for i, result in enumerate(search_results, 1):
            metadata = result.get('metadata', {})
            print(f"   {i}. {metadata.get('name')} - {metadata.get('website')}")

        print("\n✅ Migration verified successfully!")
        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Migrate YC companies to Railway pgvector')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    args = parser.parse_args()

    print("\n" + "="*80)
    print(" "*20 + "YC COMPANIES MIGRATION TO RAILWAY PGVECTOR")
    print("="*80)

    # Load companies
    companies = load_yc_companies()

    if not companies:
        print("❌ No companies found to migrate")
        return 1

    # Ask for confirmation
    print(f"\n⚠️  About to migrate {len(companies)} YC companies to Railway pgvector")
    print("   This will:")
    print("   - Store embeddings in Railway PostgreSQL with pgvector")
    print("   - Enable semantic search via Mem0")
    print("   - Preserve all enrichment data as metadata")

    if not args.yes:
        response = input("\nProceed with migration? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Migration cancelled")
            return 1
    else:
        print("\n✅ Auto-confirming migration (--yes flag)")


    # Migrate
    migrated, failed = migrate_to_mem0(companies)

    if migrated == 0:
        print("❌ Migration failed")
        return 1

    # Verify
    if not verify_migration():
        print("⚠️  Migration completed but verification failed")
        return 1

    print("\n🎉 YC companies successfully migrated to Railway pgvector!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
