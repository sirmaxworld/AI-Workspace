#!/usr/bin/env python3
"""
Smithery.ai MCP Directory Scraper
Extracts all MCP servers from Smithery.ai and organizes by category and usage
"""

import json
import time
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import subprocess

def fetch_smithery_page(page_num: int = 1, filter_query: str = "") -> Optional[str]:
    """
    Fetch a page from Smithery.ai using WebFetch via subprocess

    Args:
        page_num: Page number to fetch (1-indexed)
        filter_query: Optional filter query (e.g., "is:deployed is:verified")

    Returns:
        str: Page content or None if failed
    """
    if filter_query:
        url = f"https://smithery.ai/search?q={filter_query}&page={page_num}"
    else:
        url = f"https://smithery.ai/search?page={page_num}"

    print(f"  Fetching page {page_num}... ", end='', flush=True)

    # Use curl instead of WebFetch for simpler scraping
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and result.stdout:
            print(f"✓ ({len(result.stdout)} bytes)")
            return result.stdout
        else:
            print(f"✗ (failed with code {result.returncode})")
            return None

    except Exception as e:
        print(f"✗ ({e})")
        return None


def parse_server_from_html(html_block: str) -> Optional[Dict]:
    """
    Parse a single MCP server entry from HTML

    This is a simplified parser - in production you'd use BeautifulSoup
    """
    server = {}

    # Extract package name (look for @org/package-name pattern)
    package_match = re.search(r'@[\w-]+/[\w-]+', html_block)
    if package_match:
        server['package'] = package_match.group(0)

    # Extract use count (look for numbers followed by 'uses' or 'k')
    use_match = re.search(r'([\d.]+)k?\s*(?:uses|downloads)', html_block, re.IGNORECASE)
    if use_match:
        uses_str = use_match.group(1)
        if 'k' in use_match.group(0):
            server['uses'] = float(uses_str) * 1000
        else:
            server['uses'] = float(uses_str)
    else:
        server['uses'] = 0

    # Extract deployment type (Remote/Local)
    if 'Remote' in html_block:
        server['deployment'] = 'remote'
    elif 'Local' in html_block:
        server['deployment'] = 'local'
    else:
        server['deployment'] = 'unknown'

    # Extract name (typically before package identifier)
    name_match = re.search(r'<h[23][^>]*>([^<]+)</h[23]>', html_block)
    if name_match:
        server['name'] = name_match.group(1).strip()

    # Extract description
    desc_match = re.search(r'<p[^>]*>([^<]+)</p>', html_block)
    if desc_match:
        server['description'] = desc_match.group(1).strip()

    # Only return if we at least got a package name
    return server if 'package' in server else None


def scrape_all_servers(max_pages: int = 50, filter_query: str = "") -> List[Dict]:
    """
    Scrape all MCP servers from Smithery.ai

    Args:
        max_pages: Maximum number of pages to scrape
        filter_query: Optional filter (e.g., "is:deployed is:verified")

    Returns:
        List of server dictionaries
    """
    print(f"\n{'='*80}")
    print(f"🔍 SMITHERY.AI MCP DIRECTORY SCRAPER")
    print(f"{'='*80}\n")

    if filter_query:
        print(f"Filter: {filter_query}")
    print(f"Max pages: {max_pages}\n")

    all_servers = []
    empty_pages = 0

    for page_num in range(1, max_pages + 1):
        html = fetch_smithery_page(page_num, filter_query)

        if not html:
            empty_pages += 1
            if empty_pages >= 3:
                print(f"\n⚠️  Got {empty_pages} empty pages, stopping...")
                break
            continue

        # Reset empty page counter on success
        empty_pages = 0

        # Split HTML into potential server blocks (very rough approach)
        # In production, use BeautifulSoup or similar
        server_blocks = re.split(r'(?=@[\w-]+/[\w-]+)', html)

        page_servers = []
        for block in server_blocks:
            server = parse_server_from_html(block)
            if server and server not in all_servers:
                page_servers.append(server)

        print(f"    → Extracted {len(page_servers)} servers from page {page_num}")
        all_servers.extend(page_servers)

        # Rate limiting
        time.sleep(1)

    print(f"\n{'='*80}")
    print(f"✅ SCRAPING COMPLETE")
    print(f"{'='*80}\n")
    print(f"Total servers extracted: {len(all_servers)}\n")

    return all_servers


