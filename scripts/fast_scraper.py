#!/usr/bin/env python3
"""
Fast Content Scraper - requests + BeautifulSoup

Scrapes historical articles from top 10 priority sources.
10-50x faster than browser-based scraping.

Usage:
    python3 fast_scraper.py --test              # Test with 1 source
    python3 fast_scraper.py --source inc        # Scrape specific source
    python3 fast_scraper.py --scrape            # Scrape all top 10
    python3 fast_scraper.py --scrape --parallel # Parallel (10 workers)
"""

import os
import sys
import json
import time
import hashlib
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
load_dotenv('/Users/yourox/AI-Workspace/.env')

from scripts.rss_expanded_collector import ALL_SOURCES

# Top 10 priority sources
TOP_10_SOURCES = [
    'wharton', 'huggingface', 'entrepreneur', 'inc',
    'copyblogger', 'buffer', 'marketingprofs', 'cmi', 'moz',
    'smallbiz'  # Added instead of reuters (403 errors)
]

# Archive/blog URLs
ARCHIVE_URLS = {
    'wharton': 'https://knowledge.wharton.upenn.edu/',
    'huggingface': 'https://huggingface.co/blog',
    'entrepreneur': 'https://www.entrepreneur.com/topic/business-news',
    'inc': 'https://www.inc.com/articles',
    'copyblogger': 'https://copyblogger.com/blog/',
    'buffer': 'https://buffer.com/resources/',
    'marketingprofs': 'https://www.marketingprofs.com/articles',
    'cmi': 'https://contentmarketinginstitute.com/articles/',
    'moz': 'https://moz.com/blog',
    'smallbiz': 'https://smallbiztrends.com/'
}

# Selectors for article links on archive pages
LINK_SELECTORS = {
    'wharton': {'selector': 'a[href*="/article/"]', 'attr': 'href'},
    'huggingface': {'selector': 'article a, h2 a', 'attr': 'href'},
    'entrepreneur': {'selector': 'h3 a, .headline a', 'attr': 'href'},
    'inc': {'selector': 'h2 a, .article-title a', 'attr': 'href'},
    'copyblogger': {'selector': 'h2 a, .entry-title a', 'attr': 'href'},
    'buffer': {'selector': 'h2 a, h3 a', 'attr': 'href'},
    'marketingprofs': {'selector': 'h2 a, h3 a', 'attr': 'href'},
    'cmi': {'selector': 'h2 a, .entry-title a', 'attr': 'href'},
    'moz': {'selector': 'h2 a, .blog-post-title a', 'attr': 'href'},
    'smallbiz': {'selector': 'h2 a, h3 a', 'attr': 'href'}
}

# Content selectors for full article extraction
CONTENT_SELECTORS = {
    'wharton': ['article', '.article-content', 'main'],
    'huggingface': ['article', '.prose', 'main'],
    'entrepreneur': ['article', '.article-content', '.content'],
    'inc': ['article', '.article-body', '.post-content'],
    'copyblogger': ['article', '.entry-content', '.post-content'],
    'buffer': ['article', '.post-content', 'main'],
    'marketingprofs': ['article', '.article-content', 'main'],
    'cmi': ['article', '.entry-content', 'main'],
    'moz': ['article', '.post-content', 'main'],
    'smallbiz': ['article', '.entry-content', 'main']
}

