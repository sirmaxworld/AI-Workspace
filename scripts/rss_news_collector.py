#!/usr/bin/env python3
"""
RSS News Collector - Tier 1 Sources

Fetches news from RSS feeds with quality filtering and scoring.
Based on CONTENT_SOURCES_ARCHITECTURE.md design.

Tier 1 Sources (8 RSS feeds):
- TechCrunch AI
- HubSpot Blog
- Small Business Trends
- Social Media Examiner
- Neil Patel Blog
- Seth Godin's Blog
- Moz Blog
- Hacker News (via API, not RSS)

Usage:
    python3 rss_news_collector.py --source techcrunch
    python3 rss_news_collector.py --source all --limit 10
    python3 rss_news_collector.py --test
"""

import os
import sys
import json
import hashlib
import argparse
import requests
import feedparser
import psycopg2
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
load_dotenv('/Users/yourox/AI-Workspace/.env')

# Tier 1 RSS Sources Configuration
TIER1_SOURCES = {
    "techcrunch": {
        "name": "TechCrunch AI",
        "domain": "techcrunch.com",
        "rss_url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "ai_news",
        "priority": "high",
        "base_weight": 0.6,
        "rate_limit_per_day": 20,
        "min_word_count": 30  # RSS only has summaries
    },
    "hubspot": {
        "name": "HubSpot Blog",
        "domain": "blog.hubspot.com",
        "rss_url": "https://blog.hubspot.com/marketing/rss.xml",
        "category": "marketing",
        "priority": "high",
        "base_weight": 0.7,
        "rate_limit_per_day": 15,
        "min_word_count": 30
    },
    "smallbiz": {
        "name": "Small Business Trends",
        "domain": "smallbiztrends.com",
        "rss_url": "https://smallbiztrends.com/feed",
        "category": "sme_news",
        "priority": "medium",
        "base_weight": 0.5,
        "rate_limit_per_day": 10,
        "min_word_count": 30
    },
    "socialmedia": {
        "name": "Social Media Examiner",
        "domain": "socialmediaexaminer.com",
        "rss_url": "https://www.socialmediaexaminer.com/feed/",
        "category": "social_media",
        "priority": "medium",
        "base_weight": 0.5,
        "rate_limit_per_day": 10,
        "min_word_count": 30
    },
    "neilpatel": {
        "name": "Neil Patel Blog",
        "domain": "neilpatel.com",
        "rss_url": "https://neilpatel.com/feed/",
        "category": "digital_marketing",
        "priority": "medium",
        "base_weight": 0.6,
        "rate_limit_per_day": 10,
        "min_word_count": 30
    },
    "sethgodin": {
        "name": "Seth Godin's Blog",
        "domain": "seths.blog",
        "rss_url": "https://seths.blog/feed/",
        "category": "marketing_philosophy",
        "priority": "high",
        "base_weight": 0.7,
        "rate_limit_per_day": 5,
        "min_word_count": 20  # Seth's posts are often short but valuable
    },
    "moz": {
        "name": "Moz Blog",
        "domain": "moz.com",
        "rss_url": "https://moz.com/blog/feed",
        "category": "seo",
        "priority": "medium",
        "base_weight": 0.6,
        "rate_limit_per_day": 10,
        "min_word_count": 30
    }
}

