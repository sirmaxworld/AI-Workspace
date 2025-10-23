#!/usr/bin/env python3
"""
NewsAPI.ai Historical Content Collector

Collects 6 months of historical articles from 26 sources using NewsAPI.ai (Event Registry).
Uses free tier (2,000 tokens) - should be sufficient for our needs.

Usage:
    python3 newsapi_collector.py --setup        # First time: set API key
    python3 newsapi_collector.py --test         # Test with 1 source
    python3 newsapi_collector.py --collect      # Collect from all sources
    python3 newsapi_collector.py --stats        # Show token usage stats
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
load_dotenv('/Users/yourox/AI-Workspace/.env')

# Import RSS sources for domain list
from scripts.rss_expanded_collector import ALL_SOURCES

try:
    from eventregistry import EventRegistry, QueryArticlesIter
except ImportError:
    print("❌ eventregistry not installed. Run: pip3 install eventregistry")
    sys.exit(1)

class NewsAPICollector:
    """Collect historical articles using NewsAPI.ai"""

    def __init__(self, api_key=None, output_dir="/Users/yourox/AI-Workspace/data/newsapi"):
        self.api_key = api_key or os.getenv('NEWSAPI_AI_KEY')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.api_key:
            print("❌ No API key found!")
            print("   1. Sign up at https://newsapi.ai/")
            print("   2. Get your API key from dashboard")
            print("   3. Run: python3 newsapi_collector.py --setup")
            sys.exit(1)

        # Initialize Event Registry
        self.er = EventRegistry(apiKey=self.api_key, allowUseOfArchive=True)

        # Token tracking
        self.tokens_used = 0
        self.tokens_limit = 2000  # Free tier

    def get_source_uri(self, domain):
        """Get NewsAPI source URI from domain"""
        try:
            # Try exact domain match
            uri = self.er.getSourceUri(domain)
            if uri:
                return uri

            # Try without TLD
            base = domain.split('.')[0]
            uri = self.er.getSourceUri(base)
            return uri
        except Exception as e:
            print(f"   ⚠️  Could not find source URI for {domain}: {e}")
            return None

    def calculate_token_cost(self, date_start, date_end):
        """Calculate token cost for date range"""
        # Recent (30 days): 1 token
        # Historical: 5 tokens per year

        days_ago = (datetime.now() - datetime.strptime(date_start, "%Y-%m-%d")).days

        if days_ago <= 30:
            return 1
        else:
            years = days_ago / 365.0
            return int(years * 5) + 1  # 5 tokens per year + 1 base

    def collect_source(self, source_id, source_config, date_start, date_end, max_items=100, verbose=True):
        """Collect articles from a single source"""

        domain = source_config['domain']
        source_name = source_config['name']

        if verbose:
            print(f"\n{'='*70}")
            print(f"📰 Fetching: {source_name}")
            print(f"{'='*70}")
            print(f"Domain: {domain}")
            print(f"Date Range: {date_start} to {date_end}")

        # Get source URI
        source_uri = self.get_source_uri(domain)
        if not source_uri:
            print(f"   ❌ Could not resolve source URI for {domain}")
            return []

        if verbose:
            print(f"Source URI: {source_uri}")

        # Calculate token cost
        token_cost = self.calculate_token_cost(date_start, date_end)
        if verbose:
            print(f"Estimated tokens: {token_cost}")

        # Check token limit
        if self.tokens_used + token_cost > self.tokens_limit:
            print(f"   ⚠️  Token limit reached ({self.tokens_used}/{self.tokens_limit})")
            return []

        try:
            # Build query
            q = QueryArticlesIter(
                sourceUri=source_uri,
                dateStart=date_start,
                dateEnd=date_end,
                lang="eng"  # English only
            )

            # Execute query
            articles = []
            for article in q.execQuery(self.er, sortBy="date", maxItems=max_items):
                # Process article
                processed = self.process_article(article, source_id, source_config)
                if processed:
                    articles.append(processed)
                    if verbose:
                        print(f"   ✓ {processed['title'][:60]}...")

            # Update token usage
            self.tokens_used += token_cost

            if verbose:
                print(f"\n✅ Collected {len(articles)} articles")
                print(f"📊 Tokens used: {self.tokens_used}/{self.tokens_limit}")

            return articles

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []

    def process_article(self, article, source_id, source_config):
        """Process raw article from API into our format"""
        try:
            # Extract fields
            url = article.get('url', '')
            title = article.get('title', '')

            if not url or not title:
                return None

            # Generate content ID
            content_id = hashlib.md5(url.encode()).hexdigest()

            # Parse date
            date_str = article.get('dateTime', article.get('date', ''))
            published_at = None
            if date_str:
                try:
                    published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    published_at = datetime.now()
            else:
                published_at = datetime.now()

            # Extract content
            body = article.get('body', article.get('description', ''))
            word_count = len(body.split()) if body else 0

            # Build article object
            return {
                "content_id": content_id,
                "source_id": source_id,
                "source_name": source_config['name'],
                "title": title,
                "url": url,
                "author": article.get('authors', [{}])[0].get('name', 'Unknown') if article.get('authors') else 'Unknown',
                "published_at": published_at.isoformat(),
                "fetched_at": datetime.now().isoformat(),
                "content_type": "article",
                "content_text": body,
                "content_length": word_count,
                "category": source_config['category'],
                "priority": source_config['priority'],
                "base_weight": source_config['base_weight'],
                "raw_score": self.calculate_score(word_count, published_at, source_config),
                "api_source": "newsapi.ai"
            }
        except Exception as e:
            print(f"   ⚠️  Error processing article: {e}")
            return None

    def calculate_score(self, word_count, published_at, source_config):
        """Calculate quality score"""
        score = 0.5

        # Content length
        if word_count > 500:
            score += 0.2
        elif word_count > 200:
            score += 0.1
        elif word_count < 50:
            score -= 0.1

        # Freshness
        days_old = (datetime.now() - published_at).days
        if days_old <= 7:
            freshness = 0.9
        elif days_old <= 30:
            freshness = 0.7
        elif days_old <= 90:
            freshness = 0.5
        else:
            freshness = 0.3

        # Combine
        final_score = (
            source_config['base_weight'] * 0.5 +
            score * 0.3 +
            freshness * 0.2
        )

        return min(max(final_score, 0.0), 1.0)

    def save_articles(self, source_id, articles):
        """Save articles to JSON and database"""
        if not articles:
            return None

        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_dir = self.output_dir / source_id
        source_dir.mkdir(exist_ok=True)

        output_file = source_dir / f"{source_id}_newsapi_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                "source_id": source_id,
                "source_name": articles[0]['source_name'],
                "api": "newsapi.ai",
                "collected_at": datetime.now().isoformat(),
                "article_count": len(articles),
                "articles": articles
            }, f, indent=2)

        print(f"\n💾 Saved {len(articles)} articles to: {output_file}")

        # Save to database
        try:
            self.save_to_database(source_id, articles)
        except Exception as e:
            print(f"   ⚠️  Database save failed: {e}")

        return str(output_file)

    def save_to_database(self, source_id, articles):
        """Store articles in Railway PostgreSQL"""
        import psycopg2

        conn_string = os.getenv('RAILWAY_DATABASE_URL')
        if not conn_string:
            return

        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        saved_count = 0

        for article in articles:
            try:
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
                        content_text = EXCLUDED.content_text,
                        content_length = EXCLUDED.content_length,
                        raw_score = EXCLUDED.raw_score
                """, (
                    article['content_id'],
                    article['source_id'],
                    article['title'],
                    article['url'],
                    article['author'],
                    article['published_at'],
                    article['fetched_at'],
                    article['content_type'],
                    article['content_text'],
                    article['content_length'],
                    json.dumps([]),
                    json.dumps([article['category']]),
                    article['raw_score'],
                    article['raw_score']
                ))

                saved_count += 1

            except Exception as e:
                conn.rollback()
                continue

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Stored {saved_count} articles in database")

    def collect_all(self, date_start, date_end, max_per_source=100, verbose=True):
        """Collect from all 26 sources"""

        print(f"\n{'='*70}")
        print(f"🚀 NEWSAPI.AI HISTORICAL COLLECTION")
        print(f"{'='*70}")
        print(f"Sources: {len(ALL_SOURCES)}")
        print(f"Date Range: {date_start} to {date_end}")
        print(f"Max per source: {max_per_source}")
        print(f"Token Limit: {self.tokens_limit}")
        print(f"{'='*70}\n")

        results = {}
        total_articles = 0

        for source_id, config in ALL_SOURCES.items():
            articles = self.collect_source(
                source_id, config, date_start, date_end,
                max_items=max_per_source, verbose=verbose
            )

            if articles:
                self.save_articles(source_id, articles)
                results[source_id] = len(articles)
                total_articles += len(articles)
            else:
                results[source_id] = 0

            # Check token limit
            if self.tokens_used >= self.tokens_limit:
                print(f"\n⚠️  Token limit reached! Stopping collection.")
                break

        # Summary
        print(f"\n{'='*70}")
        print(f"📊 COLLECTION SUMMARY")
        print(f"{'='*70}\n")

        for source_id, count in results.items():
            source_name = ALL_SOURCES[source_id]['name']
            print(f"   {source_name}: {count} articles")

        print(f"\n   TOTAL: {total_articles} articles")
        print(f"   TOKENS USED: {self.tokens_used}/{self.tokens_limit}")
        print(f"{'='*70}\n")

        return results

