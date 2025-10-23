#!/usr/bin/env python3
"""
Local transcript extractor using youtube-transcript-api
Run this on your local machine with ProtonVPN connected
"""

import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
except ImportError:
    print("❌ Please install: pip3 install youtube-transcript-api")
    sys.exit(1)


class LocalVPNExtractor:
    """Extract transcripts using local machine + VPN"""

    def __init__(self):
        self.output_dir = Path("/Users/yourox/AI-Workspace/data/transcripts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_transcript(self, video_id: str) -> dict:
        """Extract transcript using youtube-transcript-api (routes through your VPN)"""
        try:
            # This will use your system's network connection (ProtonVPN if connected)
            api = YouTubeTranscriptApi()
            transcript = api.get_transcript(video_id)

            segments = []
            for item in transcript:
                segments.append({
                    'text': item['text'],
                    'start': int(item['start']),
                    'duration': int(item['duration'])
                })

            return {
                'video_id': video_id,
                'transcript': {
                    'segments': segments,
                    'segment_count': len(segments)
                },
                'method': 'youtube_transcript_api_vpn',
                'status': 'success'
            }

        except TranscriptsDisabled:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': 'Transcripts disabled by uploader'
            }
        except NoTranscriptFound:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': 'No transcript available'
            }
        except VideoUnavailable:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': 'Video unavailable'
            }
        except Exception as e:
            return {
                'video_id': video_id,
                'status': 'error',
                'error': str(e)
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
    """Main function"""

    # Check network connection
    print("\n" + "="*70)
    print("🌐 LOCAL VPN EXTRACTOR")
    print("="*70)
    print("\n⚠️  IMPORTANT: Make sure ProtonVPN is CONNECTED before continuing!")
    print("   This script will use your local network connection.\n")

    response = input("Is ProtonVPN connected? (y/n): ").lower().strip()
    if response != 'y':
        print("\n❌ Please connect to ProtonVPN first, then run this script again.")
        sys.exit(0)

    # Get failed videos
    failed_file = Path("/tmp/tier2_3_failed.txt")
    if not failed_file.exists():
        print(f"\n❌ Failed videos file not found: {failed_file}")
        sys.exit(1)

    with open(failed_file) as f:
        video_ids = [line.strip() for line in f if line.strip()]

    print(f"\n📋 Found {len(video_ids)} failed videos to retry")

    # Ask for workers
    try:
        workers = int(input("\nHow many parallel workers? (recommended: 5-10): "))
    except:
        workers = 5

    print(f"\n🚀 Starting extraction with {workers} workers...")
    print("="*70 + "\n")

    extractor = LocalVPNExtractor()
    success = 0
    failed = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(extractor.process_video, vid, i, len(video_ids)): vid
            for i, vid in enumerate(video_ids, 1)
        }

        for future in as_completed(futures):
            if future.result():
                success += 1
            else:
                failed += 1

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
