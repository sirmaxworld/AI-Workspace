#!/usr/bin/env python3
"""
GitHub Pattern Extractor
Extracts coding patterns, rules, and methods from GitHub repositories
Uses GitHub API to analyze README, CONTRIBUTING, and code structure
"""

import os
import re
import json
import time
import requests
import psycopg2
import psycopg2.extras
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

load_dotenv('/Users/yourox/AI-Workspace/.env')

# GitHub API setup
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

def fetch_github_file(repo_full_name: str, file_path: str) -> Optional[str]:
    """
    Fetch a file from GitHub repository

    Args:
        repo_full_name: e.g., "facebook/react"
        file_path: e.g., "CONTRIBUTING.md"

    Returns:
        File content as string or None
    """
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)

        if response.status_code == 200:
            data = response.json()

            # Decode base64 content
            import base64
            content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
            return content

    except Exception as e:
        print(f"   ⚠️  Error fetching {file_path}: {e}")

    return None

def extract_rules_from_contributing(content: str, repo_id: int, repo_name: str) -> List[Dict]:
    """Extract coding rules from CONTRIBUTING.md"""
    rules = []

    # Look for common rule sections
    sections = {
        'Code Style': 'naming',
        'Coding Style': 'naming',
        'Style Guide': 'naming',
        'Testing': 'testing',
        'Documentation': 'docs',
        'Security': 'security',
        'Pull Requests': 'structure',
        'Commit Messages': 'structure'
    }

    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Look for headings
        if line.startswith('#'):
            heading = line.lstrip('#').strip()

            for section_name, category in sections.items():
                if section_name.lower() in heading.lower():
                    # Extract content under this heading
                    description_lines = []
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith('#'):
                        if lines[j].strip():
                            description_lines.append(lines[j].strip())
                        j += 1

                    if description_lines:
                        rules.append({
                            'repo_id': repo_id,
                            'category': category,
                            'title': heading,
                            'description': ' '.join(description_lines[:5]),  # First 5 lines
                            'extracted_from': 'CONTRIBUTING.md',
                            'confidence': 90
                        })

    return rules

def extract_rules_from_readme(content: str, repo_id: int, repo_name: str) -> List[Dict]:
    """Extract best practices and guidelines from README"""
    rules = []

    # Look for common patterns
    patterns = [
        (r'(?:best practice|recommended|guideline)s?:?\s*(.{50,300})', 'best-practice'),
        (r'(?:do not|don\'t|avoid|never)\s+(.{30,200})', 'anti-pattern'),
        (r'(?:always|must|should)\s+(.{30,200})', 'guideline'),
    ]

    for pattern, rule_type in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

        for match in matches:
            description = match.group(1).strip()

            rules.append({
                'repo_id': repo_id,
                'category': rule_type,
                'title': f"{rule_type.title()} from {repo_name}",
                'description': description,
                'extracted_from': 'README.md',
                'confidence': 70
            })

    return rules[:10]  # Limit to top 10

def extract_coding_patterns(repo_full_name: str, language: str) -> List[Dict]:
    """
    Extract common coding patterns from repository structure

    This is a simplified version - in production, you'd clone and analyze actual code
    """
    patterns = []

    # Fetch package.json for JavaScript/TypeScript projects
    if language in ['JavaScript', 'TypeScript']:
        package_json = fetch_github_file(repo_full_name, 'package.json')
        if package_json:
            try:
                data = json.loads(package_json)

                # Extract testing frameworks
                dev_deps = data.get('devDependencies', {})
                if 'jest' in dev_deps:
                    patterns.append({
                        'pattern_type': 'testing',
                        'pattern_name': 'Jest Testing Framework',
                        'description': f'Uses Jest for testing. Version: {dev_deps["jest"]}',
                        'language': language,
                        'usage_frequency': 'very-common'
                    })

                # Extract build tools
                scripts = data.get('scripts', {})
                if 'build' in scripts:
                    patterns.append({
                        'pattern_type': 'build-process',
                        'pattern_name': 'Build Script',
                        'description': f'Build command: {scripts["build"]}',
                        'language': language,
                        'usage_frequency': 'common'
                    })

            except json.JSONDecodeError:
                pass

    # Fetch setup.py or pyproject.toml for Python
    elif language == 'Python':
        # Try pyproject.toml first (modern)
        pyproject = fetch_github_file(repo_full_name, 'pyproject.toml')
        if pyproject:
            patterns.append({
                'pattern_type': 'project-structure',
                'pattern_name': 'Modern Python Project Structure',
                'description': 'Uses pyproject.toml for project configuration',
                'language': language,
                'usage_frequency': 'common'
            })

        # Check for pytest
        if pyproject and 'pytest' in pyproject:
            patterns.append({
                'pattern_type': 'testing',
                'pattern_name': 'Pytest Testing Framework',
                'description': 'Uses pytest for testing',
                'language': language,
                'usage_frequency': 'very-common'
            })

    return patterns

