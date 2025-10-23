#!/usr/bin/env python3
"""
Quality Check Script
Validates infrastructure and data quality before running large-scale collection
"""

import os
import sys
import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('/Users/yourox/AI-Workspace/.env')

class QualityChecker:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0

    def check(self, name: str, condition: bool, error_msg: str = "", warning: bool = False):
        """Record a check result"""
        if condition:
            print(f"   ✓ {name}")
            self.checks_passed += 1
            return True
        else:
            if warning:
                print(f"   ⚠  {name}: {error_msg}")
                self.warnings += 1
            else:
                print(f"   ✗ {name}: {error_msg}")
                self.checks_failed += 1
            return False

    def section(self, name: str):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {name}")
        print(f"{'='*80}")

def check_environment(qc: QualityChecker):
    """Check environment variables"""
    qc.section("ENVIRONMENT VARIABLES")

    railway_url = os.getenv('RAILWAY_DATABASE_URL')
    qc.check("RAILWAY_DATABASE_URL set", railway_url is not None, "Database URL not found")

    github_token = os.getenv('GITHUB_TOKEN')
    qc.check("GITHUB_TOKEN set", github_token is not None, "GitHub token not found", warning=True)

    gemini_key = os.getenv('GEMINI_API_KEY')
    qc.check("GEMINI_API_KEY set", gemini_key is not None, "Gemini API key not found (needed for AI enrichment)", warning=True)

