#!/usr/bin/env python3
"""
Import 4,103 MCP Servers from npm Registry into Railway PostgreSQL
"""
import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def load_npm_packages():
    """Load all npm MCP packages"""
    with open('/Users/yourox/AI-Workspace/data/mcp_directory/all_packages.json', 'r') as f:
        data = json.load(f)
    return data['packages']

def load_categories():
    """Load category mappings"""
    with open('/Users/yourox/AI-Workspace/data/mcp_directory/by_category.json', 'r') as f:
        data = json.load(f)
        return data['categories']

def determine_category(package, category_data):
    """Determine category for a package"""
    pkg_name = package['name']

    # Check each category
    for category, category_dict in category_data.items():
        packages = category_dict.get('packages', [])
        if pkg_name in [p['name'] for p in packages]:
            # Map npm categories to our categories
            category_map = {
                'official': 'general',
                'web_search': 'search',
                'browser_automation': 'automation',
                'database': 'database',
                'file_system': 'general',
                'api_integration': 'integration',
                'developer_tools': 'development',
                'ai_models': 'ai',
                'data_extraction': 'data',
                'communication': 'communication',
                'productivity': 'productivity',
                'finance': 'finance',
                'security': 'security',
                'other': 'general'
            }
            return category_map.get(category, 'general')

    return 'general'

def import_packages():
    """Import all packages to Railway PostgreSQL"""
    print("="*80)
    print(" "*15 + "IMPORTING 4,103 MCP SERVERS FROM NPM")
    print("="*80)

    # Load data
    packages = load_npm_packages()
    category_data = load_categories()

    print(f"\n📦 Loaded {len(packages)} packages from npm registry")

    # Connect to database
    conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
    cursor = conn.cursor()

    inserted = 0
    updated = 0
    skipped = 0

    for i, pkg in enumerate(packages, 1):
        try:
            # Check if already exists
            cursor.execute("SELECT id FROM mcp_servers WHERE server_name = %s;", (pkg['name'],))
            existing = cursor.fetchone()

            # Determine category
            category = determine_category(pkg, category_data)

            # Parse dates
            date_published = None
            if pkg.get('date_published'):
                try:
                    date_published = datetime.fromisoformat(pkg['date_published'].replace('Z', '+00:00'))
                except:
                    pass

            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE mcp_servers SET
                        description = COALESCE(description, %s),
                        source_type = %s,
                        source_url = %s,
                        package_name = %s,
                        category = COALESCE(category, %s),
                        author = COALESCE(author, %s),
                        documentation_url = COALESCE(documentation_url, %s),
                        downloads_count = %s,
                        last_updated = %s,
                        server_metadata = %s
                    WHERE server_name = %s;
                """, (
                    pkg.get('description'),
                    'npm',
                    pkg.get('npm_url'),
                    pkg['name'],
                    category,
                    pkg.get('publisher'),
                    pkg.get('homepage') or pkg.get('repository'),
                    pkg.get('downloads_last_month', 0),
                    date_published,
                    json.dumps(pkg),
                    pkg['name']
                ))
                updated += 1
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO mcp_servers (
                        server_name,
                        display_name,
                        description,
                        source_type,
                        source_url,
                        package_name,
                        install_command,
                        category,
                        author,
                        documentation_url,
                        downloads_count,
                        last_updated,
                        is_actively_maintained,
                        server_metadata,
                        verified
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                """, (
                    pkg['name'],
                    pkg['name'],
                    pkg.get('description'),
                    'npm',
                    pkg.get('npm_url'),
                    pkg['name'],
                    f"npx -y {pkg['name']}",
                    category,
                    pkg.get('publisher'),
                    pkg.get('homepage') or pkg.get('repository'),
                    pkg.get('downloads_last_month', 0),
                    date_published,
                    True,  # Assume maintained if on npm
                    json.dumps(pkg),
                    False  # Not verified yet
                ))
                inserted += 1

            # Commit in batches
            if (i % 100) == 0:
                conn.commit()
                print(f"   Progress: {i}/{len(packages)} ({(i/len(packages)*100):.1f}%) - Inserted: {inserted}, Updated: {updated}", end='\r')

        except Exception as e:
            skipped += 1
            if skipped < 10:  # Only show first 10 errors
                print(f"\n   ⚠️  Error with {pkg['name']}: {e}")

    # Final commit
    conn.commit()

    # Get final count
    cursor.execute("SELECT COUNT(*) FROM mcp_servers;")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print(f"\n\n{'='*80}")
    print(f"✅ Import Complete!")
    print(f"   Inserted: {inserted}")
    print(f"   Updated: {updated}")
    print(f"   Skipped: {skipped}")
    print(f"   Total in database: {total}")
    print(f"{'='*80}")

    return inserted, updated, skipped, total

def show_stats():
    """Show database statistics"""
    print("\n" + "="*80)
    print(" "*25 + "DATABASE STATISTICS")
    print("="*80)

    conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
    cursor = conn.cursor()

    # Total servers
    cursor.execute("SELECT COUNT(*) FROM mcp_servers;")
    total = cursor.fetchone()[0]
    print(f"\nTotal MCP Servers: {total:,}")

    # By category
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM mcp_servers
        GROUP BY category
        ORDER BY count DESC;
    """)

    print(f"\nBy Category:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,} servers")

    # By source
    cursor.execute("""
        SELECT source_type, COUNT(*) as count
        FROM mcp_servers
        GROUP BY source_type
        ORDER BY count DESC;
    """)

    print(f"\nBy Source:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,} servers")

    # With descriptions
    cursor.execute("SELECT COUNT(*) FROM mcp_servers WHERE description IS NOT NULL;")
    with_desc = cursor.fetchone()[0]
    print(f"\nWith Descriptions: {with_desc:,} ({(with_desc/total*100):.1f}%)")

    # With tools documented
    cursor.execute("SELECT COUNT(*) FROM mcp_servers WHERE tools_count > 0;")
    with_tools = cursor.fetchone()[0]
    print(f"With Tools Documented: {with_tools:,} ({(with_tools/total*100):.1f}%)")

    # Top 10 by downloads
    cursor.execute("""
        SELECT server_name, downloads_count
        FROM mcp_servers
        WHERE downloads_count > 0
        ORDER BY downloads_count DESC
        LIMIT 10;
    """)

    top_downloads = cursor.fetchall()
    if top_downloads:
        print(f"\nTop 10 by Downloads:")
        for row in top_downloads:
            print(f"  {row[0]}: {row[1]:,} downloads")

    cursor.close()
    conn.close()

    print("\n" + "="*80)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Import npm MCP servers to Railway')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    args = parser.parse_args()

    if not args.yes:
        response = input(f"\n⚠️  About to import 4,103 MCP servers to Railway PostgreSQL.\nProceed? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Import cancelled")
            exit(1)
    else:
        print("\n✅ Auto-confirming import (--yes flag)")

    # Import
    import_packages()

    # Show stats
    show_stats()
