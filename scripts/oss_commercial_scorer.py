#!/usr/bin/env python3
"""
OSS Commercial Scorer
Scores open source repositories for commercial friendliness, usability, and benefit
"""

import os
import json
import psycopg2
import psycopg2.extras
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv('/Users/yourox/AI-Workspace/.env')

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Accept': 'application/vnd.github.v3+json'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'

def get_db_connection():
    """Get Railway PostgreSQL connection"""
    return psycopg2.connect(
        os.getenv('RAILWAY_DATABASE_URL'),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def calculate_license_score(license_type: str) -> int:
    """Score based on license permissiveness (0-100)"""
    scores = {
        'MIT': 100,
        'Apache-2.0': 100,
        'BSD-3-Clause': 95,
        'BSD-2-Clause': 95,
        'ISC': 90,
        'Unlicense': 100,
        'CC0-1.0': 90,
        'MPL-2.0': 70,  # Some restrictions
        'LGPL-3.0': 50,  # More restrictive
        'GPL-3.0': 30,  # Very restrictive
        'AGPL-3.0': 20,  # Most restrictive
    }

    return scores.get(license_type, 40)  # Default for unknown

def calculate_maintenance_score(repo_data: Dict) -> int:
    """Score based on maintenance activity (0-100)"""
    score = 0

    # Check last push date
    if repo_data.get('pushed_at'):
        try:
            pushed_at = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
            days_since_push = (datetime.now(pushed_at.tzinfo) - pushed_at).days

            if days_since_push < 30:
                score += 40  # Very active
            elif days_since_push < 90:
                score += 30  # Active
            elif days_since_push < 180:
                score += 20  # Moderate
            elif days_since_push < 365:
                score += 10  # Slow
            # else: 0 points - inactive

        except:
            score += 10  # Some activity

    # Open issues ratio
    open_issues = repo_data.get('open_issues_count', 0)
    if open_issues < 10:
        score += 15
    elif open_issues < 50:
        score += 10
    elif open_issues < 100:
        score += 5

    # Check if has wiki/docs
    if repo_data.get('has_wiki'):
        score += 5

    if repo_data.get('has_pages'):  # GitHub Pages (often docs)
        score += 10

    # Forks indicate community engagement
    forks = repo_data.get('forks_count', 0)
    if forks > 1000:
        score += 15
    elif forks > 500:
        score += 10
    elif forks > 100:
        score += 5

    # Watchers indicate interest
    watchers = repo_data.get('watchers_count', 0)
    if watchers > 1000:
        score += 15
    elif watchers > 500:
        score += 10
    elif watchers > 100:
        score += 5

    return min(score, 100)

def calculate_documentation_score(repo_data: Dict) -> int:
    """Score based on documentation quality (0-100)"""
    score = 0

    # Has description
    if repo_data.get('description'):
        score += 20

    # Has homepage (often docs site)
    if repo_data.get('homepage'):
        score += 20

    # Has wiki
    if repo_data.get('has_wiki'):
        score += 15

    # Has topics (indicates categorization effort)
    topics = repo_data.get('topics', [])
    if len(topics) >= 5:
        score += 20
    elif len(topics) >= 3:
        score += 15
    elif len(topics) >= 1:
        score += 10

    # Star count indicates visibility/documentation quality correlation
    stars = repo_data.get('stargazers_count', 0)
    if stars > 10000:
        score += 25
    elif stars > 5000:
        score += 15
    elif stars > 1000:
        score += 10
    elif stars > 100:
        score += 5

    return min(score, 100)

def calculate_usability_score(repo_data: Dict) -> int:
    """Score based on ease of use (0-100)"""
    score = 40  # Base score

    # Language popularity (affects ease of integration)
    language = repo_data.get('language', '')
    popular_languages = ['JavaScript', 'TypeScript', 'Python', 'Go', 'Java', 'Ruby', 'PHP', 'C#']
    if language in popular_languages:
        score += 20

    # Size (smaller is often easier)
    size_kb = repo_data.get('size', 0)
    if size_kb < 1000:  # < 1MB
        score += 15
    elif size_kb < 10000:  # < 10MB
        score += 10
    elif size_kb < 100000:  # < 100MB
        score += 5

    # Has topics (good organization)
    if len(repo_data.get('topics', [])) > 0:
        score += 10

    # Has homepage (easier to understand)
    if repo_data.get('homepage'):
        score += 15

    return min(score, 100)

def calculate_benefit_score(repo_data: Dict) -> int:
    """Score based on value/benefit to users (0-100)"""
    score = 0

    # Stars indicate value
    stars = repo_data.get('stargazers_count', 0)
    if stars > 50000:
        score += 40
    elif stars > 20000:
        score += 35
    elif stars > 10000:
        score += 30
    elif stars > 5000:
        score += 25
    elif stars > 1000:
        score += 20
    elif stars > 500:
        score += 15
    elif stars > 100:
        score += 10
    else:
        score += 5

    # Forks indicate usefulness
    forks = repo_data.get('forks_count', 0)
    if forks > 5000:
        score += 30
    elif forks > 1000:
        score += 25
    elif forks > 500:
        score += 20
    elif forks > 100:
        score += 15
    else:
        score += 10

    # Recency
    if repo_data.get('pushed_at'):
        try:
            pushed_at = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
            days_since_push = (datetime.now(pushed_at.tzinfo) - pushed_at).days

            if days_since_push < 30:
                score += 30  # Very fresh
            elif days_since_push < 90:
                score += 20
            elif days_since_push < 180:
                score += 10

        except:
            score += 5

    return min(score, 100)

def calculate_commercial_suitability_score(repo_row: Dict) -> Dict[str, int]:
    """Calculate all commercial suitability scores"""

    repo_metadata = repo_row.get('repo_metadata', {})
    if isinstance(repo_metadata, str):
        repo_metadata = json.loads(repo_metadata)

    scores = {
        'license_score': calculate_license_score(repo_row.get('license_type', '')),
        'maintenance_score': calculate_maintenance_score(repo_metadata),
        'documentation_score': calculate_documentation_score(repo_metadata),
        'usability_score': calculate_usability_score(repo_metadata),
        'benefit_score': calculate_benefit_score(repo_metadata)
    }

    # Overall score (weighted average)
    scores['overall_score'] = int(
        scores['license_score'] * 0.30 +  # License is most important
        scores['maintenance_score'] * 0.25 +
        scores['documentation_score'] * 0.20 +
        scores['usability_score'] * 0.15 +
        scores['benefit_score'] * 0.10
    )

    return scores

def score_repositories():
    """Score all unscored repositories"""
    print("\n" + "="*80)
    print(" "*20 + "OSS COMMERCIAL SCORING")
    print("="*80)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get repos without scores (docs_quality_score is NULL)
    cursor.execute("""
        SELECT *
        FROM oss_commercial_repos
        WHERE docs_quality_score IS NULL
        ORDER BY stars DESC;
    """)
    repos = cursor.fetchall()

    if not repos:
        print("\n✅ All repositories already scored!")
        cursor.close()
        conn.close()
        return

    print(f"\n📊 Found {len(repos)} repositories to score")

    scored_count = 0
    for i, repo in enumerate(repos, 1):
        try:
            scores = calculate_commercial_suitability_score(repo)

            # Determine commit frequency
            commit_freq = 'unknown'
            if repo.get('repo_metadata'):
                metadata = repo['repo_metadata']
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)

                if metadata.get('pushed_at'):
                    pushed_at = datetime.fromisoformat(metadata['pushed_at'].replace('Z', '+00:00'))
                    days_since = (datetime.now(pushed_at.tzinfo) - pushed_at).days

                    if days_since < 7:
                        commit_freq = 'very-active'
                    elif days_since < 30:
                        commit_freq = 'active'
                    elif days_since < 90:
                        commit_freq = 'moderate'
                    elif days_since < 365:
                        commit_freq = 'slow'
                    else:
                        commit_freq = 'inactive'

            # Update repository with scores
            cursor.execute("""
                UPDATE oss_commercial_repos SET
                    docs_quality_score = %s,
                    commit_frequency = %s,
                    is_actively_maintained = %s,
                    enriched_at = NOW()
                WHERE id = %s;
            """, (
                scores['overall_score'],
                commit_freq,
                commit_freq in ['very-active', 'active', 'moderate'],
                repo['id']
            ))

            scored_count += 1

            if i % 50 == 0:
                print(f"   Scored {i}/{len(repos)} repos")
                conn.commit()

        except Exception as e:
            print(f"   ❌ Error scoring {repo.get('repo_full_name', 'unknown')}: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✅ Scored {scored_count}/{len(repos)} repositories")