def setup_api_key():
    """Interactive setup for API key"""
    print("\n🔑 NewsAPI.ai API Key Setup")
    print("="*70)
    print("\n1. Go to: https://newsapi.ai/")
    print("2. Sign up for a free account")
    print("3. Get your API key from the dashboard")
    print()

    api_key = input("Paste your API key here: ").strip()

    if not api_key:
        print("❌ No API key provided")
        return

    # Save to .env
    env_file = Path('/Users/yourox/AI-Workspace/.env')

    # Read existing .env
    env_lines = []
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_lines = f.readlines()

    # Update or add NEWSAPI_AI_KEY
    found = False
    for i, line in enumerate(env_lines):
        if line.startswith('NEWSAPI_AI_KEY='):
            env_lines[i] = f'NEWSAPI_AI_KEY={api_key}\n'
            found = True
            break

    if not found:
        env_lines.append(f'NEWSAPI_AI_KEY={api_key}\n')

    # Write back
    with open(env_file, 'w') as f:
        f.writelines(env_lines)

    print("\n✅ API key saved to .env file")
    print("   You can now run: python3 newsapi_collector.py --test")

def main():
    parser = argparse.ArgumentParser(description='NewsAPI.ai Historical Collector')
    parser.add_argument('--setup', action='store_true',
                        help='Setup API key')
    parser.add_argument('--test', action='store_true',
                        help='Test with 1 source')
    parser.add_argument('--collect', action='store_true',
                        help='Collect from all sources')
    parser.add_argument('--stats', action='store_true',
                        help='Show token usage stats')
    parser.add_argument('--source', type=str,
                        help='Collect from specific source')
    parser.add_argument('--months', type=int, default=6,
                        help='Months of history to collect (default: 6)')

    args = parser.parse_args()

    if args.setup:
        setup_api_key()
        return

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.months * 30)

    date_start = start_date.strftime("%Y-%m-%d")
    date_end = end_date.strftime("%Y-%m-%d")

    # Initialize collector
    collector = NewsAPICollector()

    if args.test:
        print("🧪 TEST MODE: Collecting from TechCrunch only\n")
        articles = collector.collect_source(
            'techcrunch',
            ALL_SOURCES['techcrunch'],
            date_start,
            date_end,
            max_items=10
        )
        if articles:
            collector.save_articles('techcrunch', articles)

    elif args.source:
        if args.source not in ALL_SOURCES:
            print(f"❌ Unknown source: {args.source}")
            print(f"Available: {', '.join(ALL_SOURCES.keys())}")
            return

        articles = collector.collect_source(
            args.source,
            ALL_SOURCES[args.source],
            date_start,
            date_end,
            max_items=100
        )
        if articles:
            collector.save_articles(args.source, articles)

    elif args.collect:
        collector.collect_all(date_start, date_end, max_per_source=100)

    elif args.stats:
        print(f"\n📊 Token Usage Statistics")
        print(f"="*70)
        print(f"Tokens Used: {collector.tokens_used}")
        print(f"Tokens Limit: {collector.tokens_limit}")
        print(f"Tokens Remaining: {collector.tokens_limit - collector.tokens_used}")
        print(f"="*70)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
