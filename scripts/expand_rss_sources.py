#!/usr/bin/env python3
"""
Expand RSS Collector to include all high-priority sources from catalog

Generates configuration for rss_news_collector.py from content_sources_catalog.json
"""

import json
from pathlib import Path

# Read catalog
catalog_path = Path("/Users/yourox/AI-Workspace/config/content_sources_catalog.json")
with open(catalog_path) as f:
    catalog = json.load(f)

# Extract RSS sources with configurations
rss_sources = {}
source_id_counter = 0

print("Extracting RSS sources from catalog...")
print()

for category_id, category in catalog['categories'].items():
    for source in category['sources']:
        if source.get('has_rss') and source.get('extraction_method') == 'rss':
            # Generate source ID
            source_id = source['name'].lower().replace(' ', '_').replace("'", '').replace('(', '').replace(')', '').replace('.', '').replace('/', '_')

            # Determine RSS URL (need to find the actual feed URL)
            url = source.get('url', '')

            # Common RSS feed patterns
            possible_rss_urls = [
                f"{url}/feed",
                f"{url}/rss",
                f"{url}/feed/",
                f"{url}/rss.xml",
                f"{url}/feeds/posts/default",
            ]

            # Set priority weight
            priority_weights = {
                'critical': 0.9,
                'high': 0.7,
                'medium': 0.5,
                'low': 0.3
            }

            priority = category.get('priority', 'medium')
            base_weight = priority_weights.get(priority, 0.5)

            # Set rate limits
            rate_limits = {
                'critical': 50,
                'high': 20,
                'medium': 10,
                'low': 5
            }

            rate_limit = rate_limits.get(priority, 10)

            rss_sources[source_id] = {
                "name": source['name'],
                "domain": url.replace('https://', '').replace('http://', '').split('/')[0],
                "rss_url": possible_rss_urls[0],  # Will need to be verified
                "category": source.get('primary_content', category_id),
                "priority": priority,
                "base_weight": base_weight,
                "rate_limit_per_day": rate_limit,
                "min_word_count": 30
            }

            if category.get('priority') in ['critical', 'high']:
                source_id_counter += 1

# Output Python dictionary
print(f"Found {len(rss_sources)} RSS sources ({source_id_counter} high-priority)")
print()
print("="*70)
print("TIER2_SOURCES Configuration")
print("="*70)
print()
print("TIER2_SOURCES = {")

for source_id, config in sorted(rss_sources.items()):
    if config['priority'] in ['critical', 'high']:
        print(f'    "{source_id}": {{')
        for key, value in config.items():
            if isinstance(value, str):
                print(f'        "{key}": "{value}",')
            else:
                print(f'        "{key}": {value},')
        print('    },')

print("}")
print()
print(f"Total high-priority sources: {source_id_counter}")