def show_scoring_summary():
    """Show summary of scored repositories"""
    print(f"\n{'='*80}")
    print("  SCORING SUMMARY")
    print(f"{'='*80}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Top scored repos
    cursor.execute("""
        SELECT repo_full_name, license_type, docs_quality_score, stars, commit_frequency
        FROM oss_commercial_repos
        WHERE docs_quality_score IS NOT NULL
        ORDER BY docs_quality_score DESC
        LIMIT 20;
    """)
    top_repos = cursor.fetchall()

    print(f"\n🏆 Top 20 Commercial-Friendly Repos:")
    for i, repo in enumerate(top_repos, 1):
        print(f"   {i:2d}. {repo['repo_full_name']:40s} | Score: {repo['docs_quality_score']:3d} | ⭐ {repo['stars']:6,d} | {repo['license_type']:15s}")

    # By commit frequency
    cursor.execute("""
        SELECT commit_frequency, COUNT(*) as count
        FROM oss_commercial_repos
        WHERE commit_frequency IS NOT NULL
        GROUP BY commit_frequency
        ORDER BY count DESC;
    """)
    by_freq = cursor.fetchall()

    print(f"\n📈 By Maintenance Activity:")
    for row in by_freq:
        print(f"   • {row['commit_frequency']}: {row['count']}")

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")

def main():
    """Main scoring process"""
    score_repositories()
    show_scoring_summary()

if __name__ == "__main__":
    main()
