#!/usr/bin/env python3
"""
Premium Meditation & Manifestation Content Collector
Multi-method approach: RSS → Web Scraping → API
Focus: High quality, reputable sources only
"""

import os
import sys
import json
import hashlib
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import psycopg2

sys.path.append('/Users/yourox/AI-Workspace')
load_dotenv('/Users/yourox/AI-Workspace/.env')

# PREMIUM SOURCES - Tier 1 (Science-Based)
SCIENCE_SOURCES = {
    "greatergood": {
        "name": "Greater Good Science Center (UC Berkeley)",
        "domain": "greatergood.berkeley.edu",
        "category": "mindfulness_science",
        "priority": "critical",
        "base_weight": 1.0,
        "rss_url": "https://greatergood.berkeley.edu/feed",
        "archive_url": "https://greatergood.berkeley.edu/topic/mindfulness",
        "selectors": {
            "article_links": "article h3 a, article h2 a",
            "title": "h1.article-title, h1",
            "content": "div.article-body, div.article-content",
            "date": "time, span.date"
        }
    },
    "mindful": {
        "name": "Mindful Magazine",
        "domain": "mindful.org",
        "category": "mindfulness_practice",
        "priority": "critical",
        "base_weight": 0.95,
        "rss_url": "https://www.mindful.org/feed/",
        "archive_url": "https://www.mindful.org/meditation/",
        "selectors": {
            "article_links": "article h2 a, h3 a",
            "title": "h1.entry-title, h1",
            "content": "div.entry-content, article",
            "date": "time.entry-date, time"
        }
    },
    "lionsroar": {
        "name": "Lion's Roar Buddhist Magazine",
        "domain": "lionsroar.com",
        "category": "buddhist_meditation",
        "priority": "high",
        "base_weight": 0.9,
        "rss_url": "https://www.lionsroar.com/feed/",
        "archive_url": "https://www.lionsroar.com/category/practice/",
        "selectors": {
            "article_links": "article h2 a, h3 a",
            "title": "h1.article-title, h1",
            "content": "div.article-content, div.entry-content",
            "date": "time.published, time"
        }
    },
    "tricycle": {
        "name": "Tricycle Buddhist Review",
        "domain": "tricycle.org",
        "category": "buddhist_meditation",
        "priority": "high",
        "base_weight": 0.9,
        "rss_url": "https://tricycle.org/feed/",
        "archive_url": "https://tricycle.org/beginners/",
        "selectors": {
            "article_links": "article h2 a, h3 a",
            "title": "h1.entry-title, h1",
            "content": "div.entry-content, article",
            "date": "time, span.date"
        }
    }
}

# PREMIUM SOURCES - Tier 2 (Respected Teachers)
TEACHER_SOURCES = {
    "tarabrach": {
        "name": "Tara Brach",
        "domain": "tarabrach.com",
        "category": "meditation_teacher",
        "priority": "high",
        "base_weight": 0.9,
        "rss_url": "https://www.tarabrach.com/feed/podcast/",
        "archive_url": "https://www.tarabrach.com/articles/",
        "selectors": {
            "article_links": "article a, h2 a",
            "title": "h1, h1.entry-title",
            "content": "div.entry-content, article",
            "date": "time, span.date"
        }
    },
    "jackkornfield": {
        "name": "Jack Kornfield",
        "domain": "jackkornfield.com",
        "category": "meditation_teacher",
        "priority": "high",
        "base_weight": 0.9,
        "rss_url": None,  # Try to find
        "archive_url": "https://jackkornfield.com/blog/",
        "selectors": {
            "article_links": "article h2 a, h3 a",
            "title": "h1.entry-title, h1",
            "content": "div.entry-content, article",
            "date": "time, span.date"
        }
    },
    "sharonsalzberg": {
        "name": "Sharon Salzberg",
        "domain": "sharonsalzberg.com",
        "category": "meditation_teacher",
        "priority": "high",
        "base_weight": 0.9,
        "rss_url": None,  # Try to find
        "archive_url": "https://www.sharonsalzberg.com/blog/",
        "selectors": {
            "article_links": "article h2 a, h3 a",
            "title": "h1, h1.entry-title",
            "content": "div.entry-content, article",
            "date": "time, span.date"
        }
    },
    "pemachodron": {
        "name": "Pema Chödrön",
        "domain": "pemachodronfoundation.org",
        "category": "meditation_teacher",
        "priority": "high",
        "base_weight": 0.9,
        "rss_url": None,  # Try to find
        "archive_url": "https://pemachodronfoundation.org/teachings/",
        "selectors": {
            "article_links": "article a, h2 a",
            "title": "h1",
            "content": "div.content, article",
            "date": "time, span.date"
        }
    }
}