class RSSNewsCollector:
    def __init__(self, output_dir="/Users/yourox/AI-Workspace/data/rss_news", store_db=True):
        """Initialize RSS collector"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.store_db = store_db

        # Database connection
        if self.store_db:
            self.conn_string = os.getenv('RAILWAY_DATABASE_URL')

        # Create subdirectories for each source
        for source_id in TIER1_SOURCES.keys():
            (self.output_dir / source_id).mkdir(exist_ok=True)

    def fetch_rss_feed(self, source_id, limit=None, max_age_days=30, verbose=True):
        """
        Fetch RSS feed for a source

        Args:
            source_id: Source identifier (e.g., 'techcrunch')
            limit: Max articles to fetch (None = use rate_limit_per_day)
            max_age_days: Maximum age of articles in days (default 30)
            verbose: Print detailed progress (default True)

        Returns:
            list: Parsed articles
        """
        if source_id not in TIER1_SOURCES:
            print(f"❌ Unknown source: {source_id}")
            return []

        source = TIER1_SOURCES[source_id]
        limit = limit or source['rate_limit_per_day']

        if verbose:
            print(f"\n{'='*70}")
            print(f"📰 Fetching: {source['name']}")
            print(f"{'='*70}")
            print(f"URL: {source['rss_url']}")
            print(f"Limit: {limit} articles | Max age: {max_age_days} days")

        try:
            # Fetch RSS feed with requests first (handles SSL better)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(source['rss_url'], headers=headers, timeout=30)
            response.raise_for_status()

            # Parse RSS feed
            feed = feedparser.parse(response.content)

            if feed.bozo and verbose:
                print(f"⚠️  Feed parsing warning: {feed.get('bozo_exception', 'Unknown')}")

            if verbose:
                print(f"✅ Found {len(feed.entries)} entries in feed")

            # Process entries
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

    def process_entry(self, entry, source_id, source):
        """
        Process a single RSS entry into structured article

        Args:
            entry: RSS entry from feedparser
            source_id: Source identifier
            source: Source config

        Returns:
            dict: Processed article or None if invalid
        """
        try:
            # Extract basic fields
            title = entry.get('title', '').strip()
            url = entry.get('link', '').strip()

            if not title or not url:
                return None

            # Generate unique content ID
            content_id = hashlib.md5(url.encode()).hexdigest()

            # Parse published date
            published_at = None
            if 'published_parsed' in entry and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            elif 'updated_parsed' in entry and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6])
            else:
                published_at = datetime.now()

            # Extract content
            content_text = ""
            if 'summary' in entry:
                content_text = entry.summary
            elif 'content' in entry:
                content_text = entry.content[0].value if entry.content else ""
            elif 'description' in entry:
                content_text = entry.description

            # Strip HTML tags (basic)
            import re
            content_text = re.sub(r'<[^>]+>', '', content_text)
            content_text = content_text.strip()

            # Extract author
            author = entry.get('author', 'Unknown')

            # Calculate word count
            word_count = len(content_text.split())

            # Build article object
            article = {
                "content_id": content_id,
                "source_id": source_id,
                "source_name": source['name'],
                "title": title,
                "url": url,
                "author": author,
                "published_at": published_at.isoformat(),
                "fetched_at": datetime.now().isoformat(),
                "content_type": "article",
                "content_text": content_text,
                "content_length": word_count,
                "category": source['category'],
                "priority": source['priority'],
                "base_weight": source['base_weight'],
                "tags": entry.get('tags', []),
                "raw_entry": {
                    "id": entry.get('id', ''),
                    "guid": entry.get('guid', '')
                }
            }

            # Calculate initial score
            article['raw_score'] = self.calculate_raw_score(article, source)

            return article

        except Exception as e:
            print(f"   ⚠️  Error processing entry: {e}")
            return None

    def calculate_raw_score(self, article, source):
        """
        Calculate initial quality score for article

        Based on CONTENT_SOURCES_ARCHITECTURE.md scoring formula
        """
        score = 0.5  # Start neutral

        # Content length signals (adjusted for RSS summaries)
        if article['content_length'] > 200:
            score += 0.15  # Good summary
        elif article['content_length'] < 20:
            score -= 0.15  # Too short

        # Freshness (decays over time)
        published_at = datetime.fromisoformat(article['published_at'])
        days_old = (datetime.now() - published_at).days

        if days_old <= 1:
            freshness = 1.0
        elif days_old <= 7:
            freshness = 0.9
        elif days_old <= 30:
            freshness = 0.7
        else:
            freshness = 0.5

        # Combine
        final_score = (
            source['base_weight'] * 0.5 +
            score * 0.3 +
            freshness * 0.2
        )

        return min(max(final_score, 0.0), 1.0)

    def passes_quality_filter(self, article, source, max_age_days=30):
        """
        Check if article passes minimum quality thresholds

        Args:
            article: Article dict
            source: Source config
            max_age_days: Maximum age in days (default 30)

        Returns:
            bool: True if passes filters
        """
        # Check minimum word count
        min_words = source.get('min_word_count', 300)
        if article['content_length'] < min_words:
            return False

        # Check if too old
        published_at = datetime.fromisoformat(article['published_at'])
        days_old = (datetime.now() - published_at).days
        if days_old > max_age_days:
            return False

        # Check minimum score
        if article['raw_score'] < 0.3:
            return False

        return True

    def save_articles(self, source_id, articles):
        """
        Save articles to JSON files and database

        Args:
            source_id: Source identifier
            articles: List of articles

        Returns:
            str: Output file path
        """
        if not articles:
            print("⚠️  No articles to save")
            return None

        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / source_id / f"{source_id}_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                "source_id": source_id,
                "source_name": TIER1_SOURCES[source_id]['name'],
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

    def save_to_database(self, source_id, articles):
        """
        Store articles in Railway PostgreSQL

        Args:
            source_id: Source identifier
            articles: List of articles

        Returns:
            int: Number of articles saved
        """
        if not articles:
            return 0

        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()

            saved_count = 0

            for article in articles:
                try:
                    # Insert article
                    cursor.execute("""
                        INSERT INTO external_content (
                            content_id, source_id, title, url, author,
                            published_at, fetched_at, content_type,
                            content_text, content_length, tags, categories,
                            raw_score, final_score
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s
                        )
                        ON CONFLICT (url) DO UPDATE SET
                            fetched_at = EXCLUDED.fetched_at,
                            raw_score = EXCLUDED.raw_score,
                            final_score = EXCLUDED.final_score
                    """, (
                        article['content_id'],
                        article['source_id'],
                        article['title'],
                        article['url'],
                        article.get('author'),
                        article['published_at'],
                        article['fetched_at'],
                        article['content_type'],
                        article['content_text'],
                        article['content_length'],
                        json.dumps(article.get('tags', [])),
                        json.dumps([article['category']]),
                        article['raw_score'],
                        article['raw_score']  # Use raw_score as final_score for now
                    ))

                    saved_count += 1

                except psycopg2.errors.UniqueViolation:
                    # Article already exists
                    conn.rollback()
                    continue

            # Update source last_fetched_at
            cursor.execute("""
                UPDATE external_sources
                SET last_fetched_at = %s,
                    total_articles_fetched = total_articles_fetched + %s
                WHERE source_id = %s
            """, (datetime.now(), saved_count, source_id))

            conn.commit()
            cursor.close()
            conn.close()

            return saved_count

        except Exception as e:
            print(f"❌ Database error: {e}")
            return 0

    def collect_all_sources(self, limit_per_source=None, max_age_days=30, verbose=True):
        """
        Collect from all Tier 1 sources

        Args:
            limit_per_source: Max articles per source
            max_age_days: Maximum age of articles in days
            verbose: Print detailed progress

        Returns:
            dict: Results by source
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"🚀 COLLECTING FROM ALL TIER 1 SOURCES")
            print(f"{'='*70}\n")

        results = {}
        total_articles = 0

        for source_id in TIER1_SOURCES.keys():
            articles = self.fetch_rss_feed(source_id, limit=limit_per_source,
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

        # Summary
        if verbose:
            print(f"\n{'='*70}")
            print(f"📊 COLLECTION SUMMARY")
            print(f"{'='*70}\n")

            for source_id, result in results.items():
                source_name = TIER1_SOURCES[source_id]['name']
                count = result['article_count']
                print(f"   {source_name}: {count} articles")

            print(f"\n   TOTAL: {total_articles} articles collected")

        return results

def main():
    parser = argparse.ArgumentParser(description='RSS News Collector - Tier 1 Sources')
    parser.add_argument('--source',
                        choices=list(TIER1_SOURCES.keys()) + ['all'],
                        help='Source to collect from')
    parser.add_argument('--limit', type=int,
                        help='Max articles per source')
    parser.add_argument('--max-age-days', type=int, default=30,
                        help='Maximum age of articles in days (default: 30, use 180 for 6 months)')
    parser.add_argument('--historical', action='store_true',
                        help='Historical mode: collect 6 months of data (180 days)')
    parser.add_argument('--test', action='store_true',
                        help='Test collection (fetch 3 articles from each)')
    parser.add_argument('--quiet', action='store_true',
                        help='Quiet mode: minimal output')

    args = parser.parse_args()

    collector = RSSNewsCollector()

    # Set max age
    max_age = 180 if args.historical else args.max_age_days
    verbose = not args.quiet

    if args.historical:
        print(f"\n{'='*70}")
        print(f"📚 HISTORICAL COLLECTION MODE (6 months)")
        print(f"{'='*70}")
        print(f"Max age: {max_age} days")
        print(f"Note: RSS feeds typically only provide last 10-50 items")
        print(f"      For full historical data, consider web scraping\n")

    if args.test:
        print("🧪 TEST MODE: Fetching 3 articles from each source\n")
        collector.collect_all_sources(limit_per_source=3, max_age_days=max_age, verbose=verbose)

    elif args.source == 'all':
        collector.collect_all_sources(limit_per_source=args.limit, max_age_days=max_age, verbose=verbose)

    elif args.source:
        articles = collector.fetch_rss_feed(args.source, limit=args.limit,
                                           max_age_days=max_age, verbose=verbose)
        if articles:
            collector.save_articles(args.source, articles)

    else:
        print("❌ Please specify --source, --test, or --historical")
        parser.print_help()

if __name__ == "__main__":
    main()
