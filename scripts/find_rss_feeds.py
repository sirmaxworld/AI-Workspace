#!/usr/bin/env python3
"""
Find and validate RSS feed URLs for all high-priority sources

Tests common RSS feed patterns and validates they work.
"""

import requests
import feedparser
from urllib.parse import urljoin

# Common RSS feed patterns to test
RSS_PATTERNS = [
    '/feed',
    '/feed/',
    '/rss',
    '/rss/',
    '/rss.xml',
    '/feed.xml',
    '/feeds/posts/default',
    '/blog/feed',
    '/blog/rss',
    '/index.xml',
    '/atom.xml',
]

def find_rss_feed(base_url, source_name):
    """
    Try to find working RSS feed for a website

    Args:
        base_url: Base website URL
        source_name: Source name for logging

    Returns:
        str: Working RSS URL or None
    """
    print(f"\n🔍 Testing: {source_name}")
    print(f"   Base: {base_url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    for pattern in RSS_PATTERNS:
        test_url = urljoin(base_url, pattern)

        try:
            response = requests.get(test_url, headers=headers, timeout=10)

            if response.status_code == 200:
                # Try to parse as RSS
                feed = feedparser.parse(response.content)

                if len(feed.entries) > 0:
                    print(f"   ✅ Found: {test_url} ({len(feed.entries)} entries)")
                    return test_url

        except Exception as e:
            continue

    print(f"   ❌ No RSS feed found")
    return None

# Test high-priority sources
PRIORITY_SOURCES = {
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/",
    "HubSpot Blog": "https://blog.hubspot.com",
    "Seth Godin's Blog": "https://seths.blog",
    "Neil Patel Blog": "https://neilpatel.com/blog",
    "Social Media Examiner": "https://www.socialmediaexaminer.com",
    "Small Business Trends": "https://smallbiztrends.com",
    "Moz Blog": "https://moz.com/blog",
    "Hacker News": "https://news.ycombinator.com",  # Has API, not RSS
    "MIT Technology Review": "https://www.technologyreview.com",
    "Hugging Face Blog": "https://huggingface.co/blog",
    "AI News": "https://www.artificialintelligence-news.com",
    "Times of AI": "https://www.timesofai.com",
    "Google AI Blog": "https://blog.google/technology/ai/",
    "MarkTechPost": "https://www.marktechpost.com",
    "Inc.com": "https://www.inc.com",
    "Forbes": "https://www.forbes.com",
    "Fast Company": "https://www.fastcompany.com",
    "Entrepreneur": "https://www.entrepreneur.com",
    "Reuters Business": "https://www.reuters.com/business",
    "Knowledge @ Wharton": "https://knowledge.wharton.upenn.edu",
    "Marketing Profs": "https://www.marketingprofs.com",
    "Search Engine Journal": "https://www.searchenginejournal.com",
    "Copyblogger": "https://copyblogger.com",
    "Content Marketing Institute": "https://contentmarketinginstitute.com",
    "Buffer Resources": "https://buffer.com/resources",
    "Sales Hacker": "https://www.saleshacker.com",
}

if __name__ == "__main__":
    print("="*70)
    print("RSS FEED DISCOVERY")
    print("="*70)

    found_feeds = {}
    notfound = []

    for name, url in PRIORITY_SOURCES.items():
        feed_url = find_rss_feed(url, name)
        if feed_url:
            found_feeds[name] = feed_url
        else:
            not_found.append(name)

    print("\n" + "="*70)
    print(f"RESULTS: {len(found_feeds)}/{len(PRIORITY_SOURCES)} feeds found")
    print("="*70)

    print("\n✅ Working RSS Feeds:")
    for name, url in found_feeds.items():
        print(f"   • {name:35} {url}")

    if not_found:
        print("\n❌ No RSS Found (may need manual lookup or API):")
        for name in not_found:
            print(f"   • {name}")