def categorize_servers(servers: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Categorize servers based on keywords in name/description
    """
    categories = {
        'web_search': [],
        'browser_automation': [],
        'database': [],
        'memory': [],
        'weather': [],
        'filesystem': [],
        'api_integration': [],
        'developer_tools': [],
        'ai_models': [],
        'data_extraction': [],
        'communication': [],
        'finance': [],
        'education': [],
        'security': [],
        'other': []
    }

    category_keywords = {
        'web_search': ['search', 'google', 'web', 'crawl', 'scrape'],
        'browser_automation': ['browser', 'playwright', 'puppeteer', 'automation'],
        'database': ['database', 'postgres', 'mysql', 'sql', 'supabase', 'mongodb'],
        'memory': ['memory', 'context', 'recall', 'letta'],
        'weather': ['weather', 'climate', 'forecast'],
        'filesystem': ['file', 'filesystem', 'directory', 'storage'],
        'api_integration': ['api', 'rest', 'graphql', 'webhook'],
        'developer_tools': ['git', 'github', 'code', 'development', 'debugging'],
        'ai_models': ['ai', 'llm', 'model', 'openai', 'anthropic'],
        'data_extraction': ['extract', 'parse', 'ocr', 'pdf', 'document'],
        'communication': ['slack', 'email', 'chat', 'messaging', 'discord'],
        'finance': ['crypto', 'blockchain', 'bitcoin', 'trading', 'finance'],
        'education': ['learn', 'education', 'quiz', 'tutorial', 'course'],
        'security': ['security', 'auth', 'encryption', 'vault']
    }

    for server in servers:
        text = (server.get('name', '') + ' ' + server.get('description', '')).lower()

        categorized = False
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories[category].append(server)
                categorized = True
                break

        if not categorized:
            categories['other'].append(server)

    return categories


def generate_rankings(servers: List[Dict], top_n: int = 100) -> List[Dict]:
    """
    Generate top N ranking by usage
    """
    sorted_servers = sorted(servers, key=lambda x: x.get('uses', 0), reverse=True)
    return sorted_servers[:top_n]


def save_mcp_directory(servers: List[Dict], categories: Dict, output_dir: str = "/Users/yourox/AI-Workspace/data/mcp_directory"):
    """
    Save MCP directory to structured files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()

    # Save all servers
    all_servers_file = output_path / "all_servers.json"
    with open(all_servers_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'total_count': len(servers),
            'servers': servers
        }, f, indent=2)

    print(f"✅ Saved all servers to: {all_servers_file}")

    # Save by category
    categories_file = output_path / "by_category.json"
    category_summary = {
        'timestamp': timestamp,
        'categories': {
            cat: {
                'count': len(servers_list),
                'servers': servers_list
            }
            for cat, servers_list in categories.items()
            if servers_list
        }
    }

    with open(categories_file, 'w') as f:
        json.dump(category_summary, f, indent=2)

    print(f"✅ Saved categorized servers to: {categories_file}")

    # Save top 100
    top_100 = generate_rankings(servers, 100)
    top_100_file = output_path / "top_100_by_usage.json"
    with open(top_100_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'count': len(top_100),
            'servers': top_100
        }, f, indent=2)

    print(f"✅ Saved top 100 to: {top_100_file}")

    # Save top 500
    top_500 = generate_rankings(servers, 500)
    top_500_file = output_path / "top_500_by_usage.json"
    with open(top_500_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'count': len(top_500),
            'servers': top_500
        }, f, indent=2)

    print(f"✅ Saved top 500 to: {top_500_file}")

    # Save summary statistics
    stats_file = output_path / "statistics.json"
    stats = {
        'timestamp': timestamp,
        'total_servers': len(servers),
        'by_deployment': {
            'remote': len([s for s in servers if s.get('deployment') == 'remote']),
            'local': len([s for s in servers if s.get('deployment') == 'local']),
            'unknown': len([s for s in servers if s.get('deployment') == 'unknown'])
        },
        'by_category': {cat: len(servers_list) for cat, servers_list in categories.items()},
        'total_usage': sum(s.get('uses', 0) for s in servers),
        'avg_usage': sum(s.get('uses', 0) for s in servers) / len(servers) if servers else 0,
        'top_10_servers': [
            {'name': s.get('name'), 'package': s.get('package'), 'uses': s.get('uses')}
            for s in generate_rankings(servers, 10)
        ]
    }

    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"✅ Saved statistics to: {stats_file}")


def main():
    """Main execution"""

    # Scrape all servers (try up to 50 pages)
    servers = scrape_all_servers(max_pages=50, filter_query="")

    if not servers:
        print("❌ No servers extracted. Check network connection or HTML parsing.")
        return

    # Categorize servers
    print(f"\n📊 Categorizing {len(servers)} servers...")
    categories = categorize_servers(servers)

    # Print category summary
    print(f"\n{'='*80}")
    print("📂 CATEGORY BREAKDOWN")
    print(f"{'='*80}\n")
    for category, servers_list in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        if servers_list:
            print(f"  {category:.<30} {len(servers_list):>4} servers")

    # Save everything
    print(f"\n💾 Saving data...")
    save_mcp_directory(servers, categories)

    print(f"\n{'='*80}")
    print("✅ MCP DIRECTORY EXTRACTION COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
