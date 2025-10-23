#!/usr/bin/env python3
"""
GitHub Repository Collector
Fetches top GitHub repositories by stars for each programming language and stores in Railway PostgreSQL
"""

import os
import json
import time
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv('/Users/yourox/AI-Workspace/.env')

# GitHub API setup
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Optional but recommended for higher rate limits
HEADERS = {'Accept': 'application/vnd.github.v3+json'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'

# Languages to collect
LANGUAGES = [
    'JavaScript', 'TypeScript', 'Python', 'Go', 'Rust',
    'Java', 'C++', 'C', 'Ruby', 'PHP', 'Swift', 'Kotlin',
    'C#', 'Scala', 'Elixir', 'Haskell'
]

# Number of repos per language
REPOS_PER_LANGUAGE = 100
REPOS_PER_PAGE = 100  # GitHub API max

def get_db_connection():
    """Get Railway PostgreSQL connection"""
    return psycopg2.connect(
        os.getenv('RAILWAY_DATABASE_URL'),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def fetch_top_repos_for_language(language: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch top repositories for a specific language using GitHub API

    Args:
        language: Programming language
        limit: Number of repos to fetch

    Returns:
        List of repository data
    """
    repos = []
    page = 1
    per_page = min(100, limit)  # GitHub max is 100 per page

    print(f"\n📥 Fetching {language} repositories...")

    while len(repos) < limit:
        url = f"https://api.github.com/search/repositories"
        params = {
            'q': f'language:{language}',
            'sort': 'stars',
            'order': 'desc',
            'per_page': per_page,
            'page': page
        }

        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)

            # Check rate limit
            if response.status_code == 403:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                if reset_time:
                    wait_seconds = max(reset_time - time.time(), 0) + 10
                    print(f"⚠️  Rate limited. Waiting {wait_seconds:.0f} seconds...")
                    time.sleep(wait_seconds)
                    continue
                else:
                    print(f"❌ Access forbidden: {response.json().get('message', 'Unknown error')}")
                    break

            if response.status_code != 200:
                print(f"❌ Error fetching repos: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                break

            data = response.json()
            items = data.get('items', [])

            if not items:
                print(f"   No more repositories found for {language}")
                break

            repos.extend(items)
            print(f"   Fetched {len(items)} repos (total: {len(repos)}/{limit})")

            # Check if we have enough
            if len(repos) >= limit:
                repos = repos[:limit]
                break

            page += 1

            # Be nice to GitHub API
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error fetching repos for {language}: {e}")
            break

    return repos

def store_repository(cursor, repo_data: Dict[str, Any]) -> int:
    """
    Store or update repository in database

    Returns:
        Repository ID
    """
    # Check if repo exists
    cursor.execute(
        "SELECT id FROM github_repositories WHERE repo_full_name = %s;",
        (repo_data['full_name'],)
    )
    existing = cursor.fetchone()

    # Extract topics (tags)
    topics = repo_data.get('topics', [])

    if existing:
        # Update existing repo
        cursor.execute("""
            UPDATE github_repositories SET
                description = %s,
                language = %s,
                stars = %s,
                forks = %s,
                watchers = %s,
                open_issues = %s,
                created_at = %s,
                updated_at = %s,
                pushed_at = %s,
                clone_url = %s,
                homepage = %s,
                topics = %s,
                license = %s,
                has_wiki = %s,
                has_pages = %s,
                repo_data = %s,
                updated_at_db = NOW()
            WHERE id = %s
            RETURNING id;
        """, (
            repo_data.get('description', ''),
            repo_data.get('language', ''),
            repo_data.get('stargazers_count', 0),
            repo_data.get('forks_count', 0),
            repo_data.get('watchers_count', 0),
            repo_data.get('open_issues_count', 0),
            repo_data.get('created_at'),
            repo_data.get('updated_at'),
            repo_data.get('pushed_at'),
            repo_data.get('clone_url', ''),
            repo_data.get('homepage', ''),
            topics,
            repo_data.get('license', {}).get('spdx_id', '') if repo_data.get('license') else '',
            repo_data.get('has_wiki', False),
            repo_data.get('has_pages', False),
            json.dumps(repo_data),
            existing['id']
        ))
        return existing['id']
    else:
        # Insert new repo
        cursor.execute("""
            INSERT INTO github_repositories (
                repo_full_name,
                owner,
                repo_name,
                description,
                language,
                stars,
                forks,
                watchers,
                open_issues,
                created_at,
                updated_at,
                pushed_at,
                clone_url,
                homepage,
                topics,
                license,
                has_wiki,
                has_pages,
                repo_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            repo_data['full_name'],
            repo_data['owner']['login'],
            repo_data['name'],
            repo_data.get('description', ''),
            repo_data.get('language', ''),
            repo_data.get('stargazers_count', 0),
            repo_data.get('forks_count', 0),
            repo_data.get('watchers_count', 0),
            repo_data.get('open_issues_count', 0),
            repo_data.get('created_at'),
            repo_data.get('updated_at'),
            repo_data.get('pushed_at'),
            repo_data.get('clone_url', ''),
            repo_data.get('homepage', ''),
            topics,
            repo_data.get('license', {}).get('spdx_id', '') if repo_data.get('license') else '',
            repo_data.get('has_wiki', False),
            repo_data.get('has_pages', False),
            json.dumps(repo_data)
        ))

        return cursor.fetchone()['id']

def collect_repos_for_language(language: str, limit: int = 100):
    """Collect and store repositories for a specific language"""
    print(f"\n{'='*80}")
    print(f"  COLLECTING {language.upper()} REPOSITORIES")
    print(f"{'='*80}")

    # Fetch repos from GitHub
    repos = fetch_top_repos_for_language(language, limit)

    if not repos:
        print(f"⚠️  No repositories found for {language}")
        return 0

    # Store in database
    conn = get_db_connection()
    cursor = conn.cursor()

    stored_count = 0
    for i, repo in enumerate(repos, 1):
        try:
            repo_id = store_repository(cursor, repo)
            stored_count += 1

            if i % 10 == 0:
                print(f"   ✅ Stored {i}/{len(repos)} repos")
                conn.commit()  # Commit in batches

        except Exception as e:
            print(f"   ❌ Error storing {repo.get('full_name', 'unknown')}: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✅ Stored {stored_count}/{len(repos)} {language} repositories")
    return stored_count

def fetch_additional_repo_details(repo_full_name: str) -> Dict[str, Any]:
    """Fetch additional details for a repository (contributors, languages, etc.)"""
    url = f"https://api.github.com/repos/{repo_full_name}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"❌ Error fetching details for {repo_full_name}: {e}")

    return {}

def show_collection_summary():
    """Show summary of collected repositories"""
    print(f"\n{'='*80}")
    print("  COLLECTION SUMMARY")
    print(f"{'='*80}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total repos
    cursor.execute("SELECT COUNT(*) as count FROM github_repositories;")
    total = cursor.fetchone()['count']

    # By language
    cursor.execute("""
        SELECT language, COUNT(*) as count, SUM(stars) as total_stars
        FROM github_repositories
        WHERE language IS NOT NULL AND language != ''
        GROUP BY language
        ORDER BY count DESC
        LIMIT 20;
    """)
    by_language = cursor.fetchall()

    print(f"\n📊 Total repositories: {total:,}")
    print(f"\n🔤 Top Languages:")
    for row in by_language:
        print(f"   • {row['language']}: {row['count']} repos ({row['total_stars']:,} stars)")

    # Top repos overall
    cursor.execute("""
        SELECT repo_full_name, language, stars
        FROM github_repositories
        ORDER BY stars DESC
        LIMIT 10;
    """)
    top_repos = cursor.fetchall()

    print(f"\n⭐ Top 10 Repositories:")
    for repo in top_repos:
        print(f"   • {repo['repo_full_name']} ({repo['language']}): {repo['stars']:,} stars")

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")

def main():
    """Main collection process"""
    print("\n" + "="*80)
    print(" "*20 + "GITHUB REPOSITORY COLLECTOR")
    print("="*80)

    start_time = time.time()
    total_collected = 0

    for language in LANGUAGES:
        try:
            count = collect_repos_for_language(language, REPOS_PER_LANGUAGE)
            total_collected += count

            # Be nice to GitHub API
            time.sleep(2)

        except Exception as e:
            print(f"❌ Error collecting {language} repos: {e}")
            continue

    elapsed = time.time() - start_time

    print(f"\n{'='*80}")
    print(f"✅ Collection complete!")
    print(f"   Total repositories collected: {total_collected}")
    print(f"   Time elapsed: {elapsed/60:.1f} minutes")
    print(f"{'='*80}")

    # Show summary
    show_collection_summary()

if __name__ == "__main__":
    main()
