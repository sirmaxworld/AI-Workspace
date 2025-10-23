#!/usr/bin/env python3
"""
Non-interactive local Playwright VPN extractor
Automatically processes all failed videos
"""

import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Please install: pip3 install playwright")
    print("   Then run: playwright install chromium")
    exit(1)


class LocalPlaywrightVPNExtractor:
    """Extract transcripts using Playwright on local machine with VPN"""

    def __init__(self):
        self.output_dir = Path("/Users/yourox/AI-Workspace/data/transcripts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_transcript(self, video_id: str) -> dict:
        """Extract transcript using Playwright (routes through VPN)"""

        try:
            with sync_playwright() as p:
                # Launch browser (will use your system's network = ProtonVPN)
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                page = context.new_page()

                # Navigate to video
                url = f"https://www.youtube.com/watch?v={video_id}"
                page.goto(url, wait_until='domcontentloaded', timeout=30000)

                # Wait for page to load
                time.sleep(3)

                # Try to find and click transcript button
                try:
                    # Click "Show more" if present
                    show_more = page.locator('tp-yt-paper-button#expand').first
                    if show_more.is_visible(timeout=2000):
                        show_more.click()
                        time.sleep(1)
                except:
                    pass

                # Find transcript button
                try:
                    # Look for "Show transcript" button
                    transcript_button = page.locator('button:has-text("Show transcript"), button:has-text("Transcript")').first
                    if not transcript_button.is_visible(timeout=5000):
                        browser.close()
                        return {
                            'video_id': video_id,
                            'status': 'error',
                            'error': 'Transcript button not found'
                        }

                    transcript_button.click()
                    time.sleep(2)
                except Exception as e:
                    browser.close()
                    return {
                        'video_id': video_id,
                        'status': 'error',
                        'error': f'Could not click transcript button: {str(e)}'
                    }

                # Extract transcript segments
                try:
                    # Wait for transcript panel to load
                    page.wait_for_selector('ytd-transcript-segment-renderer', timeout=10000)

                    # Get all transcript segments
                    segment_elements = page.locator('ytd-transcript-segment-renderer').all()

                    segments = []
                    for element in segment_elements:
                        try:
                            text = element.locator('.segment-text').inner_text()
                            timestamp = element.locator('.segment-timestamp').inner_text()

                            # Convert timestamp to seconds
                            parts = timestamp.strip().split(':')
                            if len(parts) == 2:  # MM:SS
                                start = int(parts[0]) * 60 + int(parts[1])
                            elif len(parts) == 3:  # HH:MM:SS
                                start = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                            else:
                                start = 0

                            segments.append({
                                'text': text.strip(),
                                'start': start,
                                'duration': 0  # YouTube doesn't provide duration in UI
                            })
                        except:
                            continue

                    browser.close()

                    if not segments:
                        return {
                            'video_id': video_id,
                            'status': 'error',
                            'error': 'No transcript segments found'
                        }

                    return {
                        'video_id': video_id,
                        'transcript': {
                            'segments': segments,
                            'segment_count': len(segments)
                        },
                        'method': 'local_playwright_vpn',
                        'status': 'success'
                    }

                except Exception as e:
                    browser.close()
                    return {
                        'video_id': video_id,
                        'status': 'error',
                        'error': f'Transcript extraction failed: {str(e)}'
                    }

        except Exception as e:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': f'Browser error: {str(e)}'
            }

    def save_transcript(self, video_id: str, data: dict):
        """Save transcript to file"""
        output_file = self.output_dir / f"{video_id}_full.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

    def process_video(self, video_id: str, index: int, total: int) -> bool:
        """Process single video"""
        # Check if already exists
        output_file = self.output_dir / f"{video_id}_full.json"
        if output_file.exists():
            print(f"[{index}/{total}] ⏭️  {video_id}: Already exists")
            return True

        print(f"[{index}/{total}] 🔄 {video_id}: Extracting...")
        result = self.extract_transcript(video_id)

        if result['status'] == 'success':
            self.save_transcript(video_id, result)
            segments = result['transcript']['segment_count']
            print(f"[{index}/{total}] ✅ {video_id}: {segments} segments")
            return True
        else:
            print(f"[{index}/{total}] ❌ {video_id}: {result['error']}")
            return False


def main():
    """Main function - non-interactive"""

    # Configuration
    WORKERS = 3  # Conservative to avoid rate limits

    print("\n" + "="*70)
    print("🌐 LOCAL PLAYWRIGHT VPN EXTRACTOR")
    print("="*70)
    print(f"\n⚠️  Using {WORKERS} workers")
    print("   Routing through ProtonVPN (make sure it's connected!)\n")

    # Get failed videos
    failed_file = Path("/tmp/tier2_3_failed.txt")
    if not failed_file.exists():
        print(f"\n❌ Failed videos file not found: {failed_file}")
        exit(1)

    with open(failed_file) as f:
        video_ids = [line.strip() for line in f if line.strip()]

    print(f"📋 Processing {len(video_ids)} failed videos")
    print("="*70 + "\n")

    extractor = LocalPlaywrightVPNExtractor()
    success = 0
    failed = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(extractor.process_video, vid, i, len(video_ids)): vid
            for i, vid in enumerate(video_ids, 1)
        }

        for future in as_completed(futures):
            if future.result():
                success += 1
            else:
                failed += 1

            # Small delay between videos
            time.sleep(1)

    elapsed = time.time() - start

    print("\n" + "="*70)
    print("✅ COMPLETE")
    print("="*70)
    print(f"Time: {elapsed/60:.1f} minutes")
    print(f"Success: {success}/{len(video_ids)} ({success/len(video_ids)*100:.1f}%)")
    print(f"Failed: {failed}/{len(video_ids)} ({failed/len(video_ids)*100:.1f}%)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
