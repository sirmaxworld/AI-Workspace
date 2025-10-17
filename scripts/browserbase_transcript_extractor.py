#!/usr/bin/env python3
"""
YouTube Transcript Extractor using Browserbase
Bypasses IP blocks using real browser automation
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from browserbase import Browserbase
from playwright.sync_api import sync_playwright

load_dotenv('/Users/yourox/AI-Workspace/.env')


def extract_youtube_transcript(video_id: str) -> dict:
    """
    Extract YouTube transcript using Browserbase browser automation

    Args:
        video_id: YouTube video ID

    Returns:
        dict with transcript data
    """

    api_key = os.getenv('BROWSERBASE_API_KEY')
    project_id = os.getenv('BROWSERBASE_PROJECT_ID')

    if not api_key or not project_id:
        raise ValueError("Browserbase credentials not found in .env")

    print(f"🌐 Starting Browserbase session...")
    print(f"📹 Video ID: {video_id}")

    # Initialize Browserbase
    bb = Browserbase(api_key=api_key)

    # Create a session with extended timeout (10 minutes for long videos)
    session = bb.sessions.create(
        project_id=project_id,
        timeout=600  # 10 minutes in seconds
    )
    session_id = session.id

    print(f"✅ Session created: {session_id} (timeout: 10min)")

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        with sync_playwright() as playwright:
            # Connect to Browserbase session
            browser = playwright.chromium.connect_over_cdp(
                f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={session_id}"
            )

            context = browser.contexts[0]
            page = context.pages[0]

            print(f"🔗 Navigating to: {video_url}")
            page.goto(video_url, wait_until="domcontentloaded", timeout=30000)

            # Wait for page to load
            time.sleep(3)

            print(f"📄 Looking for transcript button...")

            # Try to click "Show transcript" button
            try:
                # Look for the transcript button (multiple selectors as YouTube layout changes)
                selectors = [
                    'button[aria-label*="transcript" i]',
                    'button[aria-label*="Show transcript" i]',
                    'ytd-engagement-panel-title-header-renderer button',
                    '#primary-button button'
                ]

                clicked = False
                for selector in selectors:
                    try:
                        button = page.wait_for_selector(selector, timeout=5000)
                        if button and 'transcript' in button.get_attribute('aria-label').lower():
                            button.click()
                            clicked = True
                            print(f"✅ Clicked transcript button")
                            break
                    except:
                        continue

                if not clicked:
                    # Try alternative: look for "...more" button first
                    try:
                        more_button = page.wait_for_selector('#expand', timeout=3000)
                        if more_button:
                            more_button.click()
                            time.sleep(1)
                    except:
                        pass

                    # Then try Show transcript
                    try:
                        transcript_button = page.locator('text=/show transcript/i').first
                        transcript_button.click()
                        clicked = True
                        print(f"✅ Clicked transcript button (alt method)")
                    except:
                        pass

                if clicked:
                    time.sleep(2)

                    # Extract transcript segments
                    print(f"📝 Extracting transcript segments...")

                    # Transcript segments are in ytd-transcript-segment-renderer
                    segments = page.locator('ytd-transcript-segment-renderer').all()

                    transcript_data = []
                    for segment in segments:
                        try:
                            # Get timestamp
                            timestamp_elem = segment.locator('.segment-timestamp').first
                            timestamp_text = timestamp_elem.inner_text() if timestamp_elem else "0:00"

                            # Get text
                            text_elem = segment.locator('.segment-text').first
                            text = text_elem.inner_text() if text_elem else ""

                            # Convert timestamp to seconds
                            time_parts = timestamp_text.split(':')
                            if len(time_parts) == 2:
                                start_seconds = int(time_parts[0]) * 60 + int(time_parts[1])
                            else:
                                start_seconds = 0

                            transcript_data.append({
                                'text': text.strip(),
                                'start': start_seconds,
                                'duration': 0  # Duration not available
                            })
                        except:
                            continue

                    if transcript_data:
                        print(f"✅ Extracted {len(transcript_data)} segments")

                        # Get video title
                        try:
                            title_elem = page.locator('h1.ytd-watch-metadata yt-formatted-string').first
                            title = title_elem.inner_text() if title_elem else "Unknown Title"
                        except:
                            title = "Unknown Title"

                        # Get channel name
                        try:
                            channel_elem = page.locator('ytd-channel-name a').first
                            channel = channel_elem.inner_text() if channel_elem else "Unknown Channel"
                        except:
                            channel = "Unknown Channel"

                        # Extract video metadata
                        try:
                            view_count_elem = page.locator('span.view-count').first
                            views = view_count_elem.inner_text() if view_count_elem else "0"
                        except:
                            views = "0"

                        # Scroll to load comments (optimized for speed)
                        print(f"💬 Loading comments...")
                        comments = []
                        try:
                            # Check if page is still alive before comment extraction
                            if page.is_closed():
                                print(f"⚠️  Page closed before comment extraction")
                                comments = []
                            else:
                                # Initial scroll to comments section
                                page.evaluate("window.scrollTo(0, 800)")
                                time.sleep(1)

                                # Try to load more comments by scrolling to bottom of comment section
                                # and clicking "Show more" buttons (reduced to 3 attempts for speed)
                                for attempt in range(3):
                                    try:
                                        # Check page still alive before each scroll
                                        if page.is_closed():
                                            print(f"  ⚠️  Page closed during scroll attempt {attempt + 1}")
                                            break

                                        # Scroll to bottom of loaded comments
                                        page.evaluate("""
                                            const comments = document.querySelector('ytd-comments#comments');
                                            if (comments) {
                                                comments.scrollIntoView({block: 'end', behavior: 'smooth'});
                                            }
                                        """)
                                        time.sleep(1)

                                        # Try to click continuation button (Show more comments)
                                        try:
                                            continuation_button = page.locator('ytd-continuation-item-renderer button').first
                                            if continuation_button.is_visible(timeout=1000):
                                                continuation_button.click()
                                                print(f"  🔄 Clicked 'Show more' (attempt {attempt + 1})")
                                                time.sleep(1)
                                        except:
                                            pass  # Button might not exist or not be visible
                                    except Exception as scroll_error:
                                        print(f"  ⚠️  Scroll attempt {attempt + 1} failed: {scroll_error}")
                                        break

                                print(f"  📜 Attempted to load more comments...")

                                # Extract top comments (limit to 100)
                                if not page.is_closed():
                                    all_comments = page.locator('ytd-comment-thread-renderer').all()
                                    print(f"  💬 Found {len(all_comments)} comment elements")
                                    comment_elements = all_comments[:100]

                                    for comment_elem in comment_elements:
                                        try:
                                            author_elem = comment_elem.locator('#author-text').first
                                            author = author_elem.inner_text() if author_elem else ""

                                            text_elem = comment_elem.locator('#content-text').first
                                            text = text_elem.inner_text() if text_elem else ""

                                            likes_elem = comment_elem.locator('#vote-count-middle').first
                                            likes_text = likes_elem.inner_text() if likes_elem else "0"
                                            likes = int(likes_text.replace('K', '000').replace('M', '000000')) if likes_text and likes_text != "0" else 0

                                            if text:
                                                comments.append({
                                                    'author': author.strip(),
                                                    'text': text.strip(),
                                                    'likes': likes
                                                })
                                        except:
                                            continue

                                    print(f"✅ Extracted {len(comments)} comments")
                                else:
                                    print(f"⚠️  Page closed before comment extraction")
                        except Exception as e:
                            print(f"⚠️  Could not extract comments: {e}")
                            comments = []

                        result = {
                            'video_id': video_id,
                            'title': title,
                            'channel': channel,
                            'views': views,
                            'transcript': {
                                'segments': transcript_data,
                                'segment_count': len(transcript_data)
                            },
                            'comments': {
                                'top_comments': comments,
                                'count': len(comments)
                            },
                            'method': 'browserbase',
                            'status': 'success'
                        }

                        return result
                    else:
                        print(f"⚠️  No transcript segments found")
                        return {
                            'video_id': video_id,
                            'error': 'No transcript segments extracted',
                            'status': 'error'
                        }
                else:
                    print(f"⚠️  Could not find transcript button")
                    return {
                        'video_id': video_id,
                        'error': 'Transcript button not found',
                        'status': 'error'
                    }

            except Exception as e:
                print(f"❌ Error extracting transcript: {e}")
                return {
                    'video_id': video_id,
                    'error': str(e),
                    'status': 'error'
                }

    finally:
        # Clean up session
        try:
            bb.sessions.delete(session_id)
            print(f"🧹 Session closed")
        except:
            pass

    return {
        'video_id': video_id,
        'error': 'Unknown error',
        'status': 'error'
    }


def save_transcript(video_id: str, data: dict, output_dir: str = "/Users/yourox/AI-Workspace/data/transcripts"):
    """Save transcript to JSON file"""
    output_path = Path(output_dir) / f"{video_id}_full.json"

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"💾 Saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python browserbase_transcript_extractor.py VIDEO_ID")
        sys.exit(1)

    video_id = sys.argv[1]

    print(f"\n{'='*70}")
    print(f"🚀 BROWSERBASE TRANSCRIPT EXTRACTOR")
    print(f"{'='*70}\n")

    result = extract_youtube_transcript(video_id)

    if result.get('status') == 'success':
        save_transcript(video_id, result)
        print(f"\n✅ SUCCESS!")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")
        print(f"\nResult: {json.dumps(result, indent=2)}")
