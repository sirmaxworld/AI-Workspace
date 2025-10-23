#!/usr/bin/env python3
"""
Expanded RSS News Collector - 26+ Sources

Tier 1 + Tier 2 sources for comprehensive news coverage.

Usage:
    python3 rss_expanded_collector.py --tier 1
    python3 rss_expanded_collector.py --tier 2
    python3 rss_expanded_collector.py --tier all
    python3 rss_expanded_collector.py --historical
"""

import sys
sys.path.append('/Users/yourox/AI-Workspace')

# Import existing collector
from scripts.rss_news_collector import RSSNewsCollector, TIER1_SOURCES
import argparse

# Tier 2: Additional high-priority sources
TIER2_SOURCES = {
    "mittech": {
        "name": "MIT Technology Review",
        "domain": "technologyreview.com",
        "rss_url": "https://www.technologyreview.com/feed/",
        "category": "tech_analysis",
        "priority": "high",
        "base_weight": 0.7,
        "rate_limit_per_day": 15,
        "min_word_count": 50
    },
    "huggingface": {
        "name": "Hugging Face Blog",
        "domain": "huggingface.co",
        "rss_url": "https://huggingface.co/blog/feed.xml",
        "category": "ai_tutorials",
        "priority": "high",
        "base_weight": 0.7,
        "rate_limit_per_day": 10,
        "min_word_count": 50
    },
    "ainews": {
        "name": "AI News",
        "domain": "artificialintelligence-news.com",
        "rss_url": "https://www.artificialintelligence-news.com/feed/",
        "category": "ai_news",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 15,
        "min_word_count": 40
    },
    "timesofai": {
        "name": "Times of AI",
        "domain": "timesofai.com",
        "rss_url": "https://www.timesofai.com/feed/",
        "category": "ai_news",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 15,
        "min_word_count": 40
    },
    "marktechpost": {
        "name": "MarkTechPost",
        "domain": "marktechpost.com",
        "rss_url": "https://www.marktechpost.com/feed/",
        "category": "ai_news",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 20,
        "min_word_count": 40
    },
    "entrepreneur": {
        "name": "Entrepreneur",
        "domain": "entrepreneur.com",
        "rss_url": "https://www.entrepreneur.com/latest.rss",
        "category": "entrepreneurship",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 15,
        "min_word_count": 40
    },
    "fastcompany": {
        "name": "Fast Company",
        "domain": "fastcompany.com",
        "rss_url": "https://www.fastcompany.com/latest/rss",
        "category": "innovation",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 15,
        "min_word_count": 40
    },
    "inc": {
        "name": "Inc.com",
        "domain": "inc.com",
        "rss_url": "https://www.inc.com/rss/",
        "category": "business_news",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 15,
        "min_word_count": 40
    },
    "reuters": {
        "name": "Reuters Business",
        "domain": "reuters.com",
        "rss_url": "https://www.reuters.com/business/feed/",
        "category": "business_news",
        "priority": "high",
        "base_weight": 0.7,
        "rate_limit_per_day": 20,
        "min_word_count": 40
    },
    "wharton": {
        "name": "Knowledge @ Wharton",
        "domain": "knowledge.wharton.upenn.edu",
        "rss_url": "https://knowledge.wharton.upenn.edu/feed/",
        "category": "business_research",
        "priority": "high",
        "base_weight": 0.7,
        "rate_limit_per_day": 10,
        "min_word_count": 50
    },
    "marketingprofs": {
        "name": "Marketing Profs",
        "domain": "marketingprofs.com",
        "rss_url": "https://www.marketingprofs.com/marketing/rss.xml",
        "category": "marketing_training",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 15,
        "min_word_count": 40
    },
    "sej": {
        "name": "Search Engine Journal",
        "domain": "searchenginejournal.com",
        "rss_url": "https://www.searchenginejournal.com/feed/",
        "category": "seo",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 15,
        "min_word_count": 40
    },
    "copyblogger": {
        "name": "Copyblogger",
        "domain": "copyblogger.com",
        "rss_url": "https://copyblogger.com/feed/",
        "category": "copywriting",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 10,
        "min_word_count": 40
    },
    "cmi": {
        "name": "Content Marketing Institute",
        "domain": "contentmarketinginstitute.com",
        "rss_url": "https://contentmarketinginstitute.com/feed/",
        "category": "content_marketing",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 10,
        "min_word_count": 40
    },
    "buffer": {
        "name": "Buffer Resources",
        "domain": "buffer.com",
        "rss_url": "https://buffer.com/resources/feed/",
        "category": "social_media",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 15,
        "min_word_count": 40
    },
    "saleshacker": {
        "name": "Sales Hacker",
        "domain": "saleshacker.com",
        "rss_url": "https://www.saleshacker.com/feed/",
        "category": "modern_sales",
        "priority": "medium",
        "base_weight": 0.5,
        "rate_limit_per_day": 10,
        "min_word_count": 40
    },
    "salesblog": {
        "name": "The Sales Blog",
        "domain": "thesalesblog.com",
        "rss_url": "https://www.thesalesblog.com/feed/",
        "category": "b2b_sales",
        "priority": "medium",
        "base_weight": 0.5,
        "rate_limit_per_day": 10,
        "min_word_count": 40
    },
    "heinzmarketing": {
        "name": "Heinz Marketing",
        "domain": "heinzmarketing.com",
        "rss_url": "https://www.heinzmarketing.com/blog/feed/",
        "category": "b2b_marketing",
        "priority": "medium",
        "base_weight": 0.5,
        "rate_limit_per_day": 10,
        "min_word_count": 40
    },
    "predictablerevenue": {
        "name": "Predictable Revenue",
        "domain": "predictablerevenue.com",
        "rss_url": "https://predictablerevenue.com/blog/feed/",
        "category": "sales_development",
        "priority": "medium",
        "base_weight": 0.5,
        "rate_limit_per_day": 10,
        "min_word_count": 40
    },
}

