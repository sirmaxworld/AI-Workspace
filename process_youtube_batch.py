#!/usr/bin/env python3
"""
Improved YouTube Batch Processing Script
Fixes cache handling issues and processes videos efficiently
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import the components we need
from youtube_channel_extractor import YouTubeChannelExtractor
from youtube_transcriber_pro import YouTubeTranscriberPro

load_dotenv('/Users/yourox/AI-Workspace/.env')

BASE_PATH = Path('/Users/yourox/AI-Workspace')
DATA_PATH = BASE_PATH / 'data'
TRANSCRIPTS_PATH = DATA_PATH / 'transcripts'
REPORTS_PATH = DATA_PATH / 'batch_reports'
REPORTS_PATH.mkdir(parents=True, exist_ok=True)


class YouTubeBatchProcessor:
    """Fixed batch processor for YouTube videos"""

    def __init__(self, user_id: str = "yourox_youtube_batch"):
        self.extractor = YouTubeChannelExtractor()
        self.transcriber = YouTubeTranscriberPro(
            user_id=user_id,
            cache_dir=str(TRANSCRIPTS_PATH)
        )
        self.processed_videos = self._load_processed_videos()

    def _load_processed_videos(self) -> set:
        """Load list of already processed video IDs"""
        processed = set()

        # Check for existing transcript files
        if TRANSCRIPTS_PATH.exists():
            # Look for both .json and _full.json files
            for pattern in ['*.json', '*_full.json']:
                for file_path in TRANSCRIPTS_PATH.glob(pattern):
                    # Extract video ID from filename
                    filename = file_path.stem
                    if filename.endswith('_full'):
                        video_id = filename[:-5]  # Remove _full
                    elif not filename.endswith(('_audio', '_insights')):
                        video_id = filename
                    else:
                        continue

                    # Validate it looks like a YouTube video ID
                    if len(video_id) == 11 and video_id.replace('-', '').replace('_', '').isalnum():
                        processed.add(video_id)

        return processed

    def _fix_cache_path(self, video_id: str) -> bool:
        """Fix cache file naming issue - rename _full.json to .json if needed"""
        full_path = TRANSCRIPTS_PATH / f"{video_id}_full.json"
        cache_path = TRANSCRIPTS_PATH / f"{video_id}.json"

        if full_path.exists() and not cache_path.exists():
            try:
                # Copy the file with correct naming
                import shutil
                shutil.copy2(full_path, cache_path)
                print(f"  ✓ Fixed cache file naming for {video_id}")
                return True
            except Exception as e:
                print(f"  ⚠️ Could not fix cache naming: {e}")
                return False

        return cache_path.exists()

    async def process_batch(
        self,
        channel_url: str,
        max_videos: int = 5,
        skip_existing: bool = True,
        filter_shorts: bool = True
    ) -> Dict:
        """
        Process a batch of videos from a channel

        Args:
            channel_url: YouTube channel URL or handle
            max_videos: Maximum videos to process
            skip_existing: Skip videos that have already been processed
            filter_shorts: Exclude YouTube Shorts

        Returns:
            Batch processing report
        """

        print(f"\n{'='*80}")
        print(f"🚀 YOUTUBE BATCH PROCESSING - FIXED VERSION")
        print(f"{'='*80}\n")

        start_time = datetime.now()

        # Step 1: Extract channel videos
        print(f"📺 Extracting videos from channel...")
        all_videos = self.extractor.get_channel_videos(
            channel_url,
            max_videos=max_videos + 10,  # Get extra in case some are already processed
            filter_shorts=filter_shorts
        )

        if not all_videos:
            return {
                'status': 'error',
                'message': 'No videos found in channel'
            }

        channel_name = all_videos[0]['channel']
        print(f"  Found {len(all_videos)} videos from {channel_name}")

        # Step 2: Filter out already processed videos
        videos_to_process = []
        skipped_videos = []

        for video in all_videos:
            video_id = video['id']

            # Fix cache naming if needed
            self._fix_cache_path(video_id)

            if skip_existing and video_id in self.processed_videos:
                skipped_videos.append(video)
                print(f"  ⏭️  Skipping (already processed): {video['title'][:50]}...")
            else:
                videos_to_process.append(video)
                if len(videos_to_process) >= max_videos:
                    break

        print(f"\n  Will process {len(videos_to_process)} new videos")
        print(f"  Skipped {len(skipped_videos)} already processed videos")

        if not videos_to_process:
            return {
                'status': 'success',
                'message': 'All videos already processed',
                'channel': channel_name,
                'skipped_count': len(skipped_videos)
            }

        # Step 3: Process videos
        print(f"\n📝 Processing {len(videos_to_process)} videos...")
        print(f"{'='*80}\n")

        results = []
        successful = []
        failed = []

        for idx, video in enumerate(videos_to_process):
            print(f"\n[{idx + 1}/{len(videos_to_process)}] Processing: {video['title'][:60]}...")
            print(f"  Video ID: {video['id']}")
            print(f"  Duration: {video['duration_formatted']}")
            print(f"  URL: {video['url']}")

            try:
                # Process the video
                result = await self.transcriber.process_video(video['url'])

                if result['status'] == 'success':
                    successful.append({
                        'video_id': video['id'],
                        'title': video['title'],
                        'method': result.get('method', 'unknown'),
                        'chunks': result.get('chunks', 0),
                        'segments': result.get('transcript_segments', 0)
                    })
                    print(f"  ✅ Success: {result.get('method', 'unknown')} method, {result.get('chunks', 0)} chunks")

                    # Save as both naming conventions for compatibility
                    self._ensure_both_cache_formats(video['id'])
                else:
                    failed.append({
                        'video_id': video['id'],
                        'title': video['title'],
                        'error': result.get('message', 'Unknown error')
                    })
                    print(f"  ❌ Failed: {result.get('message', 'Unknown error')}")

                results.append(result)

            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                failed.append({
                    'video_id': video['id'],
                    'title': video['title'],
                    'error': str(e)
                })
                continue

            # Small delay between videos to be respectful
            if idx < len(videos_to_process) - 1:
                await asyncio.sleep(2)

        # Step 4: Generate report
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        report = {
            'batch_run': {
                'channel': channel_name,
                'channel_url': channel_url,
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat(),
                'duration_seconds': duration,
                'duration_formatted': f"{int(duration // 60)}m {int(duration % 60)}s"
            },
            'summary': {
                'total_found': len(all_videos),
                'already_processed': len(skipped_videos),
                'attempted': len(videos_to_process),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': f"{(len(successful) / len(videos_to_process) * 100):.1f}%" if videos_to_process else "N/A"
            },
            'processing_stats': self.transcriber.stats,
            'successful_videos': successful,
            'failed_videos': failed,
            'skipped_videos': [{'id': v['id'], 'title': v['title']} for v in skipped_videos[:10]]
        }

        # Save report
        report_file = self._save_report(report, channel_name)

        # Print summary
        self._print_summary(report, report_file)

        return report

    def _ensure_both_cache_formats(self, video_id: str):
        """Ensure transcript exists in both naming formats for compatibility"""
        standard_path = TRANSCRIPTS_PATH / f"{video_id}.json"
        full_path = TRANSCRIPTS_PATH / f"{video_id}_full.json"

        # If one exists but not the other, create a copy
        if standard_path.exists() and not full_path.exists():
            import shutil
            shutil.copy2(standard_path, full_path)
        elif full_path.exists() and not standard_path.exists():
            import shutil
            shutil.copy2(full_path, standard_path)

    def _save_report(self, report: Dict, channel_name: str) -> str:
        """Save batch report to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        clean_name = channel_name.replace(' ', '_').replace('@', '')
        filename = f"{clean_name}_batch_{timestamp}.json"
        filepath = REPORTS_PATH / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def _print_summary(self, report: Dict, report_file: str):
        """Print batch processing summary"""
        print(f"\n{'='*80}")
        print(f"📊 BATCH PROCESSING COMPLETE")
        print(f"{'='*80}\n")

        summary = report['summary']
        print(f"📺 Videos:")
        print(f"  Found: {summary['total_found']}")
        print(f"  Already processed: {summary['already_processed']}")
        print(f"  Attempted: {summary['attempted']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Success rate: {summary['success_rate']}\n")

        stats = report['processing_stats']
        print(f"📝 Processing Methods:")
        print(f"  YouTube captions: {stats['youtube_captions_used']}")
        print(f"  Whisper API: {stats['whisper_transcriptions']}")
        print(f"  Total chunks created: {stats['total_chunks']}\n")

        if report['successful_videos']:
            print(f"✅ Successfully Processed:")
            for video in report['successful_videos'][:5]:
                print(f"  • {video['title'][:50]}... ({video['method']}, {video['chunks']} chunks)")

        if report['failed_videos']:
            print(f"\n❌ Failed Videos:")
            for video in report['failed_videos'][:5]:
                print(f"  • {video['title'][:50]}...")
                print(f"    Error: {video['error']}")

        run = report['batch_run']
        print(f"\n⏱️  Duration: {run['duration_formatted']}")
        print(f"💾 Report saved: {report_file}\n")
        print(f"{'='*80}\n")


async def main():
    """Process next 5 videos from Greg Isenberg channel"""
    processor = YouTubeBatchProcessor()

    # Process next 5 videos from Greg Isenberg
    result = await processor.process_batch(
        channel_url="@GregIsenberg",
        max_videos=5,
        skip_existing=True,
        filter_shorts=True
    )

    return result


if __name__ == "__main__":
    result = asyncio.run(main())

    if result.get('status') == 'error':
        print(f"❌ Batch processing failed: {result.get('message')}")
        exit(1)
    else:
        print(f"✅ Batch processing completed successfully!")