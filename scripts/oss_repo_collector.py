#!/usr/bin/env python3
"""
OSS Repository Collector
Collects commercial-friendly open source projects from awesome lists and other sources
"""

import os
import re
import json
import time
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

load_dotenv('/Users/yourox/AI-Workspace/.env')

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Accept': 'application/vnd.github.v3+json'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'

# Awesome lists to scrape
AWESOME_LISTS = [
    'sindresorhus/awesome',
    'Solido/awesome-flutter',
    'avelino/awesome-go',
    'vinta/awesome-python',
    'sorrycc/awesome-javascript',
    'enaqx/awesome-react',
    'vuejs/awesome-vue',
    'rust-unofficial/awesome-rust',
    'akullpp/awesome-java',
    'JStumpp/awesome-android',
    'vsouza/awesome-ios',
    'nuxt/awesome',
    'humanetech-community/awesome-humane-tech',
    'stefanbuck/awesome-browser-extensions-for-github',
    'crewAIInc/awesome-crewai',
]

# Specific project lists (known commercial-friendly OSS)
KNOWN_PROJECTS = [
    {'repo': 'n8n-io/n8n', 'category': 'workflow-automation'},
    {'repo': 'activepieces/activepieces', 'category': 'workflow-automation'},
    {'repo': 'windmill-labs/windmill', 'category': 'workflow-automation'},
    {'repo': 'nocobase/nocobase', 'category': 'database'},
    {'repo': 'appsmithorg/appsmith', 'category': 'low-code'},
    {'repo': 'ToolJet/ToolJet', 'category': 'low-code'},
    {'repo': 'PostHog/posthog', 'category': 'analytics'},
    {'repo': 'plausible/analytics', 'category': 'analytics'},
    {'repo': 'supabase/supabase', 'category': 'database'},
    {'repo': 'directus/directus', 'category': 'cms'},
    {'repo': 'strapi/strapi', 'category': 'cms'},
]

def get_db_connection():
    """Get Railway PostgreSQL connection"""
    return psycopg2.connect(
        os.getenv('RAILWAY_DATABASE_URL'),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def fetch_repo_details(repo_full_name: str) -> Optional[Dict]:
    """Fetch complete repository details from GitHub API"""
    url = f"https://api.github.com/repos/{repo_full_name}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"   ⚠️  Repo not found: {repo_full_name}")
        elif response.status_code == 403:
            print(f"   ⚠️  Rate limited. Waiting...")
            time.sleep(60)

    except Exception as e:
        print(f"   ❌ Error fetching {repo_full_name}: {e}")

    return None

def fetch_readme_content(repo_full_name: str) -> Optional[str]:
    """Fetch README from a repository"""
    url = f"https://api.github.com/repos/{repo_full_name}/readme"

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)

        if response.status_code == 200:
            data = response.json()
            import base64
            content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
            return content

    except Exception as e:
        pass

    return None