# All sources combined
ALL_SOURCES = {**TIER1_SOURCES, **TIER2_SOURCES}

def main():
    parser = argparse.ArgumentParser(description='Expanded RSS News Collector')
    parser.add_argument('--tier',
                        choices=['1', '2', 'all'],
                        default='all',
                        help='Which tier to collect from')
    parser.add_argument('--limit', type=int,
                        help='Max articles per source')
    parser.add_argument('--historical', action='store_true',
                        help='Historical mode (6 months)')
    parser.add_argument('--test', action='store_true',
                        help='Test mode (3 articles each)')
    parser.add_argument('--quiet', action='store_true',
                        help='Quiet mode')

    args = parser.parse_args()

    # Select sources
    if args.tier == '1':
        sources = TIER1_SOURCES
        print(f"\n📰 Tier 1: {len(sources)} sources")
    elif args.tier == '2':
        sources = TIER2_SOURCES
        print(f"\n📰 Tier 2: {len(sources)} sources")
    else:
        sources = ALL_SOURCES
        print(f"\n📰 All Tiers: {len(sources)} sources (Tier 1: {len(TIER1_SOURCES)}, Tier 2: {len(TIER2_SOURCES)})")

    max_age = 180 if args.historical else 30
    verbose = not args.quiet
    limit = args.limit

    if args.test:
        limit = 3

    # Create custom collector with selected sources
    collector = ExpandedRSSCollector(sources, store_db=True)

    print(f"Max age: {max_age} days")
    print(f"Limit: {limit or 'default'} articles/source")
    print()

    # Collect
    collector.collect_all_sources(limit_per_source=limit, max_age_days=max_age, verbose=verbose)

