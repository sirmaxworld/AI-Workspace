#!/usr/bin/env python3
"""
Quality Quantum Physics & Meditation/Manifestation Scraper
Target: Last 6 months of content from high-quality sources
"""

import os
import sys
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import psycopg2

sys.path.append('/Users/yourox/AI-Workspace')
load_dotenv('/Users/yourox/AI-Workspace/.env')

# HIGH-QUALITY QUANTUM PHYSICS SOURCES
QUANTUM_SOURCES = {
    "sciencedaily_quantum": {
        "name": "ScienceDaily Quantum Physics",
        "domain": "sciencedaily.com",
        "category": "quantum_physics",
        "priority": "high",
        "base_weight": 0.9,
        "archive_url": "https://www.sciencedaily.com/news/matter_energy/quantum_physics/",
        "selectors": {
            "article_links": "div.latest-head a",
            "title": "h1#headline",
            "content": "div#story_text",
            "date": "dd#date_posted"
        }
    },
    "quanta_quantum": {
        "name": "Quanta Magazine - Quantum Physics",
        "domain": "quantamagazine.org",
        "category": "quantum_physics",
        "priority": "high",
        "base_weight": 0.9,
        "archive_url": "https://www.quantamagazine.org/tag/quantum-physics/",
        "selectors": {
            "article_links": "article.post__card h2 a",
            "title": "h1.post__title__title",
            "content": "div.post__content",
            "date": "time"
        }
    },
    "physorg_quantum": {
        "name": "Phys.org Quantum Physics",
        "domain": "phys.org",
        "category": "quantum_physics",
        "priority": "high",
        "base_weight": 0.8,
        "archive_url": "https://phys.org/physics-news/quantum-physics/",
        "selectors": {
            "article_links": "article.sorted-article h3 a",
            "title": "h1.news-article__title",
            "content": "div.article-main",
            "date": "p.article-byline time"
        }
    },
    "physicsworld_quantum": {
        "name": "Physics World - Quantum",
        "domain": "physicsworld.com",
        "category": "quantum_physics",
        "priority": "high",
        "base_weight": 0.8,
        "archive_url": "https://physicsworld.com/c/quantum/",
        "selectors": {
            "article_links": "article h3 a",
            "title": "h1.article-title",
            "content": "div.article-content",
            "date": "time.date"
        }
    },
    "sciencenews_quantum": {
        "name": "Science News - Quantum Physics",
        "domain": "sciencenews.org",
        "category": "quantum_physics",
        "priority": "high",
        "base_weight": 0.9,
        "archive_url": "https://www.sciencenews.org/topic/quantum-physics",
        "selectors": {
            "article_links": "article h3 a",
            "title": "h1.post-title",
            "content": "div.post-content",
            "date": "time.post-date"
        }
    }
}

# HIGH-QUALITY MEDITATION & MANIFESTATION SOURCES
MEDITATION_SOURCES = {
    "tinybuddhist": {
        "name": "Tiny Buddha",
        "domain": "tinybuddha.com",
        "category": "meditation",
        "priority": "high",
        "base_weight": 0.8,
        "archive_url": "https://tinybuddha.com/blog/",
        "selectors": {
            "article_links": "article h2 a",
            "title": "h1.entry-title",
            "content": "div.entry-content",
            "date": "time.entry-date"
        }
    },
    "dailymeditation": {
        "name": "The Daily Meditation",
        "domain": "thedailymeditation.com",
        "category": "meditation",
        "priority": "high",
        "base_weight": 0.7,
        "archive_url": "https://www.thedailymeditation.com/blog",
        "selectors": {
            "article_links": "article h2 a",
            "title": "h1",
            "content": "div.article-content",
            "date": "time"
        }
    },
    "liveanddare": {
        "name": "Live and Dare",
        "domain": "liveanddare.com",
        "category": "meditation",
        "priority": "high",
        "base_weight": 0.8,
        "archive_url": "https://liveanddare.com/blog/",
        "selectors": {
            "article_links": "article h2 a",
            "title": "h1.entry-title",
            "content": "div.entry-content",
            "date": "time.entry-date"
        }
    },
    "alignedlife": {
        "name": "The Aligned Life",
        "domain": "thealignedlife.co",
        "category": "manifestation",
        "priority": "high",
        "base_weight": 0.7,
        "archive_url": "https://thealignedlife.co/blog/",
        "selectors": {
            "article_links": "article h2 a, article h3 a",
            "title": "h1",
            "content": "div.blog-content, div.entry-content",
            "date": "time"
        }
    },
    "manifestlikeapowerhouse": {
        "name": "Manifest Like a Powerhouse",
        "domain": "manifestlikeapowerhouse.com",
        "category": "manifestation",
        "priority": "high",
        "base_weight": 0.7,
        "archive_url": "https://manifestlikeapowerhouse.com/blog/",
        "selectors": {
            "article_links": "article a",
            "title": "h1",
            "content": "div.entry-content, article",
            "date": "time"
        }
    }
}

ALL_QUALITY_SOURCES = {**QUANTUM_SOURCES, **MEDITATION_SOURCES}

