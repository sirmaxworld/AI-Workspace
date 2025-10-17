#!/usr/bin/env python3
"""Test Pinkbike collector with real article URLs from search"""

import sys
sys.path.insert(0, '/Users/yourox/AI-Workspace')

from pathlib import Path
from domains.cycling_trends.pinkbike_collector import PinkbikeCollector

# Initialize collector
domain_path = Path("/Users/yourox/AI-Workspace/domains/cycling_trends")
collector = PinkbikeCollector(domain_path)

# Real Pinkbike article URLs from WebSearch
test_articles = [
    "https://www.pinkbike.com/news/review-2024-yt-jeffsy-core-4.html",
    "https://www.pinkbike.com/news/field-test-review-2024-ibis-ripmo-the-revised-classic.html"
]

print(f"\n{'='*70}")
print("🚴 TESTING WITH REAL PINKBIKE ARTICLES")
print(f"{'='*70}\n")

results = []

for i, url in enumerate(test_articles, 1):
    print(f"\n[{i}/{len(test_articles)}] Testing: {url.split('/')[-1][:50]}...")

    article_data = collector.extract_article_content(url)

    if article_data and article_data.get('status') == 'success':
        collector.save_article(article_data)
        results.append(article_data)

        # Print summary
        print(f"\n✅ SUCCESS!")
        print(f"  Title: {article_data.get('title', 'N/A')[:60]}")
        print(f"  Author: {article_data.get('author', {}).get('name', 'N/A')}")
        print(f"  Content: {len(article_data.get('content', ''))} chars")
        print(f"  Comments: {article_data.get('engagement', {}).get('comment_count', 0)}")
        print(f"  Views: {article_data.get('engagement', {}).get('view_count', 0):,}")
        print(f"  Images: {article_data.get('media', {}).get('image_count', 0)}")
        print(f"  Videos: {article_data.get('media', {}).get('video_count', 0)}")
        print(f"  Rating: {article_data.get('rating', 'N/A')}")
    else:
        print(f"❌ Failed: {article_data.get('error', 'Unknown error')}")

print(f"\n{'='*70}")
print(f"✅ TEST COMPLETE - {len(results)}/{len(test_articles)} articles extracted")
print(f"{'='*70}\n")