class ExpandedRSSCollector(RSSNewsCollector):
    """Extended collector with configurable sources"""

    def __init__(self, sources_config, output_dir="/Users/yourox/AI-Workspace/data/rss_news", store_db=True):
        self.sources_config = sources_config

        # Initialize parent WITHOUT overriding
        from pathlib import Path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.store_db = store_db

        if self.store_db:
            import os
            self.conn_string = os.getenv('RAILWAY_DATABASE_URL')

        # Create subdirectories for ALL sources
        for source_id in sources_config.keys():
            (self.output_dir / source_id).mkdir(exist_ok=True)

    def collect_all_sources(self, limit_per_source=None, max_age_days=30, verbose=True):
        """Collect from ALL configured sources"""
        if verbose:
            print(f"\n{'='*70}")
            print(f"🚀 COLLECTING FROM ALL SOURCES")
            print(f"{'='*70}\n")

        results = {}
        total_articles = 0

        # Iterate through OUR sources, not TIER1_SOURCES
        for source_id in self.sources_config.keys():
            articles = self.fetch_rss_feed_custom(source_id, limit=limit_per_source,
                                                  max_age_days=max_age_days, verbose=verbose)

            if articles:
                output_file = self.save_articles(source_id, articles)
                results[source_id] = {
                    "article_count": len(articles),
                    "output_file": output_file
                }
                total_articles += len(articles)
            else:
                results[source_id] = {
                    "article_count": 0,
                    "output_file": None
                }

        if verbose:
            print(f"\n{'='*70}")
            print(f"📊 COLLECTION SUMMARY")
            print(f"{'='*70}\n")

            for source_id, result in results.items():
                source_name = self.sources_config[source_id]['name']
                count = result['article_count']
                print(f"   {source_name}: {count} articles")

            print(f"\n   TOTAL: {total_articles} articles collected")

        return results

    def save_articles(self, source_id, articles):
        """Override to use custom source config"""
        if not articles:
            print("⚠️  No articles to save")
            return None

        from datetime import datetime
        import json

        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / source_id / f"{source_id}_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                "source_id": source_id,
                "source_name": self.sources_config[source_id]['name'],
                "collected_at": datetime.now().isoformat(),
                "article_count": len(articles),
                "articles": articles
            }, f, indent=2)

        print(f"\n💾 Saved {len(articles)} articles to: {output_file}")

        # Save to database
        if self.store_db:
            db_saved = self.save_to_database(source_id, articles)
            if db_saved:
                print(f"✅ Stored {db_saved} articles in database")

        return str(output_file)

    def fetch_rss_feed_custom(self, source_id, limit=None, max_age_days=30, verbose=True):
        """Fetch RSS using custom source config"""
        if source_id not in self.sources_config:
            print(f"❌ Unknown source: {source_id}")
            return []

        source = self.sources_config[source_id]
        limit = limit or source['rate_limit_per_day']

        if verbose:
            print(f"\n{'='*70}")
            print(f"📰 Fetching: {source['name']}")
            print(f"{'='*70}")
            print(f"URL: {source['rss_url']}")
            print(f"Limit: {limit} articles | Max age: {max_age_days} days")

        try:
            import requests
            import feedparser
            from datetime import datetime

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(source['rss_url'], headers=headers, timeout=30)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if feed.bozo and verbose:
                print(f"⚠️  Feed parsing warning: {feed.get('bozo_exception', 'Unknown')}")

            if verbose:
                print(f"✅ Found {len(feed.entries)} entries in feed")

            articles = []
            for entry in feed.entries[:limit]:
                article = self.process_entry(entry, source_id, source)

                if article and self.passes_quality_filter(article, source, max_age_days=max_age_days):
                    articles.append(article)
                    if verbose:
                        print(f"   ✓ {article['title'][:60]}...")
                else:
                    if verbose:
                        print(f"   ✗ Filtered: {entry.get('title', 'No title')[:60]}...")

            if verbose:
                print(f"\n✅ Collected {len(articles)}/{len(feed.entries[:limit])} articles (after filtering)")
            return articles

        except Exception as e:
            print(f"❌ Error fetching {source_id}: {e}")
            return []

if __name__ == "__main__":
    main()