def extract_repos_from_readme(readme_content: str) -> List[str]:
    """Extract GitHub repo links from README"""
    repos = []

    # Pattern: github.com/owner/repo
    pattern = r'github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)'
    matches = re.findall(pattern, readme_content)

    for match in matches:
        # Clean up
        repo = match.rstrip(')')  # Remove trailing )
        repo = repo.split('#')[0]  # Remove anchors
        repo = repo.split('?')[0]  # Remove query params

        # Skip if it contains invalid characters
        if not re.match(r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$', repo):
            continue

        repos.append(repo)

    return list(set(repos))  # Remove duplicates

def categorize_repo(repo_data: Dict, source_category: str = None) -> List[str]:
    """Determine categories for a repository"""
    categories = []

    # Use source category if provided
    if source_category:
        categories.append(source_category)

    # Analyze description and topics
    description = (repo_data.get('description', '') or '').lower()
    topics = [t.lower() for t in repo_data.get('topics', [])]

    all_text = ' '.join([description] + topics)

    # Category keywords
    category_map = {
        'workflow-automation': ['workflow', 'automation', 'zapier', 'n8n', 'integrate'],
        'ai-ml': ['ai', 'machine-learning', 'ml', 'artificial-intelligence', 'llm', 'gpt'],
        'database': ['database', 'sql', 'nosql', 'postgres', 'mongodb', 'firebase'],
        'low-code': ['low-code', 'no-code', 'visual', 'builder', 'drag-and-drop'],
        'cms': ['cms', 'content-management', 'headless'],
        'analytics': ['analytics', 'tracking', 'metrics', 'telemetry'],
        'dev-tools': ['developer', 'devtools', 'cli', 'tool'],
        'api': ['api', 'rest', 'graphql', 'endpoint'],
        'frontend': ['frontend', 'ui', 'react', 'vue', 'angular'],
        'backend': ['backend', 'server', 'node', 'express', 'fastapi'],
    }

    for category, keywords in category_map.items():
        for keyword in keywords:
            if keyword in all_text:
                categories.append(category)
                break

    return list(set(categories)) or ['general']

def store_oss_repo(cursor, repo_data: Dict, categories: List[str]) -> Optional[int]:
    """Store OSS repository in database"""

    # Check if exists
    cursor.execute(
        "SELECT id FROM oss_commercial_repos WHERE repo_full_name = %s;",
        (repo_data['full_name'],)
    )
    existing = cursor.fetchone()

    license_type = 'Unknown'
    if repo_data.get('license'):
        license_type = repo_data['license'].get('spdx_id', 'Unknown')

    # Commercial-friendly licenses
    commercial_licenses = ['MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC', 'Unlicense']
    is_commercial_friendly = license_type in commercial_licenses

    repo_id = None

    try:
        if existing:
            # Update
            cursor.execute("""
                UPDATE oss_commercial_repos SET
                    description = %s,
                    primary_language = %s,
                    license_type = %s,
                    is_commercial_friendly = %s,
                    stars = %s,
                    forks = %s,
                    watchers = %s,
                    last_commit_date = %s,
                    has_readme = %s,
                    has_wiki = %s,
                    repo_url = %s,
                    homepage = %s,
                    repo_metadata = %s
                WHERE id = %s
                RETURNING id;
            """, (
                repo_data.get('description', ''),
                repo_data.get('language', ''),
                license_type,
                is_commercial_friendly,
                repo_data.get('stargazers_count', 0),
                repo_data.get('forks_count', 0),
                repo_data.get('watchers_count', 0),
                repo_data.get('pushed_at'),
                True,  # has_readme (we don't check this yet)
                repo_data.get('has_wiki', False),
                repo_data.get('html_url', ''),
                repo_data.get('homepage', ''),
                json.dumps(repo_data),
                existing['id']
            ))
            repo_id = existing['id']
        else:
            # Insert
            cursor.execute("""
                INSERT INTO oss_commercial_repos (
                    repo_full_name,
                    owner,
                    repo_name,
                    description,
                    primary_language,
                    license_type,
                    is_commercial_friendly,
                    stars,
                    forks,
                    watchers,
                    last_commit_date,
                    has_readme,
                    has_wiki,
                    repo_url,
                    homepage,
                    repo_metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                repo_data['full_name'],
                repo_data['owner']['login'],
                repo_data['name'],
                repo_data.get('description', ''),
                repo_data.get('language', ''),
                license_type,
                is_commercial_friendly,
                repo_data.get('stargazers_count', 0),
                repo_data.get('forks_count', 0),
                repo_data.get('watchers_count', 0),
                repo_data.get('pushed_at'),
                True,
                repo_data.get('has_wiki', False),
                repo_data.get('html_url', ''),
                repo_data.get('homepage', ''),
                json.dumps(repo_data)
            ))
            repo_id = cursor.fetchone()['id']

        # Store categories
        for category in categories:
            cursor.execute("""
                INSERT INTO oss_repo_categories (repo_id, category, relevance_score)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (repo_id, category, 80))

        return repo_id

    except Exception as e:
        print(f"   ❌ Error storing {repo_data['full_name']}: {e}")
        return None

def collect_from_awesome_list(list_repo: str):
    """Collect repos from an awesome list"""
    print(f"\n📚 Processing awesome list: {list_repo}")

    # Fetch README
    readme = fetch_readme_content(list_repo)
    if not readme:
        print(f"   ⚠️  Could not fetch README")
        return 0

    # Extract repos
    repos = extract_repos_from_readme(readme)
    print(f"   Found {len(repos)} repository links")

    conn = get_db_connection()
    cursor = conn.cursor()

    stored_count = 0
    for i, repo_name in enumerate(repos[:100], 1):  # Limit to 100 per list
        try:
            # Fetch repo details
            repo_data = fetch_repo_details(repo_name)
            if not repo_data:
                continue

            # Skip if < 100 stars (quality filter)
            if repo_data.get('stargazers_count', 0) < 100:
                continue

            # Categorize
            categories = categorize_repo(repo_data)

            # Store
            repo_id = store_oss_repo(cursor, repo_data, categories)
            if repo_id:
                stored_count += 1

            if i % 10 == 0:
                print(f"   Processed {i}/{min(len(repos), 100)} repos ({stored_count} stored)")
                conn.commit()

            time.sleep(0.5)  # Be nice to API

        except Exception as e:
            print(f"   ❌ Error processing {repo_name}: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"   ✅ Stored {stored_count} repos from {list_repo}")
    return stored_count

def collect_known_projects():
    """Collect known commercial-friendly projects"""
    print(f"\n📦 Collecting known commercial projects...")

    conn = get_db_connection()
    cursor = conn.cursor()

    stored_count = 0
    for project in KNOWN_PROJECTS:
        try:
            repo_data = fetch_repo_details(project['repo'])
            if not repo_data:
                continue

            categories = [project['category']]
            categories.extend(categorize_repo(repo_data))

            repo_id = store_oss_repo(cursor, repo_data, categories)
            if repo_id:
                stored_count += 1
                print(f"   ✅ {project['repo']}")

            time.sleep(0.5)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n   ✅ Stored {stored_count}/{len(KNOWN_PROJECTS)} known projects")
    return stored_count

def show_collection_summary():
    """Show summary of OSS collection"""
    print(f"\n{'='*80}")
    print("  OSS COLLECTION SUMMARY")
    print(f"{'='*80}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total repos
    cursor.execute("SELECT COUNT(*) as count FROM oss_commercial_repos;")
    total = cursor.fetchone()['count']

    # Commercial-friendly
    cursor.execute("""
        SELECT COUNT(*) as count FROM oss_commercial_repos
        WHERE is_commercial_friendly = TRUE;
    """)
    commercial = cursor.fetchone()['count']

    # By license
    cursor.execute("""
        SELECT license_type, COUNT(*) as count
        FROM oss_commercial_repos
        GROUP BY license_type
        ORDER BY count DESC
        LIMIT 10;
    """)
    by_license = cursor.fetchall()

    # By category
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM oss_repo_categories
        GROUP BY category
        ORDER BY count DESC
        LIMIT 10;
    """)
    by_category = cursor.fetchall()

    print(f"\n📊 Total OSS repos: {total:,}")
    print(f"✅ Commercial-friendly: {commercial:,} ({commercial/total*100:.1f}%)")

    print(f"\n📜 By License:")
    for row in by_license:
        print(f"   • {row['license_type']}: {row['count']}")

    print(f"\n📁 By Category:")
    for row in by_category:
        print(f"   • {row['category']}: {row['count']}")

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")

def main():
    """Main collection process"""
    print("\n" + "="*80)
    print(" "*20 + "OSS REPOSITORY COLLECTOR")
    print("="*80)

    start_time = time.time()
    total_collected = 0

    # 1. Collect known projects first
    total_collected += collect_known_projects()

    # 2. Collect from awesome lists
    for awesome_list in AWESOME_LISTS[:5]:  # Start with first 5 lists
        try:
            count = collect_from_awesome_list(awesome_list)
            total_collected += count
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error collecting from {awesome_list}: {e}")
            continue

    elapsed = time.time() - start_time

    print(f"\n{'='*80}")
    print(f"✅ Collection complete!")
    print(f"   Total repos collected: {total_collected}")
    print(f"   Time elapsed: {elapsed/60:.1f} minutes")
    print(f"{'='*80}")

    show_collection_summary()

if __name__ == "__main__":
    main()
