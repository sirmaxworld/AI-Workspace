#!/usr/bin/env python3
"""
Browserbase Content Scraper

Scrapes historical articles from top 10 priority sources using Browserbase.
Uses parallel sessions (max 10) for speed optimization.

Usage:
    python3 browserbase_scraper.py --test                    # Test single source
    python3 browserbase_scraper.py --scrape                  # Scrape all top 10
    python3 browserbase_scraper.py --source wharton          # Scrape specific source
    python3 browserbase_scraper.py --scrape --max-workers 5  # Limit parallelism
"""

import os
import sys
import json
import time
import hashlib
import argparse
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
load_dotenv('/Users/yourox/AI-Workspace/.env')

from scripts.rss_expanded_collector import ALL_SOURCES

try:
    from playwright.async_api import async_playwright
    from browserbase import Browserbase
except ImportError:
    print("❌ Required packages not installed")
    print("Run: pip3 install playwright browserbase")
    sys.exit(1)

# Top 10 priority sources
TOP_10_SOURCES = [
    'wharton', 'huggingface', 'reuters', 'entrepreneur', 'inc',
    'copyblogger', 'buffer', 'marketingprofs', 'cmi', 'moz'
]

# Archive URL patterns for each source
ARCHIVE_URLS = {
    'wharton': 'https://knowledge.wharton.upenn.edu/topics/',
    'huggingface': 'https://huggingface.co/blog',
    'reuters': 'https://www.reuters.com/business/',
    'entrepreneur': 'https://www.entrepreneur.com/latest',
    'inc': 'https://www.inc.com/latest',
    'copyblogger': 'https://copyblogger.com/blog/',
    'buffer': 'https://buffer.com/resources/',
    'marketingprofs': 'https://www.marketingprofs.com/articles',
    'cmi': 'https://contentmarketinginstitute.com/articles/',
    'moz': 'https://moz.com/blog'
}

# CSS selectors for each source (to extract article links)
ARTICLE_SELECTORS = {
    'wharton': 'article a[href*="/article/"], .post-title a',
    'huggingface': 'article a, .blog-post a',
    'reuters': 'article a[data-testid="Heading"]',
    'entrepreneur': 'article a, .headline a',
    'inc': 'article h2 a, .article-title a',
    'copyblogger': 'article a, .entry-title a',
    'buffer': 'article a, .post-title a',
    'marketingprofs': 'article a, .article-title a',
    'cmi': 'article a, .entry-title a',
    'moz': 'article a, .post-title a'
}