# PREMIUM SOURCES - Tier 3 (Modern Consciousness)
CONSCIOUSNESS_SOURCES = {
    "eckharttolle": {
        "name": "Eckhart Tolle",
        "domain": "eckharttolle.com",
        "category": "consciousness",
        "priority": "high",
        "base_weight": 0.85,
        "rss_url": None,  # Try to find
        "archive_url": "https://www.eckharttolle.com/articles/",
        "selectors": {
            "article_links": "article a, h2 a, h3 a",
            "title": "h1",
            "content": "div.article-content, article",
            "date": "time, span.date"
        }
    },
    "chopra": {
        "name": "Deepak Chopra",
        "domain": "chopra.com",
        "category": "consciousness",
        "priority": "high",
        "base_weight": 0.85,
        "rss_url": "https://chopra.com/feed",
        "archive_url": "https://chopra.com/articles/meditation",
        "selectors": {
            "article_links": "article h2 a, h3 a",
            "title": "h1",
            "content": "div.article-content, article",
            "date": "time, span.date"
        }
    },
    "gabbybernstein": {
        "name": "Gabby Bernstein",
        "domain": "gabbybernstein.com",
        "category": "manifestation",
        "priority": "medium",
        "base_weight": 0.8,
        "rss_url": "https://gabbybernstein.com/feed/",
        "archive_url": "https://gabbybernstein.com/blog/",
        "selectors": {
            "article_links": "article a, h2 a",
            "title": "h1",
            "content": "div.entry-content, article",
            "date": "time, span.date"
        }
    }
}

ALL_PREMIUM_SOURCES = {**SCIENCE_SOURCES, **TEACHER_SOURCES, **CONSCIOUSNESS_SOURCES}