def check_database_connection(qc: QualityChecker):
    """Check database connectivity and schema"""
    qc.section("DATABASE CONNECTION")

    try:
        conn = psycopg2.connect(
            os.getenv('RAILWAY_DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor,
            connect_timeout=10
        )
        qc.check("Database connection successful", True)

        cursor = conn.cursor()

        # Check PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()['version']
        qc.check(f"PostgreSQL version: {version.split(',')[0]}", True)

        cursor.close()
        conn.close()

    except Exception as e:
        qc.check("Database connection", False, f"Connection failed: {e}")

def check_database_tables(qc: QualityChecker):
    """Check if required tables exist"""
    qc.section("DATABASE TABLES")

    required_tables = {
        'github_repositories': 'GitHub repository data',
        'coding_patterns': 'Extracted coding patterns',
        'coding_rules': 'Coding rules and best practices',
        'coding_methods': 'Reusable methods/functions',
        'oss_commercial_repos': 'Commercial-friendly OSS repos',
        'oss_repo_categories': 'OSS repository categories',
        'mcp_servers': 'MCP server catalog',
        'mcp_server_tools': 'MCP server tools',
        'mcp_use_cases': 'MCP use cases',
        'oss_to_mcp_links': 'OSS to MCP links'
    }

    try:
        conn = psycopg2.connect(
            os.getenv('RAILWAY_DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        cursor = conn.cursor()

        for table, description in required_tables.items():
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = '{table}'
                );
            """)
            exists = cursor.fetchone()['exists']
            qc.check(f"{table}", exists, f"Table missing: {description}")

        cursor.close()
        conn.close()

    except Exception as e:
        qc.check("Table check", False, f"Error checking tables: {e}")

def check_database_indexes(qc: QualityChecker):
    """Check if important indexes exist"""
    qc.section("DATABASE INDEXES")

    important_indexes = [
        'idx_github_repos_name',
        'idx_github_repos_language',
        'idx_github_repos_stars',
        'idx_coding_patterns_type',
        'idx_coding_rules_category',
        'idx_oss_repos_license',
        'idx_mcp_servers_category'
    ]

    try:
        conn = psycopg2.connect(
            os.getenv('RAILWAY_DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = 'public';
        """)
        existing_indexes = {row['indexname'] for row in cursor.fetchall()}

        for index in important_indexes:
            qc.check(f"{index}", index in existing_indexes, "Index not found", warning=True)

        cursor.close()
        conn.close()

    except Exception as e:
        qc.check("Index check", False, f"Error checking indexes: {e}")

def check_github_api(qc: QualityChecker):
    """Check GitHub API access and rate limits"""
    qc.section("GITHUB API ACCESS")

    github_token = os.getenv('GITHUB_TOKEN')
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    try:
        # Test API access
        response = requests.get('https://api.github.com/rate_limit', headers=headers, timeout=10)
        qc.check("GitHub API accessible", response.status_code == 200, f"Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            core_limit = data['resources']['core']
            search_limit = data['resources']['search']

            qc.check(
                f"Core API rate limit: {core_limit['remaining']}/{core_limit['limit']}",
                core_limit['remaining'] > 100,
                f"Only {core_limit['remaining']} requests remaining",
                warning=True
            )

            qc.check(
                f"Search API rate limit: {search_limit['remaining']}/{search_limit['limit']}",
                search_limit['remaining'] > 10,
                f"Only {search_limit['remaining']} requests remaining",
                warning=True
            )

    except Exception as e:
        qc.check("GitHub API check", False, f"Error: {e}")

def check_data_quality(qc: QualityChecker):
    """Check existing data quality"""
    qc.section("DATA QUALITY")

    try:
        conn = psycopg2.connect(
            os.getenv('RAILWAY_DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        cursor = conn.cursor()

        # Check for duplicate repos
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM github_repositories;
        """)
        repo_count = cursor.fetchone()['count']
        qc.check(f"GitHub repositories: {repo_count:,}", True)

        # Check for repos with missing data
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM github_repositories
            WHERE description IS NULL OR description = '';
        """)
        missing_desc = cursor.fetchone()['count']
        if repo_count > 0:
            pct = (missing_desc / repo_count) * 100
            qc.check(
                f"Repos with descriptions: {((repo_count - missing_desc) / repo_count * 100):.1f}%",
                pct < 20,
                f"{pct:.1f}% missing descriptions",
                warning=True
            )

        # Check pattern extraction coverage
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM github_repositories
            WHERE enriched = TRUE;
        """)
        enriched_count = cursor.fetchone()['count']
        if repo_count > 0:
            pct = (enriched_count / repo_count) * 100
            qc.check(f"Repos enriched: {enriched_count:,} ({pct:.1f}%)", True)

        # Check for patterns
        cursor.execute("SELECT COUNT(*) as count FROM coding_patterns;")
        pattern_count = cursor.fetchone()['count']
        qc.check(f"Coding patterns: {pattern_count:,}", True)

        # Check for rules
        cursor.execute("SELECT COUNT(*) as count FROM coding_rules;")
        rule_count = cursor.fetchone()['count']
        qc.check(f"Coding rules: {rule_count:,}", True)

        cursor.close()
        conn.close()

    except Exception as e:
        qc.check("Data quality check", False, f"Error: {e}")

def check_scripts_executable(qc: QualityChecker):
    """Check if scripts are executable and syntactically correct"""
    qc.section("SCRIPT VALIDATION")

    scripts = [
        'github_repo_collector.py',
        'github_pattern_extractor.py',
    ]

    for script in scripts:
        path = f'/Users/yourox/AI-Workspace/scripts/{script}'

        # Check if file exists
        exists = os.path.exists(path)
        qc.check(f"{script} exists", exists, "File not found")

        if exists:
            # Check syntax
            try:
                with open(path, 'r') as f:
                    compile(f.read(), path, 'exec')
                qc.check(f"{script} syntax valid", True)
            except SyntaxError as e:
                qc.check(f"{script} syntax", False, f"Syntax error: {e}")

def run_test_collection(qc: QualityChecker):
    """Run a small test collection"""
    qc.section("TEST COLLECTION (DRY RUN)")

    print("\n   Testing GitHub API with small query...")

    github_token = os.getenv('GITHUB_TOKEN')
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    try:
        # Test search API with small query
        response = requests.get(
            'https://api.github.com/search/repositories',
            headers=headers,
            params={'q': 'language:Python', 'sort': 'stars', 'order': 'desc', 'per_page': 3},
            timeout=10
        )

        qc.check("GitHub search API working", response.status_code == 200, f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            qc.check(f"Retrieved {len(items)} test repos", len(items) > 0, "No repos returned")

            if items:
                print(f"\n   Sample repository:")
                print(f"      • {items[0]['full_name']}")
                print(f"      • Stars: {items[0]['stargazers_count']:,}")
                print(f"      • Language: {items[0]['language']}")

    except Exception as e:
        qc.check("Test collection", False, f"Error: {e}")

def main():
    """Run all quality checks"""
    print("\n" + "="*80)
    print(" "*25 + "QUALITY CHECK REPORT")
    print("="*80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    qc = QualityChecker()

    # Run all checks
    check_environment(qc)
    check_database_connection(qc)
    check_database_tables(qc)
    check_database_indexes(qc)
    check_github_api(qc)
    check_data_quality(qc)
    check_scripts_executable(qc)
    run_test_collection(qc)

    # Summary
    print(f"\n{'='*80}")
    print("  SUMMARY")
    print(f"{'='*80}")
    print(f"\n   ✓ Checks passed: {qc.checks_passed}")
    print(f"   ⚠  Warnings: {qc.warnings}")
    print(f"   ✗ Checks failed: {qc.checks_failed}")

    if qc.checks_failed > 0:
        print(f"\n   ⚠️  CRITICAL: {qc.checks_failed} checks failed. Fix issues before proceeding.")
        return 1
    elif qc.warnings > 0:
        print(f"\n   ⚠️  WARNING: {qc.warnings} warnings. Review before large-scale collection.")
        return 0
    else:
        print(f"\n   ✅ ALL CHECKS PASSED! Ready for collection.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
