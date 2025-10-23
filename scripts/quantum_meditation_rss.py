#!/usr/bin/env python3
"""
Quality RSS Collector for Quantum Physics & Meditation
Using RSS feeds for better reliability
"""

import os
import sys
sys.path.append('/Users/yourox/AI-Workspace')

from scripts.rss_expanded_collector import ExpandedRSSCollector

# HIGH-QUALITY SOURCES WITH RSS FEEDS
QUANTUM_RSS_SOURCES = {
    "sciencedaily_quantum": {
        "name": "ScienceDaily Quantum Physics",
        "domain": "sciencedaily.com",
        "rss_url": "https://www.sciencedaily.com/rss/matter_energy/quantum_physics.xml",
        "category": "quantum_physics",
        "priority": "high",
        "base_weight": 0.9
    },
    "quanta_magazine": {
        "name": "Quanta Magazine",
        "domain": "quantamagazine.org",
        "rss_url": "https://www.quantamagazine.org/feed/",
        "category": "quantum_physics",
        "priority": "high",
        "base_weight": 0.9
    },
    "physorg_quantum": {
        "name": "Phys.org Quantum",
        "domain": "phys.org",
        "rss_url": "https://phys.org/rss-feed/science-news/quantum-physics/",
        "category": "quantum_physics",
        "priority": "high",
        "base_weight": 0.8
    },
    "scientific_american": {
        "name": "Scientific American",
        "domain": "scientificamerican.com",
        "rss_url": "https://rss.scientificamerican.com/ScientificAmerican-Global",
        "category": "quantum_physics",
        "priority": "high",
        "base_weight": 0.9
    }
}

MEDITATION_RSS_SOURCES = {
    "tinybuddha": {
        "name": "Tiny Buddha",
        "domain": "tinybuddha.com",
        "rss_url": "https://tinybuddha.com/feed/",
        "category": "meditation",
        "priority": "high",
        "base_weight": 0.8
    },
    "mindful_org": {
        "name": "Mindful.org",
        "domain": "mindful.org",
        "rss_url": "https://www.mindful.org/feed/",
        "category": "meditation",
        "priority": "high",
        "base_weight": 0.8
    },
    "buddhify": {
        "name": "Buddhify Blog",
        "domain": "buddhify.com",
        "rss_url": "https://buddhify.com/blog/feed/",
        "category": "meditation",
        "priority": "medium",
        "base_weight": 0.7
    },
    "chopra_meditation": {
        "name": "Chopra Meditation",
        "domain": "chopra.com",
        "rss_url": "https://chopra.com/articles/meditation-mindfulness/feed",
        "category": "meditation",
        "priority": "high",
        "base_weight": 0.8
    },
    "gaia": {
        "name": "Gaia Meditation",
        "domain": "gaia.com",
        "rss_url": "https://www.gaia.com/lp/rss/meditation",
        "category": "meditation",
        "priority": "medium",
        "base_weight": 0.7
    }
}

ALL_RSS_SOURCES = {**QUANTUM_RSS_SOURCES, **MEDITATION_RSS_SOURCES}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Collect quality quantum physics and meditation via RSS')
    parser.add_argument('--quantum', action='store_true',
                        help='Collect quantum physics sources')
    parser.add_argument('--meditation', action='store_true',
                        help='Collect meditation sources')
    parser.add_argument('--all', action='store_true',
                        help='Collect all sources')
    parser.add_argument('--limit', type=int, default=100,
                        help='Max articles per source (default: 100)')

    args = parser.parse_args()

    if args.all:
        sources = ALL_RSS_SOURCES
        collector = ExpandedRSSCollector(sources_config=sources)
        results = collector.collect_all_sources(
            limit_per_source=args.limit,
            max_age_days=180,
            verbose=True
        )

    elif args.quantum:
        collector = ExpandedRSSCollector(sources_config=QUANTUM_RSS_SOURCES)
        results = collector.collect_all_sources(
            limit_per_source=args.limit,
            max_age_days=180,
            verbose=True
        )

    elif args.meditation:
        collector = ExpandedRSSCollector(sources_config=MEDITATION_RSS_SOURCES)
        results = collector.collect_all_sources(
            limit_per_source=args.limit,
            max_age_days=180,
            verbose=True
        )

    else:
        parser.print_help()

    # Print summary
    if 'results' in locals():
        total = sum(results.values()) if results else 0
        successful = sum(1 for v in results.values() if v > 0) if results else 0
        print(f"\n✅ Collected {total} articles from {successful}/{len(results)} sources")