class FastScraper:
    """Fast HTML scraper using requests + BeautifulSoup"""

    def __init__(self):
        self.output_dir = Path('/Users/yourox/AI-Workspace/data/scraped_articles')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        self.stats = {
            'total_articles': 0,
            'total_time': 0,
            'sources': {}
        }

    def scrape_source(self, source_id, max_articles=100, verbose=True):
        """Scrape articles from a single source"""

        if source_id not in ALL_SOURCES:
            print(f"❌ Unknown source: {source_id}")
            return []

        config = ALL_SOURCES[source_id]
        start_time = time.time()

        if verbose:
            print(f"\n{'='*70}")
            print(f"📰 Scraping: {config['name']}")
            print(f"{'='*70}")

        # Get archive page
        archive_url = ARCHIVE_URLS.get(source_id, f"https://{config['domain']}")

        try:
            if verbose:
                print(f"📄 Loading: {archive_url}")

            response = self.session.get(archive_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Extract article links
            link_config = LINK_SELECTORS.get(source_id, {'selector': 'article a', 'attr': 'href'})
            links = soup.select(link_config['selector'])

            if verbose:
                print(f"📋 Found {len(links)} potential articles")

            # Collect unique article URLs
            article_urls = set()
            for link in links:
                href = link.get(link_config['attr'])
                if not href:
                    continue

                # Make absolute URL
                if href.startswith('/'):
                    href = f"https://{config['domain']}{href}"
                elif not href.startswith('http'):
                    continue

                # Skip non-article URLs
                if any(skip in href for skip in ['#', 'tag/', 'category/', 'author/', 'page/']):
                    continue

                article_urls.add(href)

                if len(article_urls) >= max_articles:
                    break

            if verbose:
                print(f"🎯 Extracted {len(article_urls)} unique article URLs")

            # Scrape full articles
            articles = []
            for i, url in enumerate(list(article_urls)[:max_articles], 1):
                article = self.scrape_article(url, source_id, config)
                if article:
                    articles.append(article)
                    if verbose:
                        print(f"   ✓ [{i}/{len(article_urls)}] {article['title'][:60]}...")
                else:
                    if verbose:
                        print(f"   ✗ [{i}/{len(article_urls)}] Failed: {url[:60]}...")

                # Rate limiting
                time.sleep(0.5)

            elapsed = time.time() - start_time
            self.stats['sources'][source_id] = {
                'articles': len(articles),
                'time': elapsed
            }
            self.stats['total_articles'] += len(articles)
            self.stats['total_time'] += elapsed

            if verbose:
                print(f"\n✅ Scraped {len(articles)} articles in {elapsed:.1f}s")
                print(f"⏱️  Average: {elapsed/len(articles):.1f}s per article" if articles else "")

            return articles

        except Exception as e:
            print(f"❌ Error scraping {source_id}: {e}")
            return []

    def scrape_article(self, url, source_id, config):
        """Scrape full article content"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Extract title
            title = None
            for selector in ['h1', 'title', '.article-title', '.entry-title']:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text().strip()
                    break

            if not title:
                return None

            # Extract content
            content = ""
            content_selectors = CONTENT_SELECTORS.get(source_id, ['article', 'main'])

            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    # Remove script and style tags
                    for tag in elem.find_all(['script', 'style', 'nav', 'aside']):
                        tag.decompose()

                    content = elem.get_text(separator=' ', strip=True)
                    if len(content) > 200:
                        break

            if not content or len(content) < 100:
                return None

            # Extract author
            author = "Unknown"
            for selector in ['.author', '[rel="author"]', '.byline', '[itemprop="author"]']:
                elem = soup.select_one(selector)
                if elem:
                    author = elem.get_text().strip()
                    break

            # Extract date
            published_at = None
            for selector in ['time', '[datetime]', '.date', '.published']:
                elem = soup.select_one(selector)
                if elem:
                    date_str = elem.get('datetime') or elem.get_text()
                    try:
                        # Try various date formats
                        for fmt in ['%Y-%m-%d', '%B %d, %Y', '%b %d, %Y']:
                            try:
                                published_at = datetime.strptime(date_str[:10], fmt)
                                break
                            except:
                                continue
                        if not published_at:
                            # Try ISO format
                            published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        break
                    except:
                        continue

            if not published_at:
                published_at = datetime.now()

            # Build article object
            word_count = len(content.split())
            content_id = hashlib.md5(url.encode()).hexdigest()

            return {
                "content_id": content_id,
                "source_id": source_id,
                "source_name": config['name'],
                "title": title[:200],
                "url": url,
                "author": author[:100],
                "published_at": published_at.isoformat(),
                "fetched_at": datetime.now().isoformat(),
                "content_type": "article",
                "content_text": content[:10000],  # Limit to 10k chars
                "content_length": word_count,
                "category": config['category'],
                "priority": config['priority'],
                "base_weight": config['base_weight'],
                "raw_score": self.calculate_score(word_count, published_at, config),
                "scrape_method": "requests"
            }

        except Exception as e:
            return None

    def calculate_score(self, word_count, published_at, config):
        """Calculate quality score"""
        score = 0.5

        if word_count > 1000:
            score += 0.2
        elif word_count > 500:
            score += 0.15
        elif word_count > 200:
            score += 0.1
        elif word_count < 50:
            score -= 0.2

        days_old = (datetime.now() - published_at).days
        if days_old <= 7:
            freshness = 0.9
        elif days_old <= 30:
            freshness = 0.7
        elif days_old <= 90:
            freshness = 0.5
        else:
            freshness = 0.3

        final_score = (
            config['base_weight'] * 0.5 +
            score * 0.3 +
            freshness * 0.2
        )

        return min(max(final_score, 0.0), 1.0)

    def save_articles(self, source_id, articles):
        """Save articles to JSON and database"""
        if not articles:
            return

        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_dir = self.output_dir / source_id
        source_dir.mkdir(exist_ok=True)

        output_file = source_dir / f"{source_id}_scraped_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                "source_id": source_id,
                "source_name": articles[0]['source_name'],
                "scrape_method": "requests",
                "collected_at": datetime.now().isoformat(),
                "article_count": len(articles),
                "articles": articles
            }, f, indent=2)

        print(f"💾 Saved {len(articles)} articles to: {output_file}")

        # Save to database
        try:
            self.save_to_database(source_id, articles)
        except Exception as e:
            print(f"   ⚠️  Database save failed: {e}")

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

    def scrape_all_parallel(self, sources, max_workers=10):
        """Scrape multiple sources in parallel"""
        print(f"\n{'='*70}")
        print(f"🚀 PARALLEL SCRAPING")
        print(f"{'='*70}")
        print(f"Sources: {len(sources)}")
        print(f"Max workers: {max_workers}")
        print(f"{'='*70}\n")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.scrape_source, source_id, 100, True): source_id
                for source_id in sources
            }

            for future in as_completed(futures):
                source_id = futures[future]
                try:
                    articles = future.result()
                    if articles:
                        self.save_articles(source_id, articles)
                except Exception as e:
                    print(f"❌ Error with {source_id}: {e}")

        # Print final stats
        print(f"\n{'='*70}")
        print(f"📊 SCRAPING SUMMARY")
        print(f"{'='*70}\n")

        for source_id, stats in sorted(self.stats['sources'].items(), key=lambda x: x[1]['articles'], reverse=True):
            source_name = ALL_SOURCES[source_id]['name']
            print(f"   {source_name}:")
            print(f"      Articles: {stats['articles']}")
            print(f"      Time: {stats['time']:.1f}s ({stats['time']/stats['articles']:.2f}s/article)" if stats['articles'] > 0 else f"      Time: {stats['time']:.1f}s")
            print()

        print(f"   TOTAL: {self.stats['total_articles']} articles in {self.stats['total_time']:.1f}s")
        avg_time = self.stats['total_time'] / self.stats['total_articles'] if self.stats['total_articles'] > 0 else 0
        print(f"   AVERAGE: {avg_time:.2f}s per article")
        print(f"{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(description='Fast Content Scraper')
    parser.add_argument('--test', action='store_true',
                        help='Test with single source (Inc.com)')
    parser.add_argument('--source', type=str,
                        help='Scrape specific source')
    parser.add_argument('--scrape', action='store_true',
                        help='Scrape all top 10 sources')
    parser.add_argument('--parallel', action='store_true',
                        help='Use parallel scraping (10 workers)')

    args = parser.parse_args()

    scraper = FastScraper()

    if args.test:
        print("🧪 TEST MODE: Scraping Inc.com only\n")
        articles = scraper.scrape_source('inc', max_articles=10)
        if articles:
            scraper.save_articles('inc', articles)

    elif args.source:
        if args.source not in TOP_10_SOURCES:
            print(f"❌ Unknown source: {args.source}")
            print(f"Available: {', '.join(TOP_10_SOURCES)}")
            return

        articles = scraper.scrape_source(args.source, max_articles=100)
        if articles:
            scraper.save_articles(args.source, articles)

    elif args.scrape:
        if args.parallel:
            scraper.scrape_all_parallel(TOP_10_SOURCES, max_workers=10)
        else:
            # Sequential
            for source_id in TOP_10_SOURCES:
                articles = scraper.scrape_source(source_id, max_articles=100)
                if articles:
                    scraper.save_articles(source_id, articles)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