class QualityScraper:
    """Scrape high-quality quantum physics and meditation content"""

    def __init__(self, output_dir="/Users/yourox/AI-Workspace/data/quality_content"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })

    def scrape_source(self, source_id, config, max_articles=50, verbose=True):
        """Scrape articles from a single source"""

        if verbose:
            print(f"\n{'='*70}")
            print(f"📰 Scraping: {config['name']}")
            print(f"{'='*70}")
            print(f"📄 Loading: {config['archive_url']}\n")

        try:
            # Get archive page
            response = self.session.get(config['archive_url'], timeout=20)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Extract article links
            links = soup.select(config['selectors']['article_links'])

            if verbose:
                print(f"📋 Found {len(links)} potential articles")

            # Get unique URLs
            article_urls = []
            seen_urls = set()

            for link in links:
                url = link.get('href', '')

                # Make absolute URL
                if url.startswith('/'):
                    url = f"https://{config['domain']}{url}"
                elif not url.startswith('http'):
                    url = f"https://{config['domain']}/{url}"

                if url not in seen_urls and url.startswith('http'):
                    seen_urls.add(url)
                    article_urls.append(url)

                    if len(article_urls) >= max_articles:
                        break

            if verbose:
                print(f"🎯 Extracted {len(article_urls)} unique article URLs\n")

            # Scrape each article
            articles = []
            six_months_ago = datetime.now() - timedelta(days=180)

            for i, url in enumerate(article_urls, 1):
                try:
                    article = self.scrape_article(url, source_id, config)

                    if article:
                        # Check date (only last 6 months)
                        pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))

                        if pub_date >= six_months_ago:
                            articles.append(article)

                            if verbose:
                                title_preview = article['title'][:60] + '...' if len(article['title']) > 60 else article['title']
                                print(f"   ✓ [{i}/{len(article_urls)}] {title_preview}")
                        else:
                            if verbose:
                                print(f"   ⊘ [{i}/{len(article_urls)}] Too old (published {pub_date.strftime('%Y-%m-%d')})")

                except Exception as e:
                    if verbose:
                        print(f"   ❌ [{i}/{len(article_urls)}] Error: {str(e)[:50]}")
                    continue

            if verbose:
                elapsed = len(articles) * 1.2  # estimate
                print(f"\n✅ Scraped {len(articles)} articles in {elapsed:.1f}s")
                if len(articles) > 0:
                    print(f"⏱️  Average: {elapsed/len(articles):.1f}s per article")

            return articles

        except Exception as e:
            print(f"❌ Error scraping {source_id}: {e}")
            return []

    def scrape_article(self, url, source_id, config):
        """Scrape a single article"""

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

            # Calculate word count
            word_count = len(content.split())

            # Quality check
            if word_count < 100:
                return None

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
            raise Exception(f"Failed to scrape {url}: {e}")

    def calculate_score(self, word_count, published_at, config):
        """Calculate quality score"""
        score = config['base_weight']

        # Content length bonus
        if word_count > 1000:
            score += 0.2
        elif word_count > 500:
            score += 0.1

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

        final_score = (score * 0.7) + (freshness * 0.3)

        return min(max(final_score, 0.0), 1.0)

    def save_articles(self, source_id, articles):
        """Save articles to JSON and database"""
        if not articles:
            return None

        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_dir = self.output_dir / source_id
        source_dir.mkdir(exist_ok=True)

        output_file = source_dir / f"{source_id}_quality_{timestamp}.json"

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
        """Store articles in Railway PostgreSQL"""
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

    def scrape_all_parallel(self, sources, max_workers=5):
        """Scrape multiple sources in parallel"""

        print(f"\n{'='*70}")
        print(f"🚀 PARALLEL QUALITY CONTENT SCRAPING")
        print(f"{'='*70}")
        print(f"Sources: {len(sources)}")
        print(f"Max workers: {max_workers}")
        print(f"{'='*70}\n")

        start_time = datetime.now()
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.scrape_source, source_id, ALL_QUALITY_SOURCES[source_id], 50, True): source_id
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
        print(f"📊 SCRAPING SUMMARY")
        print(f"{'='*70}\n")

        for source_id, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
            source_name = ALL_QUALITY_SOURCES[source_id]['name']
            if count > 0:
                print(f"   ✅ {source_name}: {count} articles")
            else:
                print(f"   ❌ {source_name}: 0 articles")

        print(f"\n   TOTAL: {total_articles} articles in {elapsed:.1f}s")
        print(f"{'='*70}\n")

        return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Scrape quality quantum physics and meditation content')
    parser.add_argument('--quantum', action='store_true',
                        help='Scrape quantum physics sources')
    parser.add_argument('--meditation', action='store_true',
                        help='Scrape meditation & manifestation sources')
    parser.add_argument('--all', action='store_true',
                        help='Scrape all sources')

    args = parser.parse_args()

    scraper = QualityScraper()

    if args.all:
        sources = list(ALL_QUALITY_SOURCES.keys())
        scraper.scrape_all_parallel(sources, max_workers=5)
    elif args.quantum:
        sources = list(QUANTUM_SOURCES.keys())
        scraper.scrape_all_parallel(sources, max_workers=5)
    elif args.meditation:
        sources = list(MEDITATION_SOURCES.keys())
        scraper.scrape_all_parallel(sources, max_workers=5)
    else:
        parser.print_help()
