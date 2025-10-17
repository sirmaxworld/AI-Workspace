#!/usr/bin/env python3
"""Test Pinkbike collector with direct article URL"""

import sys
sys.path.insert(0, '/Users/yourox/AI-Workspace')

from pathlib import Path
from domains.cycling_trends.pinkbike_collector import PinkbikeCollector

# Initialize collector
domain_path = Path("/Users/yourox/AI-Workspace/domains/cycling_trends")
collector = PinkbikeCollector(domain_path)

# Test with a known Pinkbike review article (example URL)
test_url = "https://www.pinkbike.com/news/2024-santa-cruz-nomad-review.html"

print(f"\n{'='*70}")
print("Testing with direct article URL")
print(f"{'='*70}\n")

# Extract the article
article_data = collector.extract_article_content(test_url)

if article_data and article_data.get('status') == 'success':
    # Save it
    collector.save_article(article_data)

    # Print summary
    print(f"\n{'='*70}")
    print("✅ SUCCESS - Article Extracted!")
    print(f"{'='*70}")
    print(f"Title: {article_data.get('title', 'N/A')[:60]}")
    print(f"Author: {article_data.get('author', {}).get('name', 'N/A')}")
    print(f"Content Length: {len(article_data.get('content', ''))} chars")
    print(f"Comments: {article_data.get('engagement', {}).get('comment_count', 0)}")
    print(f"Views: {article_data.get('engagement', {}).get('view_count', 0)}")
    print(f"Images: {article_data.get('media', {}).get('image_count', 0)}")
    print(f"Videos: {article_data.get('media', {}).get('video_count', 0)}")
else:
    print(f"❌ Failed: {article_data.get('error', 'Unknown error')}")
