#!/usr/bin/env python3
"""
NPM MCP Registry Scraper
Extracts all MCP servers from the official npm registry
Much more reliable than scraping Smithery HTML!
"""

import json
import time
import requests
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def search_npm_mcp_packages(query: str = "mcp", size: int = 250, offset: int = 0) -> Dict:
    """
    Search npm registry for MCP packages

    Args:
        query: Search query
        size: Results per page (max 250)
        offset: Pagination offset

    Returns:
        dict: Search results from npm registry
    """
    url = f"https://registry.npmjs.org/-/v1/search"
    params = {
        'text': query,
        'size': size,
        'from': offset
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching from npm: {e}")
        return {}


def fetch_all_mcp_packages() -> List[Dict]:
    """
    Fetch ALL MCP packages from npm registry

    Returns:
        List of package dictionaries with full metadata
    """
    print(f"\n{'='*80}")
    print(f"📦 NPM MCP REGISTRY SCRAPER")
    print(f"{'='*80}\n")

    all_packages = []
    search_queries = [
        "@modelcontextprotocol",  # Official packages
        "mcp-server",            # Common naming pattern
        "mcp server",            # Phrase search
        "model context protocol", # Full name
    ]

    seen_packages = set()

    for query in search_queries:
        print(f"\n🔍 Searching for: '{query}'")
        offset = 0
        size = 250  # Max per page

        while True:
            print(f"  Fetching page {offset//size + 1}... ", end='', flush=True)

            results = search_npm_mcp_packages(query, size, offset)

            if not results or 'objects' not in results:
                print("✗ (no results)")
                break

            objects = results.get('objects', [])
            total = results.get('total', 0)

            if not objects:
                print("✗ (no more results)")
                break

            print(f"✓ (found {len(objects)} packages, {total} total)")

            # Extract package info
            for obj in objects:
                pkg = obj.get('package', {})
                pkg_name = pkg.get('name')

                if pkg_name and pkg_name not in seen_packages:
                    seen_packages.add(pkg_name)

                    package_data = {
                        'name': pkg_name,
                        'version': pkg.get('version'),
                        'description': pkg.get('description', ''),
                        'author': pkg.get('author', {}).get('name') if isinstance(pkg.get('author'), dict) else str(pkg.get('author', '')),
                        'keywords': pkg.get('keywords', []),
                        'npm_url': f"https://www.npmjs.com/package/{pkg_name}",
                        'repository': pkg.get('links', {}).get('repository', ''),
                        'homepage': pkg.get('links', {}).get('homepage', ''),
                        'npm': pkg.get('links', {}).get('npm', ''),
                        'downloads_last_month': pkg.get('downloads', {}).get('monthly', 0) if isinstance(pkg.get('downloads'), dict) else 0,
                        'date_published': pkg.get('date'),
                        'publisher': pkg.get('publisher', {}).get('username') if isinstance(pkg.get('publisher'), dict) else '',
                        'score': obj.get('score', {}),
                        'search_query': query
                    }

                    all_packages.append(package_data)

            # Check if we've fetched all results
            if offset + size >= total:
                print(f"  ✅ Fetched all {total} results for '{query}'")
                break

            offset += size
            time.sleep(0.5)  # Rate limiting

    print(f"\n{'='*80}")
    print(f"✅ SCRAPING COMPLETE")
    print(f"{'='*80}\n")
    print(f"Total unique packages: {len(all_packages)}\n")

    return all_packages


def categorize_mcp_packages(packages: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Categorize MCP packages based on keywords and descriptions
    """
    categories = {
        'official': [],          # @modelcontextprotocol/*
        'web_search': [],
        'browser_automation': [],
        'database': [],
        'file_system': [],
        'api_integration': [],
        'developer_tools': [],
        'ai_models': [],
        'data_extraction': [],
        'communication': [],
        'productivity': [],
        'finance': [],
        'security': [],
        'other': []
    }

    category_patterns = {
        'official': lambda p: p['name'].startswith('@modelcontextprotocol/'),
        'web_search': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                   for kw in ['search', 'google', 'web', 'crawl', 'scrape']),
        'browser_automation': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                           for kw in ['browser', 'playwright', 'puppeteer', 'automation']),
        'database': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                 for kw in ['database', 'postgres', 'mysql', 'sql', 'mongodb']),
        'file_system': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                     for kw in ['file', 'filesystem', 'directory', 'storage']),
        'api_integration': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                        for kw in ['api', 'rest', 'graphql', 'webhook']),
        'developer_tools': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                        for kw in ['git', 'github', 'code', 'development']),
        'ai_models': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                  for kw in ['ai', 'llm', 'model', 'openai', 'anthropic']),
        'data_extraction': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                        for kw in ['extract', 'parse', 'pdf', 'document']),
        'communication': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                      for kw in ['slack', 'email', 'chat', 'messaging']),
        'productivity': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                     for kw in ['calendar', 'task', 'note', 'todo']),
        'finance': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                for kw in ['crypto', 'blockchain', 'bitcoin', 'finance']),
        'security': lambda p: any(kw in (p['description'] + ' '.join(p['keywords'])).lower()
                                 for kw in ['security', 'auth', 'encryption', 'vault']),
    }

    for pkg in packages:
        categorized = False
        for category, pattern_func in category_patterns.items():
            if pattern_func(pkg):
                categories[category].append(pkg)
                categorized = True
                break

        if not categorized:
            categories['other'].append(pkg)

    return categories


def save_mcp_directory(packages: List[Dict], categories: Dict, output_dir: str = "/Users/yourox/AI-Workspace/data/mcp_directory"):
    """
    Save MCP directory to structured files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()

    # Save all packages
    all_packages_file = output_path / "all_packages.json"
    with open(all_packages_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'total_count': len(packages),
            'source': 'npm_registry',
            'packages': packages
        }, f, indent=2)

    print(f"✅ Saved all packages to: {all_packages_file}")

    # Save by category
    categories_file = output_path / "by_category.json"
    category_summary = {
        'timestamp': timestamp,
        'categories': {
            cat: {
                'count': len(pkgs),
                'packages': pkgs
            }
            for cat, pkgs in categories.items()
            if pkgs
        }
    }

    with open(categories_file, 'w') as f:
        json.dump(category_summary, f, indent=2)

    print(f"✅ Saved categorized packages to: {categories_file}")

    # Sort by downloads
    sorted_by_downloads = sorted(packages, key=lambda x: x.get('downloads_last_month', 0), reverse=True)

    # Save top 100
    top_100_file = output_path / "top_100_by_downloads.json"
    with open(top_100_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'count': min(100, len(sorted_by_downloads)),
            'packages': sorted_by_downloads[:100]
        }, f, indent=2)

    print(f"✅ Saved top 100 to: {top_100_file}")

    # Save top 500
    top_500_file = output_path / "top_500_by_downloads.json"
    with open(top_500_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'count': min(500, len(sorted_by_downloads)),
            'packages': sorted_by_downloads[:500]
        }, f, indent=2)

    print(f"✅ Saved top 500 to: {top_500_file}")

    # Save statistics
    stats_file = output_path / "statistics.json"
    total_downloads = sum(p.get('downloads_last_month', 0) for p in packages)

    stats = {
        'timestamp': timestamp,
        'total_packages': len(packages),
        'by_category': {cat: len(pkgs) for cat, pkgs in categories.items()},
        'total_downloads_last_month': total_downloads,
        'avg_downloads': total_downloads / len(packages) if packages else 0,
        'top_10_packages': [
            {'name': p['name'], 'downloads': p.get('downloads_last_month', 0), 'description': p.get('description', '')}
            for p in sorted_by_downloads[:10]
        ],
        'official_packages_count': len([p for p in packages if p['name'].startswith('@modelcontextprotocol/')])
    }

    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"✅ Saved statistics to: {stats_file}")


def main():
    """Main execution"""

    # Fetch all MCP packages from npm
    packages = fetch_all_mcp_packages()

    if not packages:
        print("❌ No packages extracted. Check network connection.")
        return

    # Categorize packages
    print(f"\n📊 Categorizing {len(packages)} packages...")
    categories = categorize_mcp_packages(packages)

    # Print category summary
    print(f"\n{'='*80}")
    print("📂 CATEGORY BREAKDOWN")
    print(f"{'='*80}\n")
    for category, pkgs in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        if pkgs:
            print(f"  {category:.<30} {len(pkgs):>4} packages")

    # Save everything
    print(f"\n💾 Saving data...")
    save_mcp_directory(packages, categories)

    print(f"\n{'='*80}")
    print("✅ MCP DIRECTORY EXTRACTION COMPLETE")
    print(f"{'='*80}\n")
    print(f"📍 Data saved to: /Users/yourox/AI-Workspace/data/mcp_directory/\n")


if __name__ == "__main__":
    main()
