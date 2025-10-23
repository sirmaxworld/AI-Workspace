#!/usr/bin/env python3
"""
YouTube Content Collector
Collect video transcripts from YouTube channels and search queries
Uses yt-dlp (already available in the system)
"""

import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent))
try:
    from collection_config_00_collection_config import (
        get_source_config, get_storage_path, get_rate_limit,
        QUALITY_FILTERS, FIRST_BATCH_TARGETS, LOGS_DIR
    )
except ImportError:
    # Fallback: load config directly
    exec(open(Path(__file__).parent / "00_collection_config.py").read())
    from typing import Any
    LOGS_DIR = Path("/tmp/intelligence_logs")
    LOGS_DIR.mkdir(exist_ok=True)

    def get_source_config(source_type: str):
        return SOURCES.get(source_type, {})
    def get_storage_path(source_type: str):
        return STORAGE_PATHS.get(source_type)
    def get_rate_limit(source_type: str):
        return RATE_LIMITS.get(source_type, {"delay_between_requests": 5})

class YouTubeCollector:
    """Collect YouTube videos and transcripts"""

    def __init__(self):
        self.storage_path = get_storage_path("youtube")
        self.config = get_source_config("youtube")
        self.rate_limit = get_rate_limit("youtube")
        self.collected_count = 0
        self.failed_count = 0
        self.log_file = LOGS_DIR / "youtube_collection.log"

    def log(self, message: str):
        """Log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")

    def collect_channel_videos(self, channel_config: Dict, max_videos: int = 50) -> List[Dict]:
        """
        Collect videos from a YouTube channel

        Args:
            channel_config: Channel configuration dict
            max_videos: Maximum number of videos to collect

        Returns:
            List of collected video metadata
        """
        channel_name = channel_config['name']
        channel_url = channel_config['url']

        self.log(f"\n{'='*80}")
        self.log(f"Collecting from channel: {channel_name}")
        self.log(f"{'='*80}")

        # Create channel directory
        channel_dir = self.storage_path / channel_name.replace(" ", "_")
        channel_dir.mkdir(parents=True, exist_ok=True)

        # Use yt-dlp to get channel videos
        cmd = [
            "yt-dlp",
            "--skip-download",  # Don't download videos
            "--write-auto-sub",  # Write auto-generated subtitles
            "--sub-lang", "en",  # English subtitles
            "--write-info-json",  # Write metadata
            "--write-description",  # Write description
            "--playlist-end", str(max_videos),  # Limit number
            "--output", str(channel_dir / "%(id)s.%(ext)s"),
            f"https://www.youtube.com/{channel_url}/videos"
        ]

        try:
            self.log(f"Running yt-dlp for {channel_name}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                self.log(f"⚠️  yt-dlp warning/error: {result.stderr[:200]}")

            # Parse collected videos
            videos = []
            for info_file in channel_dir.glob("*.info.json"):
                try:
                    with open(info_file, 'r') as f:
                        info = json.load(f)

                    video_id = info.get('id')
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)

                    # Quality filter: minimum duration
                    if duration < QUALITY_FILTERS['min_video_duration']:
                        self.log(f"   ⏭️  Skipping {title} (too short: {duration}s)")
                        continue

                    # Check for transcript
                    transcript_file = info_file.parent / f"{video_id}.en.vtt"
                    has_transcript = transcript_file.exists()

                    if not has_transcript:
                        self.log(f"   ⚠️  No transcript: {title}")
                        continue

                    # Extract transcript text
                    transcript_text = self._extract_transcript_text(transcript_file)

                    # Quality filter: minimum length
                    if len(transcript_text) < QUALITY_FILTERS['min_transcript_length']:
                        self.log(f"   ⏭️  Skipping {title} (transcript too short)")
                        continue

                    video_data = {
                        "video_id": video_id,
                        "title": title,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "channel": channel_name,
                        "channel_category": channel_config.get('category'),
                        "duration": duration,
                        "upload_date": info.get('upload_date'),
                        "description": info.get('description', ''),
                        "view_count": info.get('view_count', 0),
                        "like_count": info.get('like_count', 0),
                        "transcript": transcript_text,
                        "topics": channel_config.get('topics', []),
                        "collected_at": datetime.now().isoformat(),
                        "source": "youtube",
                        "source_type": "video"
                    }

                    # Save individual video data
                    video_file = channel_dir / f"{video_id}_full.json"
                    with open(video_file, 'w') as f:
                        json.dump(video_data, f, indent=2)

                    videos.append(video_data)
                    self.collected_count += 1
                    self.log(f"   ✅ Collected: {title} ({duration}s, {len(transcript_text)} chars)")

                except Exception as e:
                    self.log(f"   ❌ Error processing {info_file.name}: {e}")
                    self.failed_count += 1
                    continue

            self.log(f"\nCollected {len(videos)} videos from {channel_name}")
            return videos

        except subprocess.TimeoutExpired:
            self.log(f"❌ Timeout collecting from {channel_name}")
            return []
        except Exception as e:
            self.log(f"❌ Error collecting from {channel_name}: {e}")
            return []

    def _extract_transcript_text(self, vtt_file: Path) -> str:
        """Extract plain text from VTT subtitle file"""
        try:
            import re
            import html

            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Decode HTML entities (&gt; → >, &quot; → ", etc.)
            content = html.unescape(content)

            # Split into lines for processing
            lines = content.split('\n')

            text_lines = []
            seen_lines = set()  # Track seen lines to avoid duplicates

            for line in lines:
                line = line.strip()

                # Skip empty lines, headers, metadata, timestamps
                if not line:
                    continue
                if line.startswith('WEBVTT'):
                    continue
                if line.startswith('Kind:') or line.startswith('Language:'):
                    continue
                if '-->' in line:  # Timestamp line
                    continue
                if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3}', line):  # Timestamp
                    continue
                if re.match(r'^align:start position:\d+%$', line):  # Position tag
                    continue

                # Remove timing tags <00:00:00.000> and word-level tags <c>word</c>
                line = re.sub(r'<[\d:.]+>', '', line)  # Remove <00:00:00.000>
                line = re.sub(r'</?c>', '', line)  # Remove <c> and </c>
                line = re.sub(r'</?v[^>]*>', '', line)  # Remove <v> voice tags

                # Clean up the line
                line = line.strip()

                # Skip if empty after cleaning
                if not line:
                    continue

                # Normalize the line (for duplicate detection)
                normalized = line.lower().strip()

                # Skip duplicate consecutive content (VTT repeats lines across time segments)
                if normalized not in seen_lines:
                    text_lines.append(line)
                    seen_lines.add(normalized)

            # Join all text with spaces
            full_text = ' '.join(text_lines)

            # Final cleanup: remove multiple spaces
            full_text = re.sub(r'\s+', ' ', full_text)

            return full_text.strip()

        except Exception as e:
            print(f"   ⚠️  Error extracting transcript: {e}")
            return ""

    def collect_all_priority_channels(self, priority: str = "high") -> List[Dict]:
        """Collect from all channels of a specific priority"""
        channels = [
            c for c in self.config.get('channels', [])
            if c.get('priority') == priority
        ]

        self.log(f"\n{'='*80}")
        self.log(f"Collecting from {len(channels)} {priority} priority channels")
        self.log(f"{'='*80}")

        all_videos = []
        for channel in channels:
            try:
                videos = self.collect_channel_videos(
                    channel,
                    max_videos=self.config.get('max_videos_per_channel', 50)
                )
                all_videos.extend(videos)

                # Rate limiting
                time.sleep(self.rate_limit['delay_between_requests'])

            except Exception as e:
                self.log(f"❌ Error with channel {channel['name']}: {e}")
                continue

        return all_videos

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        return {
            "total_collected": self.collected_count,
            "total_failed": self.failed_count,
            "success_rate": self.collected_count / max(self.collected_count + self.failed_count, 1),
            "storage_path": str(self.storage_path)
        }


def test_youtube_collector():
    """Test YouTube collector on a single channel"""
    print("\n" + "="*80)
    print(" "*25 + "YOUTUBE COLLECTOR TEST")
    print("="*80)

    collector = YouTubeCollector()

    # Test with Y Combinator (usually has good transcripts)
    test_channel = {
        "name": "Y Combinator",
        "url": "@ycombinator",
        "category": "strategy",
        "priority": "high",
        "topics": ["startup strategy", "AI implementation"]
    }

    print(f"\nTesting collection from: {test_channel['name']}")
    print(f"Target: First 5 videos with transcripts")
    print()

    videos = collector.collect_channel_videos(test_channel, max_videos=5)

    # Show results
    stats = collector.get_stats()
    print(f"\n{'='*80}")
    print("COLLECTION RESULTS")
    print(f"{'='*80}")
    print(f"Videos collected: {stats['total_collected']}")
    print(f"Failed: {stats['total_failed']}")
    print(f"Success rate: {stats['success_rate']*100:.1f}%")
    print(f"Storage path: {stats['storage_path']}")

    if videos:
        print(f"\n{'='*80}")
        print("SAMPLE VIDEO")
        print(f"{'='*80}")
        sample = videos[0]
        print(f"Title: {sample['title']}")
        print(f"Duration: {sample['duration']}s")
        print(f"Transcript length: {len(sample['transcript'])} characters")
        print(f"Transcript preview: {sample['transcript'][:200]}...")

    print("\n" + "="*80)
    print("✅ Test complete!")
    print("="*80 + "\n")

    return videos, stats


if __name__ == "__main__":
    # Run test
    videos, stats = test_youtube_collector()

    if stats['total_collected'] > 0:
        print("✅ YouTube collector working!")
        print(f"✅ Collected {stats['total_collected']} videos")
        print("\nNext: Run full collection with:")
        print("  python3 01_youtube_collector.py --full")
    else:
        print("⚠️  No videos collected. Check:")
        print("  - yt-dlp is installed")
        print("  - YouTube channels have transcripts enabled")
        print("  - Internet connection working")