def process_repository(repo_row: Dict) -> int:
    """
    Process a single repository to extract patterns and rules

    Returns:
        Number of items extracted
    """
    repo_id = repo_row['id']
    repo_full_name = repo_row['repo_full_name']
    language = repo_row['language']

    print(f"\n📦 Processing {repo_full_name} ({language})...")

    extracted_count = 0
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Extract rules from CONTRIBUTING.md
        contributing = fetch_github_file(repo_full_name, 'CONTRIBUTING.md')
        if contributing:
            rules = extract_rules_from_contributing(contributing, repo_id, repo_full_name)

            for rule in rules:
                try:
                    cursor.execute("""
                        INSERT INTO coding_rules (
                            repo_id,
                            rule_category,
                            rule_title,
                            rule_description,
                            extracted_from,
                            confidence_score,
                            applies_to_languages
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (
                        rule['repo_id'],
                        rule['category'],
                        rule['title'],
                        rule['description'],
                        rule['extracted_from'],
                        rule['confidence'],
                        [language] if language else []
                    ))
                    extracted_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error inserting rule: {e}")

        # 2. Extract rules from README
        readme = fetch_github_file(repo_full_name, 'README.md')
        if readme:
            rules = extract_rules_from_readme(readme, repo_id, repo_full_name)

            for rule in rules[:5]:  # Limit README rules
                try:
                    cursor.execute("""
                        INSERT INTO coding_rules (
                            repo_id,
                            rule_category,
                            rule_title,
                            rule_description,
                            extracted_from,
                            confidence_score,
                            applies_to_languages
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (
                        rule['repo_id'],
                        rule['category'],
                        rule['title'],
                        rule['description'],
                        rule['extracted_from'],
                        rule['confidence'],
                        [language] if language else []
                    ))
                    extracted_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error inserting rule: {e}")

        # 3. Extract coding patterns from project structure
        patterns = extract_coding_patterns(repo_full_name, language)

        for pattern in patterns:
            try:
                cursor.execute("""
                    INSERT INTO coding_patterns (
                        repo_id,
                        pattern_type,
                        pattern_name,
                        description,
                        language,
                        usage_frequency
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    repo_id,
                    pattern['pattern_type'],
                    pattern['pattern_name'],
                    pattern['description'],
                    pattern['language'],
                    pattern['usage_frequency']
                ))
                extracted_count += 1
            except Exception as e:
                print(f"   ⚠️  Error inserting pattern: {e}")

        # Mark repo as enriched
        cursor.execute("""
            UPDATE github_repositories
            SET enriched = TRUE, enriched_at = NOW()
            WHERE id = %s;
        """, (repo_id,))

        conn.commit()
        print(f"   ✅ Extracted {extracted_count} items")

    except Exception as e:
        print(f"   ❌ Error processing {repo_full_name}: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

        # Be nice to GitHub API
        time.sleep(1)

    return extracted_count

def get_repos_to_process(limit: int = 100) -> List[Dict]:
    """Get repositories that haven't been enriched yet"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, repo_full_name, language, stars
        FROM github_repositories
        WHERE enriched = FALSE AND language IS NOT NULL
        ORDER BY stars DESC
        LIMIT %s;
    """, (limit,))

    repos = cursor.fetchall()
    cursor.close()
    conn.close()

    return repos

def show_extraction_summary():
    """Show summary of extracted patterns and rules"""
    print(f"\n{'='*80}")
    print("  EXTRACTION SUMMARY")
    print(f"{'='*80}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total patterns
    cursor.execute("SELECT COUNT(*) as count FROM coding_patterns;")
    total_patterns = cursor.fetchone()['count']

    # Total rules
    cursor.execute("SELECT COUNT(*) as count FROM coding_rules;")
    total_rules = cursor.fetchone()['count']

    # By language
    cursor.execute("""
        SELECT language, COUNT(*) as count
        FROM coding_patterns
        WHERE language IS NOT NULL
        GROUP BY language
        ORDER BY count DESC
        LIMIT 10;
    """)
    patterns_by_lang = cursor.fetchall()

    # By rule category
    cursor.execute("""
        SELECT rule_category, COUNT(*) as count
        FROM coding_rules
        GROUP BY rule_category
        ORDER BY count DESC;
    """)
    rules_by_category = cursor.fetchall()

    print(f"\n📊 Total coding patterns: {total_patterns:,}")
    print(f"📊 Total coding rules: {total_rules:,}")

    print(f"\n🔤 Patterns by Language:")
    for row in patterns_by_lang:
        print(f"   • {row['language']}: {row['count']} patterns")

    print(f"\n📏 Rules by Category:")
    for row in rules_by_category:
        print(f"   • {row['rule_category']}: {row['count']} rules")

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")

def main():
    """Main extraction process"""
    print("\n" + "="*80)
    print(" "*20 + "GITHUB PATTERN EXTRACTOR")
    print("="*80)

    # Get repos to process
    repos = get_repos_to_process(limit=200)  # Process top 200 repos

    if not repos:
        print("\n✅ All repositories already processed!")
        show_extraction_summary()
        return

    print(f"\n📚 Found {len(repos)} repositories to process")

    start_time = time.time()
    total_extracted = 0

    for i, repo in enumerate(repos, 1):
        try:
            count = process_repository(repo)
            total_extracted += count

            if i % 10 == 0:
                print(f"\n{'='*80}")
                print(f"   Progress: {i}/{len(repos)} repos processed")
                print(f"   Total items extracted: {total_extracted}")
                print(f"{'='*80}")

        except Exception as e:
            print(f"❌ Error processing repo: {e}")
            continue

    elapsed = time.time() - start_time

    print(f"\n{'='*80}")
    print(f"✅ Extraction complete!")
    print(f"   Repositories processed: {len(repos)}")
    print(f"   Total items extracted: {total_extracted}")
    print(f"   Time elapsed: {elapsed/60:.1f} minutes")
    print(f"{'='*80}")

    # Show summary
    show_extraction_summary()

if __name__ == "__main__":
    main()
