#!/usr/bin/env python3
"""
Beautiful Soup + Proxy Scraper for YouTube
Bypasses IP blocks using rotating proxies and random user agents
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, List, Optional
from fake_useragent import UserAgent


class ProxyScraper:
    """YouTube scraper with optional proxy rotation and Beautiful Soup"""

    def __init__(self, use_proxies: bool = False):
        self.ua = UserAgent()
        self.use_proxies = use_proxies
        self.current_proxy = None
        self.proxy_failures = 0
        self.max_proxy_retries = 5

        # Optional: Add your own proxy list here
        self.proxy_list = [
            # 'http://proxy1:port',
            # 'http://proxy2:port',
        ]
        self.proxy_index = 0

    def get_random_headers(self) -> dict:
        """Generate random headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def get_working_proxy(self) -> Optional[str]:
        """Get a working proxy from the pool"""
        if not self.proxy_list or not self.use_proxies:
            return None

        try:
            # Rotate through proxy list
            if self.proxy_index >= len(self.proxy_list):
                self.proxy_index = 0

            proxy = self.proxy_list[self.proxy_index]
            self.proxy_index += 1

            print(f"   🔄 Testing proxy: {proxy}")

            # Quick test
            response = requests.get(
                'https://www.youtube.com',
                proxies={'http': proxy, 'https': proxy},
                timeout=10,
                headers=self.get_random_headers()
            )

            if response.status_code == 200:
                print(f"   ✅ Proxy working: {proxy}")
                return proxy
            else:
                print(f"   ❌ Proxy failed: {proxy}")
                return None

        except Exception as e:
            print(f"   ❌ Proxy error: {e}")
            return None

    def fetch_with_proxy(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch URL with automatic proxy rotation on failure"""

        for attempt in range(max_retries):
            try:
                # Get new proxy if needed
                if not self.current_proxy or self.proxy_failures >= 2:
                    self.current_proxy = self.get_working_proxy()
                    self.proxy_failures = 0

                    if not self.current_proxy:
                        print(f"   ⚠️  No working proxy found, trying direct connection...")
                        # Try without proxy as fallback
                        response = requests.get(
                            url,
                            timeout=15,
                            headers=self.get_random_headers()
                        )
                        if response.status_code == 200:
                            return response.text
                        continue

                # Make request with proxy
                proxies = {'http': self.current_proxy, 'https': self.current_proxy}
                response = requests.get(
                    url,
                    proxies=proxies,
                    timeout=15,
                    headers=self.get_random_headers()
                )

                if response.status_code == 200:
                    self.proxy_failures = 0
                    return response.text
                else:
                    print(f"   ⚠️  Status {response.status_code}, retrying...")
                    self.proxy_failures += 1

            except Exception as e:
                print(f"   ⚠️  Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                self.proxy_failures += 1
                time.sleep(2)

        return None

    def extract_transcript_from_html(self, video_id: str) -> Optional[Dict]:
        """Extract transcript by scraping YouTube page HTML"""

        print(f"\n🌐 Scraping transcript for {video_id}...")
        url = f"https://www.youtube.com/watch?v={video_id}"

        html = self.fetch_with_proxy(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'lxml')

        # Try to find transcript data in page scripts
        # YouTube embeds transcript in JSON within script tags
        scripts = soup.find_all('script')

        for script in scripts:
            if script.string and 'captionTracks' in script.string:
                try:
                    # Extract JSON containing caption tracks
                    json_str = re.search(r'"captions":({.*?}),', script.string)
                    if json_str:
                        captions_data = json.loads(json_str.group(1))

                        # Get first available caption track URL
                        if 'playerCaptionsTracklistRenderer' in captions_data:
                            tracks = captions_data['playerCaptionsTracklistRenderer'].get('captionTracks', [])
                            if tracks:
                                caption_url = tracks[0].get('baseUrl')
                                if caption_url:
                                    return self.fetch_transcript_from_url(video_id, caption_url)

                except Exception as e:
                    print(f"   ⚠️  JSON parsing error: {e}")
                    continue

        print(f"   ❌ Could not find transcript in page HTML")
        return None

    def fetch_transcript_from_url(self, video_id: str, caption_url: str) -> Optional[Dict]:
        """Fetch and parse transcript from caption URL"""

        print(f"   📥 Fetching transcript XML...")
        xml_content = self.fetch_with_proxy(caption_url)

        if not xml_content:
            return None

        # Parse XML transcript
        soup = BeautifulSoup(xml_content, 'xml')
        texts = soup.find_all('text')

        segments = []
        for text in texts:
            segments.append({
                'text': text.get_text().strip(),
                'start': float(text.get('start', 0)),
                'duration': float(text.get('dur', 0))
            })

        print(f"   ✅ Extracted {len(segments)} segments")

        return {
            'video_id': video_id,
            'transcript': {
                'segments': segments,
                'segment_count': len(segments)
            },
            'method': 'proxy_scraper',
            'status': 'success'
        }

    def extract_comments(self, video_id: str, max_comments: int = 100) -> List[Dict]:
        """Extract comments by scraping YouTube page"""

        print(f"\n💬 Scraping comments for {video_id}...")
        url = f"https://www.youtube.com/watch?v={video_id}"

        html = self.fetch_with_proxy(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        comments = []

        # Find comment data in page scripts
        scripts = soup.find_all('script')

        for script in scripts:
            if script.string and 'commentThreadRenderer' in script.string:
                try:
                    # Extract comment threads from JSON
                    comment_matches = re.findall(
                        r'"commentThreadRenderer":\s*({.*?})\s*(?:,|\})',
                        script.string
                    )

                    for match in comment_matches[:max_comments]:
                        try:
                            comment_data = json.loads(match)
                            comment_content = comment_data.get('comment', {}).get('commentRenderer', {})

                            if comment_content:
                                text_runs = comment_content.get('contentText', {}).get('runs', [])
                                comment_text = ''.join([run.get('text', '') for run in text_runs])

                                comments.append({
                                    'author': comment_content.get('authorText', {}).get('simpleText', ''),
                                    'text': comment_text,
                                    'likes': int(comment_content.get('voteCount', {}).get('simpleText', '0').replace(',', ''))
                                })
                        except:
                            continue

                except Exception as e:
                    print(f"   ⚠️  Comment parsing error: {e}")
                    continue

        print(f"   ✅ Extracted {len(comments)} comments")
        return comments

    def extract_full_data(self, video_id: str) -> Dict:
        """Extract both transcript and comments"""

        print(f"\n{'='*70}")
        print(f"🎯 PROXY SCRAPER: {video_id}")
        print(f"{'='*70}")

        # Get transcript
        transcript_data = self.extract_transcript_from_html(video_id)
        if not transcript_data:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': 'Could not extract transcript'
            }

        # Get comments
        comments = self.extract_comments(video_id)

        transcript_data['comments'] = comments
        transcript_data['comments_extracted'] = len(comments)

        return transcript_data


def test_proxy_scraper(video_id: str = '3q1QvEkbbyk'):
    """Test the proxy scraper"""
    print(f"\n{'='*70}")
    print(f"🧪 TESTING PROXY SCRAPER")
    print(f"{'='*70}\n")

    scraper = ProxyScraper()
    result = scraper.extract_full_data(video_id)

    print(f"\n{'='*70}")
    print(f"📋 RESULT:")
    print(f"{'='*70}")
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"Segments: {result.get('transcript', {}).get('segment_count', 0)}")
        print(f"Comments: {result.get('comments_extracted', 0)}")
    else:
        print(f"Error: {result.get('error')}")
    print(f"{'='*70}\n")

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python soup_proxy_scraper.py VIDEO_ID")
        print("\nTesting with sample video...")
        test_proxy_scraper()
    else:
        video_id = sys.argv[1]

        scraper = ProxyScraper()
        result = scraper.extract_full_data(video_id)

        if result.get('status') == 'success':
            # Save result
            output_file = f"/Users/yourox/AI-Workspace/data/transcripts/{video_id}_full.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Saved to: {output_file}")
            print(f"✅ SUCCESS!")
        else:
            print(f"\n❌ FAILED: {result.get('error')}")
