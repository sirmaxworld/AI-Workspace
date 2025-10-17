#!/usr/bin/env python3
"""
Pinkbike Collector for Cycling Trends Domain
Collects articles, reviews, field tests, and comments from Pinkbike.com
Uses Browserbase to bypass bot protection
"""

import os
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from browserbase import Browserbase
from playwright.sync_api import sync_playwright

# Load environment
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / '.env')


class PinkbikeCollector:
    """Collects content from Pinkbike.com using Browserbase"""

    def __init__(self, domain_path: Path):
        self.domain_path = Path(domain_path)
        self.config = self._load_config()

        # Browserbase credentials
        self.api_key = os.getenv('BROWSERBASE_API_KEY')
        self.project_id = os.getenv('BROWSERBASE_PROJECT_ID')

        if not self.api_key or not self.project_id:
            raise ValueError("Browserbase credentials not found in .env")

        # Directories
        self.articles_dir = project_root / 'data' / 'pinkbike_articles'
        self.metadata_file = self.domain_path / 'pinkbike_articles.json'

        # Ensure directories exist
        self.articles_dir.mkdir(parents=True, exist_ok=True)

        print(f"🚴 Pinkbike Collector for: {self.config.get('display_name', 'Cycling Trends')}")

    def _load_config(self) -> Dict:
        """Load domain configuration"""
        config_file = self.domain_path / 'config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}

    def create_browser_session(self):
        """Create a Browserbase session"""
        bb = Browserbase(api_key=self.api_key)
        session = bb.sessions.create(project_id=self.project_id)
        print(f"✅ Browserbase session created: {session.id}")
        return bb, session.id

    def close_browser_session(self, bb, session_id):
        """Close Browserbase session"""
        try:
            bb.sessions.delete(session_id)
            print(f"🧹 Session closed")
        except:
            pass

    def extract_article_urls(self, section_url: str, max_articles: int = 10) -> List[str]:
        """
        Extract article URLs from a Pinkbike section (news, reviews, field-test)

        Args:
            section_url: URL of the section (e.g., https://www.pinkbike.com/news/tags/reviews/)
            max_articles: Maximum number of articles to extract

        Returns:
            List of article URLs
        """
        print(f"\n🔍 Extracting article URLs from: {section_url}")

        bb, session_id = self.create_browser_session()
        article_urls = []

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(
                    f"wss://connect.browserbase.com?apiKey={self.api_key}&sessionId={session_id}"
                )

                context = browser.contexts[0]
                page = context.pages[0]

                print(f"🔗 Navigating to: {section_url}")
                page.goto(section_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(3)

                # Pinkbike article links are typically in article cards
                # Look for article links in the main content area
                article_selectors = [
                    'article a.title',
                    'article h3 a',
                    'div.news-list-item a.title',
                    'div.article-card a.title',
                    'a[href*="/news/"]'
                ]

                for selector in article_selectors:
                    try:
                        links = page.locator(selector).all()
                        for link in links[:max_articles]:
                            try:
                                href = link.get_attribute('href')
                                if href and '/news/' in href:
                                    # Make absolute URL
                                    if href.startswith('/'):
                                        full_url = f"https://www.pinkbike.com{href}"
                                    elif not href.startswith('http'):
                                        full_url = f"https://www.pinkbike.com/{href}"
                                    else:
                                        full_url = href

                                    if full_url not in article_urls:
                                        article_urls.append(full_url)

                                        if len(article_urls) >= max_articles:
                                            break
                            except:
                                continue

                        if article_urls:
                            break  # Found articles with this selector
                    except:
                        continue

                print(f"✅ Found {len(article_urls)} article URLs")

        except Exception as e:
            print(f"❌ Error extracting URLs: {e}")
        finally:
            self.close_browser_session(bb, session_id)

        return article_urls

    def extract_article_content(self, article_url: str) -> Optional[Dict]:
        """
        Extract full article content including metadata and comments

        Args:
            article_url: URL of the article

        Returns:
            Dict with article data or None on failure
        """
        print(f"\n📰 Extracting article: {article_url}")

        # Generate article ID from URL
        article_id = re.sub(r'[^a-zA-Z0-9_-]', '_', article_url.split('/')[-1])
        if not article_id:
            article_id = re.sub(r'[^a-zA-Z0-9_-]', '_', article_url)[-50:]

        bb, session_id = self.create_browser_session()

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(
                    f"wss://connect.browserbase.com?apiKey={self.api_key}&sessionId={session_id}"
                )

                context = browser.contexts[0]
                page = context.pages[0]

                print(f"  🔗 Loading article...")
                page.goto(article_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(3)

                # Extract title
                title = ""
                title_selectors = ['h1', 'h1.title', 'article h1', '.article-title']
                for selector in title_selectors:
                    try:
                        title_elem = page.locator(selector).first
                        if title_elem:
                            title = title_elem.inner_text()
                            if title:
                                break
                    except:
                        continue

                if not title:
                    title = "Unknown Title"

                print(f"  📄 Title: {title[:60]}...")

                # Extract author
                author = ""
                author_selectors = ['.author-name', '.by-author', 'span.author', 'a[rel="author"]']
                for selector in author_selectors:
                    try:
                        author_elem = page.locator(selector).first
                        if author_elem:
                            author = author_elem.inner_text()
                            if author:
                                break
                    except:
                        continue

                # Extract publish date
                publish_date = ""
                date_selectors = ['time', '.publish-date', '.date', 'time[datetime]']
                for selector in date_selectors:
                    try:
                        date_elem = page.locator(selector).first
                        if date_elem:
                            publish_date = date_elem.get_attribute('datetime') or date_elem.inner_text()
                            if publish_date:
                                break
                    except:
                        continue

                # Extract categories/tags
                tags = []
                tag_selectors = ['.tags a', '.categories a', 'a[href*="/tags/"]']
                for selector in tag_selectors:
                    try:
                        tag_elems = page.locator(selector).all()
                        for tag_elem in tag_elems:
                            tag_text = tag_elem.inner_text()
                            if tag_text and tag_text not in tags:
                                tags.append(tag_text.strip())
                    except:
                        continue

                # Extract article body content
                content = ""
                content_selectors = [
                    '.blog-body',
                    '.blog-section-inside',
                    'article .body',
                    '.article-body',
                    'div[itemprop="articleBody"]'
                ]
                for selector in content_selectors:
                    try:
                        content_elem = page.locator(selector).first
                        if content_elem:
                            content = content_elem.inner_text()
                            if content and len(content) > 100:
                                break
                    except:
                        continue

                if not content:
                    # Fallback: try to get all sections from blog-body
                    try:
                        sections = page.locator('.blog-section .blog-section-inside').all()
                        content = '\n\n'.join([s.inner_text() for s in sections if s.inner_text()])
                    except:
                        content = ""

                print(f"  📝 Content length: {len(content)} chars")

                # ====== ENHANCED METADATA EXTRACTION ======

                # Extract author bio/credentials
                author_bio = ""
                author_role = ""
                bio_selectors = ['.author-bio', '.author-description', '.bio']
                for selector in bio_selectors:
                    try:
                        bio_elem = page.locator(selector).first
                        if bio_elem:
                            author_bio = bio_elem.inner_text()
                            break
                    except:
                        continue

                role_selectors = ['.author-role', '.author-title', 'span.role']
                for selector in role_selectors:
                    try:
                        role_elem = page.locator(selector).first
                        if role_elem:
                            author_role = role_elem.inner_text()
                            break
                    except:
                        continue

                # Extract view count / engagement
                view_count = 0
                view_selectors = ['.view-count', '.views', 'span.views', '[data-views]']
                for selector in view_selectors:
                    try:
                        view_elem = page.locator(selector).first
                        if view_elem:
                            view_text = view_elem.inner_text() or view_elem.get_attribute('data-views') or "0"
                            # Parse views (handle K, M notation)
                            view_text = view_text.strip().replace(',', '').replace(' views', '')
                            if 'K' in view_text.upper():
                                view_count = int(float(view_text.upper().replace('K', '')) * 1000)
                            elif 'M' in view_text.upper():
                                view_count = int(float(view_text.upper().replace('M', '')) * 1000000)
                            else:
                                try:
                                    view_count = int(view_text)
                                except:
                                    view_count = 0
                            break
                    except:
                        continue

                # Extract ratings/scores (if present)
                rating = None
                rating_selectors = ['.rating', '.score', '[itemprop="ratingValue"]', 'span.rating-value']
                for selector in rating_selectors:
                    try:
                        rating_elem = page.locator(selector).first
                        if rating_elem:
                            rating_text = rating_elem.inner_text() or rating_elem.get_attribute('content') or ""
                            try:
                                rating = float(rating_text.strip().split('/')[0])
                                break
                            except:
                                continue
                    except:
                        continue

                # Count images (Pinkbike uses .news-photo class)
                image_count = 0
                try:
                    images = page.locator('.news-photo, .blog-body img').all()
                    image_count = len(images)
                except:
                    pass

                # Count videos
                video_count = 0
                try:
                    videos = page.locator('.blog-body video, .blog-body iframe[src*="youtube"], .blog-body iframe[src*="vimeo"]').all()
                    video_count = len(videos)
                except:
                    pass

                # Extract update date if different from publish
                update_date = ""
                update_selectors = ['.updated-date', '.modified-date', 'time[itemprop="dateModified"]']
                for selector in update_selectors:
                    try:
                        update_elem = page.locator(selector).first
                        if update_elem:
                            update_date = update_elem.get_attribute('datetime') or update_elem.inner_text()
                            if update_date and update_date != publish_date:
                                break
                    except:
                        continue

                # Extract social shares if available
                social_shares = {}
                try:
                    share_selectors = {
                        'facebook': '.facebook-shares, [data-facebook-shares]',
                        'twitter': '.twitter-shares, [data-twitter-shares]',
                        'total': '.total-shares, [data-total-shares]'
                    }
                    for platform, selector in share_selectors.items():
                        try:
                            share_elem = page.locator(selector).first
                            if share_elem:
                                share_text = share_elem.inner_text() or share_elem.get_attribute(f'data-{platform}-shares') or "0"
                                try:
                                    social_shares[platform] = int(share_text.strip().replace(',', ''))
                                except:
                                    pass
                        except:
                            pass
                except:
                    pass

                print(f"  📊 Engagement: {view_count} views, {image_count} images, {video_count} videos")

                # Extract products mentioned (if any)
                products = []
                product_selectors = [
                    '.product-mention',
                    '.gear-mentioned',
                    'a[href*="/products/"]',
                    'span.product-name'
                ]
                for selector in product_selectors:
                    try:
                        product_elems = page.locator(selector).all()
                        for prod_elem in product_elems:
                            prod_text = prod_elem.inner_text()
                            if prod_text and prod_text not in products:
                                products.append(prod_text.strip())
                    except:
                        continue

                # Scroll to load comments
                print(f"  💬 Loading comments...")
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)

                    # Try to load more comments
                    for _ in range(3):
                        try:
                            load_more_selectors = [
                                'button:has-text("Load more")',
                                'button:has-text("Show more")',
                                '.load-more-comments'
                            ]
                            for selector in load_more_selectors:
                                try:
                                    button = page.locator(selector).first
                                    if button and button.is_visible(timeout=2000):
                                        button.click()
                                        time.sleep(2)
                                        break
                                except:
                                    continue
                        except:
                            break
                except:
                    pass

                # Extract comments (Pinkbike uses .cmcont for comment containers)
                comments = []
                comment_selectors = [
                    '.cmcont',
                    '.comment',
                    '.comment-item',
                    'div[data-comment-id]'
                ]

                for selector in comment_selectors:
                    try:
                        comment_elems = page.locator(selector).all()

                        if len(comment_elems) > 0:
                            print(f"  💬 Found {len(comment_elems)} comment elements with selector: {selector}")

                            for comment_elem in comment_elems[:50]:  # Limit to 50 comments
                                try:
                                    # Extract comment author (Pinkbike uses .commentUser)
                                    comment_author = ""
                                    author_sels = ['.commentUser', '.comment-author', '.author', 'a.username', '.user-name']
                                    for auth_sel in author_sels:
                                        try:
                                            auth_elem = comment_elem.locator(auth_sel).first
                                            if auth_elem:
                                                comment_author = auth_elem.inner_text()
                                                if comment_author:
                                                    break
                                        except:
                                            continue

                                    # Extract comment text
                                    comment_text = ""
                                    # Try to get all text from the comment, excluding nested replies
                                    try:
                                        # Get direct text content, excluding child comment containers
                                        full_text = comment_elem.inner_text()
                                        # Try to filter out author name if it's included
                                        if comment_author and comment_author in full_text:
                                            comment_text = full_text.replace(comment_author, '', 1).strip()
                                        else:
                                            comment_text = full_text

                                        # Take first reasonable chunk if too long
                                        if len(comment_text) > 1000:
                                            comment_text = comment_text[:1000]
                                    except:
                                        pass

                                    if not comment_text or len(comment_text) < 10:
                                        # Fallback: try specific selectors
                                        text_sels = ['.comment-body', '.comment-text', '.text', 'p']
                                        for text_sel in text_sels:
                                            try:
                                                text_elem = comment_elem.locator(text_sel).first
                                                if text_elem:
                                                    comment_text = text_elem.inner_text()
                                                    if comment_text and len(comment_text) > 10:
                                                        break
                                            except:
                                                continue

                                    # Extract upvotes/likes
                                    likes = 0
                                    like_sels = [
                                        '.vote-count',
                                        '.likes-count',
                                        'span.count',
                                        '[data-votes]',
                                        '.f-right'  # Pinkbike might use this
                                    ]
                                    for like_sel in like_sels:
                                        try:
                                            like_elem = comment_elem.locator(like_sel).first
                                            if like_elem:
                                                like_text = like_elem.inner_text() or like_elem.get_attribute('data-votes') or "0"
                                                # Parse likes (handle K, M notation)
                                                like_text = like_text.strip().replace(',', '')
                                                if 'K' in like_text.upper():
                                                    likes = int(float(like_text.upper().replace('K', '')) * 1000)
                                                elif 'M' in like_text.upper():
                                                    likes = int(float(like_text.upper().replace('M', '')) * 1000000)
                                                else:
                                                    try:
                                                        likes = int(like_text)
                                                    except:
                                                        likes = 0
                                                if likes > 0:
                                                    break
                                        except:
                                            continue

                                    # Extract timestamp
                                    timestamp = ""
                                    time_sels = ['time', '.comment-time', '.timestamp', '.fgrey']
                                    for time_sel in time_sels:
                                        try:
                                            time_elem = comment_elem.locator(time_sel).first
                                            if time_elem:
                                                timestamp = time_elem.get_attribute('datetime') or time_elem.inner_text()
                                                if timestamp:
                                                    break
                                        except:
                                            continue

                                    if comment_text and len(comment_text) > 10:
                                        comments.append({
                                            'author': comment_author.strip(),
                                            'text': comment_text.strip(),
                                            'likes': likes,
                                            'timestamp': timestamp
                                        })
                                except Exception as e:
                                    continue

                            if comments:
                                break  # Found comments with this selector
                    except:
                        continue

                # Sort comments by likes (descending)
                comments.sort(key=lambda x: x['likes'], reverse=True)

                print(f"  ✅ Extracted {len(comments)} comments")

                # Build result with enhanced metadata
                result = {
                    'article_id': article_id,
                    'url': article_url,
                    'title': title.strip(),
                    'author': {
                        'name': author.strip(),
                        'role': author_role.strip() if author_role else "",
                        'bio': author_bio.strip() if author_bio else ""
                    },
                    'dates': {
                        'published': publish_date,
                        'updated': update_date if update_date else publish_date
                    },
                    'tags': tags,
                    'content': content.strip(),
                    'products_mentioned': products,
                    'engagement': {
                        'view_count': view_count,
                        'comment_count': len(comments),
                        'social_shares': social_shares if social_shares else {}
                    },
                    'media': {
                        'image_count': image_count,
                        'video_count': video_count
                    },
                    'rating': rating,  # Overall rating if present
                    'comments': {
                        'count': len(comments),
                        'items': comments,
                        'top_engagement': comments[0]['likes'] if comments else 0,
                        'verified_owners': len([c for c in comments if 'verified' in c.get('author', '').lower()]),
                        'avg_comment_length': sum(len(c['text']) for c in comments) // len(comments) if comments else 0
                    },
                    'extraction_metadata': {
                        'extracted_at': datetime.now().isoformat(),
                        'method': 'browserbase',
                        'collector_version': '2.0'  # Enhanced version
                    },
                    'status': 'success'
                }

                return result

        except Exception as e:
            print(f"  ❌ Error extracting article: {e}")
            return {
                'article_id': article_id,
                'url': article_url,
                'error': str(e),
                'status': 'error'
            }
        finally:
            self.close_browser_session(bb, session_id)

    def save_article(self, article_data: Dict) -> Path:
        """Save article data to JSON file"""
        article_id = article_data.get('article_id', 'unknown')
        output_path = self.articles_dir / f"{article_id}_full.json"

        with open(output_path, 'w') as f:
            json.dump(article_data, f, indent=2)

        print(f"  💾 Saved to: {output_path}")
        return output_path

    def collect_section(self, section_url: str, max_articles: int = 10) -> List[Dict]:
        """
        Collect articles from a Pinkbike section

        Args:
            section_url: URL of the section
            max_articles: Maximum number of articles to collect

        Returns:
            List of article data dictionaries
        """
        print(f"\n{'='*70}")
        print(f"🚴 Collecting from: {section_url}")
        print(f"{'='*70}")

        # Step 1: Get article URLs
        article_urls = self.extract_article_urls(section_url, max_articles)

        if not article_urls:
            print("❌ No articles found")
            return []

        # Step 2: Extract each article
        articles = []
        for i, url in enumerate(article_urls, 1):
            print(f"\n[{i}/{len(article_urls)}]")
            article_data = self.extract_article_content(url)

            if article_data and article_data.get('status') == 'success':
                self.save_article(article_data)
                articles.append(article_data)

                # Be respectful - add delay between requests
                if i < len(article_urls):
                    time.sleep(5)
            else:
                print(f"  ⚠️  Skipped: {url}")

        return articles

    def collect_all(self, max_articles_per_section: int = 10) -> Dict:
        """
        Collect articles from all configured sections

        Args:
            max_articles_per_section: Maximum articles to collect per section

        Returns:
            Collection statistics
        """
        print(f"\n{'='*70}")
        print(f"🚀 PINKBIKE COLLECTION STARTED")
        print(f"{'='*70}\n")

        sections = self.config.get('pinkbike', {}).get('sections', [])

        if not sections:
            # Default sections
            sections = [
                "https://www.pinkbike.com/news/tags/reviews/",
                "https://www.pinkbike.com/news/tags/field-test/",
                "https://www.pinkbike.com/news/"
            ]

        all_articles = []
        stats = {
            'sections_processed': 0,
            'articles_collected': 0,
            'comments_collected': 0,
            'products_found': 0
        }

        for section_url in sections:
            articles = self.collect_section(section_url, max_articles_per_section)

            for article in articles:
                if article.get('status') == 'success':
                    stats['articles_collected'] += 1
                    stats['comments_collected'] += article.get('comments', {}).get('count', 0)
                    stats['products_found'] += len(article.get('products_mentioned', []))

            all_articles.extend(articles)
            stats['sections_processed'] += 1

            # Delay between sections
            time.sleep(10)

        # Save metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(all_articles, f, indent=2)

        # Print summary
        print(f"\n{'='*70}")
        print(f"✅ COLLECTION COMPLETE!")
        print(f"{'='*70}")
        print(f"Sections processed: {stats['sections_processed']}")
        print(f"Articles collected: {stats['articles_collected']}")
        print(f"Comments collected: {stats['comments_collected']}")
        print(f"Products found: {stats['products_found']}")
        print(f"\n📁 Metadata saved to: {self.metadata_file}")
        print(f"📁 Articles saved to: {self.articles_dir}")
        print(f"{'='*70}\n")

        return stats


def main():
    """Main execution"""
    import sys

    if len(sys.argv) < 2:
        domain_path = Path("/Users/yourox/AI-Workspace/domains/cycling_trends")
    else:
        domain_path = Path(sys.argv[1])

    if not domain_path.exists():
        print(f"✗ Domain path does not exist: {domain_path}")
        print("Creating directory...")
        domain_path.mkdir(parents=True, exist_ok=True)

    collector = PinkbikeCollector(domain_path)

    # Collect articles (default: 10 per section, can be customized)
    max_articles = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    collector.collect_all(max_articles_per_section=max_articles)


if __name__ == '__main__':
    main()
