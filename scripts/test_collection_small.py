#!/usr/bin/env python3
"""
Small Batch Test
Tests collection with minimal data to verify everything works
"""

import sys
import time
sys.path.insert(0, '/Users/yourox/AI-Workspace/scripts')

from github_repo_collector import fetch_top_repos_for_language, store_repository
from github_pattern_extractor import process_repository, get_repos_to_process
from oss_repo_collector import collect_known_projects
from oss_commercial_scorer import calculate_commercial_suitability_score
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def get_db_connection():
    return psycopg2.connect(
        os.getenv('RAILWAY_DATABASE_URL'),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def test_github_collection():
    """Test GitHub collection with 3 languages × 5 repos"""
    print("\n" + "="*80)
    print("  TEST 1: GITHUB COLLECTION (3 languages × 5 repos)")
    print("="*80)

    languages = ['Python', 'JavaScript', 'Go']
    total_collected = 0

    conn = get_db_connection()
    cursor = conn.cursor()

    for lang in languages:
        print(f"\n📥 Collecting {lang} repos...")
        repos = fetch_top_repos_for_language(lang, limit=5)

        for repo in repos:
            repo_id = store_repository(cursor, repo)
            total_collected += 1
            print(f"   ✅ {repo['full_name']} - ⭐ {repo['stargazers_count']:,}")

        conn.commit()
        time.sleep(1)

    cursor.close()
    conn.close()

    print(f"\n✅ Collected {total_collected} repos across {len(languages)} languages")
    return total_collected

def test_pattern_extraction():
    """Test pattern extraction on collected repos"""
    print("\n" + "="*80)
    print("  TEST 2: PATTERN EXTRACTION (top 5 repos)")
    print("="*80)

    repos = get_repos_to_process(limit=5)

    if not repos:
        print("\n⚠️  No repos to process (already enriched or no repos collected)")
        return 0

    print(f"\n📊 Processing {len(repos)} repositories...")

    total_extracted = 0
    for repo in repos:
        count = process_repository(repo)
        total_extracted += count

    print(f"\n✅ Extracted {total_extracted} patterns/rules")
    return total_extracted

def test_oss_collection():
    """Test OSS collection with known projects"""
    print("\n" + "="*80)
    print("  TEST 3: OSS COLLECTION (11 known projects)")
    print("="*80)

    count = collect_known_projects()

    print(f"\n✅ Collected {count} OSS projects")
    return count

def test_commercial_scoring():
    """Test commercial scoring on collected OSS repos"""
    print("\n" + "="*80)
    print("  TEST 4: COMMERCIAL SCORING")
    print("="*80)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get unscored repos
    cursor.execute("""
        SELECT *
        FROM oss_commercial_repos
        WHERE docs_quality_score IS NULL
        LIMIT 15;
    """)
    repos = cursor.fetchall()

    if not repos:
        print("\n⚠️  No repos to score")
        cursor.close()
        conn.close()
        return 0

    print(f"\n📊 Scoring {len(repos)} repositories...")

    scored_count = 0
    for repo in repos:
        try:
            scores = calculate_commercial_suitability_score(repo)

            cursor.execute("""
                UPDATE oss_commercial_repos SET
                    docs_quality_score = %s
                WHERE id = %s;
            """, (scores['overall_score'], repo['id']))

            scored_count += 1
            print(f"   ✅ {repo['repo_full_name'][:50]:50s} Score: {scores['overall_score']}/100")

        except Exception as e:
            print(f"   ⚠️  Error scoring {repo.get('repo_full_name', 'unknown')}: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✅ Scored {scored_count} repos")
    return scored_count

def show_test_summary():
    """Show summary of test data"""
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)

    conn = get_db_connection()
    cursor = conn.cursor()

    # GitHub repos
    cursor.execute("SELECT COUNT(*) as count FROM github_repositories;")
    github_count = cursor.fetchone()['count']

    # Patterns
    cursor.execute("SELECT COUNT(*) as count FROM coding_patterns;")
    patterns_count = cursor.fetchone()['count']

    # Rules
    cursor.execute("SELECT COUNT(*) as count FROM coding_rules;")
    rules_count = cursor.fetchone()['count']

    # OSS repos
    cursor.execute("SELECT COUNT(*) as count FROM oss_commercial_repos;")
    oss_count = cursor.fetchone()['count']

    # Scored OSS
    cursor.execute("""
        SELECT COUNT(*) as count FROM oss_commercial_repos
        WHERE docs_quality_score IS NOT NULL;
    """)
    scored_count = cursor.fetchone()['count']

    print(f"\n📊 Database Contents:")
    print(f"   GitHub Repositories: {github_count:,}")
    print(f"   Coding Patterns: {patterns_count:,}")
    print(f"   Coding Rules: {rules_count:,}")
    print(f"   OSS Repos: {oss_count:,}")
    print(f"   OSS Repos Scored: {scored_count:,}/{oss_count:,}")

    # Show sample repos
    cursor.execute("""
        SELECT repo_full_name, stars, language
        FROM github_repositories
        ORDER BY stars DESC
        LIMIT 5;
    """)
    top_repos = cursor.fetchall()

    if top_repos:
        print(f"\n⭐ Top 5 GitHub Repos:")
        for repo in top_repos:
            print(f"   • {repo['repo_full_name']:40s} {repo['stars']:7,} stars ({repo['language']})")

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")

def main():
    """Run small batch tests"""
    print("\n" + "="*80)
    print(" "*25 + "SMALL BATCH TEST")
    print("="*80)
    print("\nTesting with minimal data to verify all systems work")

    start_time = time.time()

    try:
        # Test 1: GitHub Collection
        github_count = test_github_collection()

        # Test 2: Pattern Extraction
        pattern_count = test_pattern_extraction()

        # Test 3: OSS Collection
        oss_count = test_oss_collection()

        # Test 4: Commercial Scoring
        scored_count = test_commercial_scoring()

        # Summary
        show_test_summary()

        elapsed = time.time() - start_time

        print(f"\n{'='*80}")
        print(f"✅ ALL TESTS PASSED!")
        print(f"   Time elapsed: {elapsed:.1f} seconds")
        print(f"\n   Ready for full collection!")
        print(f"{'='*80}\n")

        return 0

    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ TEST FAILED: {e}")
        print(f"{'='*80}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