class PremiumCollector:
    """Multi-method premium content collector"""

    def __init__(self, output_dir="/Users/yourox/AI-Workspace/data/premium_meditation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        })

        self.min_word_count = 200  # Higher quality threshold
        self.six_months_ago = datetime.now() - timedelta(days=180)

    def collect_source(self, source_id, config, max_articles=50, verbose=True):
        """Try multiple methods to collect content"""

        if verbose:
            print(f"\n{'='*70}")
            print(f"📰 Collecting: {config['name']}")
            print(f"{'='*70}")
            print(f"Category: {config['category']} | Priority: {config['priority']}")

        articles = []

        # Method 1: Try RSS first
        if config.get('rss_url'):
            if verbose:
                print(f"📡 Method 1: RSS Feed")
            articles = self.collect_via_rss(source_id, config, max_articles, verbose)

        # Method 2: Fallback to web scraping
        if len(articles) == 0 and config.get('archive_url'):
            if verbose:
                print(f"🌐 Method 2: Web Scraping (RSS failed or empty)")
            articles = self.collect_via_scraping(source_id, config, max_articles, verbose)

        return articles

    def collect_via_rss(self, source_id, config, max_articles, verbose):
        """Collect via RSS feed"""

        try:
            if verbose:
                print(f"   Loading: {config['rss_url']}")

            response = self.session.get(config['rss_url'], timeout=20)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if verbose:
                print(f"   ✅ Found {len(feed.entries)} RSS entries")

            articles = []
            for entry in feed.entries[:max_articles]:
                try:
                    # Get full article content by fetching URL
                    article_url = entry.get('link', '')
                    if not article_url:
                        continue

                    article = self.fetch_full_article(article_url, source_id, config)

                    if article and self.is_high_quality(article):
                        # Check date
                        pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))

                        if pub_date >= self.six_months_ago:
                            articles.append(article)

                            if verbose:
                                title_preview = article['title'][:60] + '...' if len(article['title']) > 60 else article['title']
                                print(f"   ✓ [{len(articles)}] {title_preview} ({article['content_length']} words)")

                except Exception as e:
                    if verbose:
                        print(f"   ⚠️  Skipped entry: {str(e)[:50]}")
                    continue

            if verbose:
                print(f"   {'✅' if articles else '❌'} RSS: {len(articles)} high-quality articles")

            return articles

        except Exception as e:
            if verbose:
                print(f"   ❌ RSS failed: {e}")
            return []

    def collect_via_scraping(self, source_id, config, max_articles, verbose):
        """Collect via web scraping"""

        try:
            if verbose:
                print(f"   Loading: {config['archive_url']}")

            response = self.session.get(config['archive_url'], timeout=20)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Find article links
            links = soup.select(config['selectors']['article_links'])

            if verbose:
                print(f"   ✅ Found {len(links)} article links")

            # Extract unique URLs
            article_urls = []
            seen_urls = set()

            for link in links:
                url = link.get('href', '')

                # Make absolute URL
                if url.startswith('/'):
                    url = f"https://{config['domain']}{url}"
                elif not url.startswith('http'):
                    continue

                if url not in seen_urls:
                    seen_urls.add(url)
                    article_urls.append(url)

                    if len(article_urls) >= max_articles:
                        break

            # Fetch full articles
            articles = []
            for i, url in enumerate(article_urls, 1):
                try:
                    article = self.fetch_full_article(url, source_id, config)

                    if article and self.is_high_quality(article):
                        pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))

                        if pub_date >= self.six_months_ago:
                            articles.append(article)

                            if verbose:
                                title_preview = article['title'][:60] + '...' if len(article['title']) > 60 else article['title']
                                print(f"   ✓ [{len(articles)}] {title_preview} ({article['content_length']} words)")

                except Exception as e:
                    if verbose:
                        print(f"   ⚠️  [{i}/{len(article_urls)}] Failed: {str(e)[:40]}")
                    continue

            if verbose:
                print(f"   {'✅' if articles else '❌'} Scraping: {len(articles)} high-quality articles")

            return articles

        except Exception as e:
            if verbose:
                print(f"   ❌ Scraping failed: {e}")
            return []

    def fetch_full_article(self, url, source_id, config):
        """Fetch and parse full article"""

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Extract title
            title_elem = soup.select_one(config['selectors']['title'])
            title = title_elem.get_text(strip=True) if title_elem else ""

            if not title:
                return None

            # Extract content
            content_elem = soup.select_one(config['selectors']['content'])
            content = content_elem.get_text(separator=' ', strip=True) if content_elem else ""

            # Extract date
            date_elem = soup.select_one(config['selectors']['date'])

            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                try:
                    published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    published_at = datetime.now()
            else:
                published_at = datetime.now()

            # Generate content ID
            content_id = hashlib.md5(url.encode()).hexdigest()

            # Word count
            word_count = len(content.split())

            return {
                "content_id": content_id,
                "source_id": source_id,
                "source_name": config['name'],
                "title": title,
                "url": url,
                "author": "Staff Writer",
                "published_at": published_at.isoformat(),
                "fetched_at": datetime.now().isoformat(),
                "content_type": "article",
                "content_text": content,
                "content_length": word_count,
                "category": config['category'],
                "priority": config['priority'],
                "base_weight": config['base_weight'],
                "raw_score": self.calculate_score(word_count, published_at, config)
            }

        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {e}")

    def is_high_quality(self, article):
        """Quality check for articles"""
        return (
            article['content_length'] >= self.min_word_count and
            len(article['title']) >= 10 and
            len(article['title']) <= 200
        )

    def calculate_score(self, word_count, published_at, config):
        """Calculate quality score"""
        score = config['base_weight']

        # Content length bonus
        if word_count > 1500:
            score += 0.1
        elif word_count > 800:
            score += 0.05

        # Freshness
        days_old = (datetime.now() - published_at).days
        if days_old <= 7:
            freshness = 1.0
        elif days_old <= 30:
            freshness = 0.8
        elif days_old <= 90:
            freshness = 0.6
        else:
            freshness = 0.4

        final_score = (score * 0.7) + (freshness * 0.3)

        return min(max(final_score, 0.0), 1.0)

    def save_articles(self, source_id, articles):
        """Save to JSON and database"""
        if not articles:
            return None

        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_dir = self.output_dir / source_id
        source_dir.mkdir(exist_ok=True)

        output_file = source_dir / f"{source_id}_premium_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                "source_id": source_id,
                "source_name": articles[0]['source_name'],
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

        return str(output_file)

    def save_to_database(self, source_id, articles):
        """Store in Railway PostgreSQL"""
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

    def collect_all_parallel(self, sources, max_workers=3):
        """Collect from multiple sources in parallel"""

        print(f"\n{'='*70}")
        print(f"🎯 PREMIUM MEDITATION & MANIFESTATION COLLECTION")
        print(f"{'='*70}")
        print(f"Sources: {len(sources)}")
        print(f"Quality threshold: {self.min_word_count}+ words")
        print(f"Date range: Last 6 months")
        print(f"{'='*70}\n")

        start_time = datetime.now()
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.collect_source, source_id, ALL_PREMIUM_SOURCES[source_id], 50, True): source_id
                for source_id in sources
            }

            for future in futures:
                source_id = futures[future]
                try:
                    articles = future.result()
                    if articles:
                        self.save_articles(source_id, articles)
                        results[source_id] = len(articles)
                    else:
                        results[source_id] = 0
                except Exception as e:
                    print(f"❌ Error with {source_id}: {e}")
                    results[source_id] = 0

        # Summary
        elapsed = (datetime.now() - start_time).total_seconds()
        total_articles = sum(results.values())

        print(f"\n{'='*70}")
        print(f"📊 COLLECTION SUMMARY")
        print(f"{'='*70}\n")

        for source_id, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
            source_name = ALL_PREMIUM_SOURCES[source_id]['name']
            if count > 0:
                print(f"   ✅ {source_name}: {count} articles")
            else:
                print(f"   ❌ {source_name}: 0 articles")

        print(f"\n   TOTAL: {total_articles} premium articles in {elapsed:.1f}s")
        print(f"   AVERAGE: {elapsed/total_articles:.1f}s per article" if total_articles > 0 else "")
        print(f"{'='*70}\n")

        return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Collect premium meditation content')
    parser.add_argument('--science', action='store_true',
                        help='Science-based sources only')
    parser.add_argument('--teachers', action='store_true',
                        help='Respected teachers only')
    parser.add_argument('--consciousness', action='store_true',
                        help='Modern consciousness teachers')
    parser.add_argument('--all', action='store_true',
                        help='All premium sources')

    args = parser.parse_args()

    collector = PremiumCollector()

    if args.all:
        sources = list(ALL_PREMIUM_SOURCES.keys())
        collector.collect_all_parallel(sources, max_workers=3)
    elif args.science:
        sources = list(SCIENCE_SOURCES.keys())
        collector.collect_all_parallel(sources, max_workers=3)
    elif args.teachers:
        sources = list(TEACHER_SOURCES.keys())
        collector.collect_all_parallel(sources, max_workers=3)
    elif args.consciousness:
        sources = list(CONSCIOUSNESS_SOURCES.keys())
        collector.collect_all_parallel(sources, max_workers=3)
    else:
        parser.print_help()