class BrowserbaseScraper:
    """Scrape articles using Browserbase for rendering"""

    def __init__(self, max_workers=10):
        self.api_key = os.getenv('BROWSERBASE_API_KEY')
        self.project_id = os.getenv('BROWSERBASE_PROJECT_ID')
        self.max_workers = max_workers
        self.output_dir = Path('/Users/yourox/AI-Workspace/data/scraped_articles')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.api_key or not self.project_id:
            print("❌ Browserbase credentials not found in .env")
            sys.exit(1)

        self.bb = Browserbase(api_key=self.api_key)
        self.stats = {
            'total_articles': 0,
            'total_time': 0,
            'sources': {}
        }

    async def scrape_source(self, source_id, max_articles=100, verbose=True):
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

        # Create Browserbase session
        try:
            session = self.bb.sessions.create(project_id=self.project_id)
            session_id = session.id

            if verbose:
                print(f"🌐 Browserbase session: {session_id}")

            # Connect with Playwright
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(
                    f"wss://connect.browserbase.com?apiKey={self.api_key}&sessionId={session_id}"
                )

                context = browser.contexts[0]
                page = context.pages[0]

                # Navigate to archive page
                archive_url = ARCHIVE_URLS.get(source_id, f"https://{config['domain']}")
                if verbose:
                    print(f"📄 Loading: {archive_url}")

                await page.goto(archive_url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(3000)  # Wait for JS to load

                # Extract article links
                selector = ARTICLE_SELECTORS.get(source_id, 'article a')
                articles = []

                try:
                    # Get all article links
                    links = await page.query_selector_all(selector)
                    if verbose:
                        print(f"📋 Found {len(links)} potential articles")

                    urls_collected = set()
                    for link in links[:max_articles * 2]:  # Get extra in case some fail
                        try:
                            href = await link.get_attribute('href')
                            if not href:
                                continue

                            # Make absolute URL
                            if href.startswith('/'):
                                href = f"https://{config['domain']}{href}"
                            elif not href.startswith('http'):
                                continue

                            # Skip duplicates and non-article URLs
                            if href in urls_collected:
                                continue
                            if any(skip in href for skip in ['#', 'tag/', 'category/', 'author/']):
                                continue

                            urls_collected.add(href)

                            # Try to extract title and date from listing
                            title_elem = link
                            title = await title_elem.inner_text()
                            title = title.strip()[:200]  # Limit title length

                            if title and len(title) > 10:
                                articles.append({
                                    'url': href,
                                    'title': title,
                                    'source_id': source_id,
                                    'discovered_at': datetime.now().isoformat()
                                })

                                if verbose:
                                    print(f"   ✓ {title[:60]}...")

                            if len(articles) >= max_articles:
                                break

                        except Exception as e:
                            continue

                except Exception as e:
                    print(f"   ⚠️  Error extracting articles: {e}")

                await browser.close()

            # Process articles (extract full content)
            processed = []
            if verbose:
                print(f"\n📖 Extracting full content from {len(articles)} articles...")

            for i, article in enumerate(articles[:max_articles], 1):
                full_article = await self.extract_full_article(article, config, session_id)
                if full_article:
                    processed.append(full_article)
                    if verbose and i % 10 == 0:
                        print(f"   Processed {i}/{len(articles)} articles...")

            elapsed = time.time() - start_time
            self.stats['sources'][source_id] = {
                'articles': len(processed),
                'time': elapsed
            }
            self.stats['total_articles'] += len(processed)
            self.stats['total_time'] += elapsed

            if verbose:
                print(f"\n✅ Scraped {len(processed)} articles in {elapsed:.1f}s")
                print(f"⏱️  Average: {elapsed/len(processed):.1f}s per article" if processed else "")

            return processed

        except Exception as e:
            print(f"❌ Error scraping {source_id}: {e}")
            return []

    async def extract_full_article(self, article_stub, config, session_id):
        """Extract full article content from URL"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(
                    f"wss://connect.browserbase.com?apiKey={self.api_key}&sessionId={session_id}"
                )

                context = browser.contexts[0]
                page = await context.new_page()

                await page.goto(article_stub['url'], wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(1000)

                # Extract content using common selectors
                content = ""
                for selector in ['article', '.article-content', '.post-content', '.entry-content', 'main']:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            content = await elem.inner_text()
                            if len(content) > 200:
                                break
                    except:
                        continue

                # Extract metadata
                author = "Unknown"
                try:
                    for selector in ['.author', '[rel="author"]', '.byline', '.author-name']:
                        elem = await page.query_selector(selector)
                        if elem:
                            author = await elem.inner_text()
                            author = author.strip()
                            break
                except:
                    pass

                # Extract date
                published_at = None
                try:
                    for selector in ['time', '.date', '.published', '[datetime]']:
                        elem = await page.query_selector(selector)
                        if elem:
                            date_str = await elem.get_attribute('datetime')
                            if not date_str:
                                date_str = await elem.inner_text()
                            if date_str:
                                # Try to parse
                                try:
                                    published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                except:
                                    pass
                            break
                except:
                    pass

                if not published_at:
                    published_at = datetime.now()

                await page.close()
                await browser.close()

                # Build article object
                word_count = len(content.split())
                content_id = hashlib.md5(article_stub['url'].encode()).hexdigest()

                return {
                    "content_id": content_id,
                    "source_id": article_stub['source_id'],
                    "source_name": config['name'],
                    "title": article_stub['title'],
                    "url": article_stub['url'],
                    "author": author,
                    "published_at": published_at.isoformat(),
                    "fetched_at": datetime.now().isoformat(),
                    "content_type": "article",
                    "content_text": content[:5000],  # Limit to 5k chars
                    "content_length": word_count,
                    "category": config['category'],
                    "priority": config['priority'],
                    "base_weight": config['base_weight'],
                    "raw_score": self.calculate_score(word_count, published_at, config),
                    "scrape_method": "browserbase"
                }

        except Exception as e:
            return None

    def calculate_score(self, word_count, published_at, config):
        """Calculate quality score"""
        score = 0.5

        if word_count > 500:
            score += 0.2
        elif word_count > 200:
            score += 0.1
        elif word_count < 50:
            score -= 0.1

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
                "scrape_method": "browserbase",
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

    async def scrape_all_parallel(self, sources, max_workers=10):
        """Scrape multiple sources in parallel"""
        print(f"\n{'='*70}")
        print(f"🚀 PARALLEL SCRAPING")
        print(f"{'='*70}")
        print(f"Sources: {len(sources)}")
        print(f"Max workers: {max_workers}")
        print(f"{'='*70}\n")

        # Scrape in parallel batches
        tasks = []
        for source_id in sources:
            tasks.append(self.scrape_source(source_id, max_articles=100, verbose=True))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Save all results
        for i, articles in enumerate(results):
            if isinstance(articles, Exception):
                print(f"❌ Error: {articles}")
                continue

            if articles:
                self.save_articles(sources[i], articles)

        # Print final stats
        print(f"\n{'='*70}")
        print(f"📊 SCRAPING SUMMARY")
        print(f"{'='*70}\n")

        for source_id, stats in self.stats['sources'].items():
            source_name = ALL_SOURCES[source_id]['name']
            print(f"   {source_name}:")
            print(f"      Articles: {stats['articles']}")
            print(f"      Time: {stats['time']:.1f}s ({stats['time']/stats['articles']:.1f}s/article)" if stats['articles'] > 0 else f"      Time: {stats['time']:.1f}s")
            print()

        print(f"   TOTAL: {self.stats['total_articles']} articles in {self.stats['total_time']:.1f}s")
        print(f"{'='*70}\n")

async def main():
    parser = argparse.ArgumentParser(description='Browserbase Content Scraper')
    parser.add_argument('--test', action='store_true',
                        help='Test with single source (Wharton)')
    parser.add_argument('--scrape', action='store_true',
                        help='Scrape all top 10 sources')
    parser.add_argument('--source', type=str,
                        help='Scrape specific source')
    parser.add_argument('--max-workers', type=int, default=10,
                        help='Max parallel sessions (default: 10)')

    args = parser.parse_args()

    scraper = BrowserbaseScraper(max_workers=args.max_workers)

    if args.test:
        print("🧪 TEST MODE: Scraping Wharton only\n")
        articles = await scraper.scrape_source('wharton', max_articles=10)
        if articles:
            scraper.save_articles('wharton', articles)

    elif args.source:
        if args.source not in TOP_10_SOURCES:
            print(f"❌ Unknown source: {args.source}")
            print(f"Available: {', '.join(TOP_10_SOURCES)}")
            return

        articles = await scraper.scrape_source(args.source, max_articles=100)
        if articles:
            scraper.save_articles(args.source, articles)

    elif args.scrape:
        await scraper.scrape_all_parallel(TOP_10_SOURCES, max_workers=args.max_workers)

    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
