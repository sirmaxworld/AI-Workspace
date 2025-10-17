#!/usr/bin/env python3
"""
Enhanced YouTube Channel Extractor
- Fetches latest videos from a channel
- Filters out YouTube Shorts automatically
- Integrates with CrewAI pipeline
- Quality validation
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

import yt_dlp
from urllib.parse import urlparse, parse_qs

load_dotenv('/Users/yourox/AI-Workspace/.env')


class YouTubeChannelExtractor:
    """Extract videos from YouTube channels with Shorts filtering"""

    def __init__(
        self,
        cache_dir: str = "/Users/yourox/AI-Workspace/data/youtube_channels"
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # YouTube Shorts are typically < 60 seconds
        self.shorts_max_duration = 60

    def extract_channel_handle(self, url: str) -> Optional[str]:
        """Extract channel handle/ID from various YouTube URL formats"""

        # Handle @username format
        if '@' in url:
            parts = url.split('@')
            if len(parts) > 1:
                handle = parts[1].split('/')[0].split('?')[0]
                return f"@{handle}"

        # Handle /c/ or /channel/ format
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc:
            path_parts = parsed.path.split('/')
            for i, part in enumerate(path_parts):
                if part in ['c', 'channel', 'user']:
                    if i + 1 < len(path_parts):
                        return path_parts[i + 1]

        # If it's already a clean handle/ID
        if url.startswith('@') or url.startswith('UC'):
            return url

        return None

    def get_channel_videos(
        self,
        channel_url: str,
        max_videos: int = 50,
        filter_shorts: bool = True,
        days_back: Optional[int] = None
    ) -> List[Dict]:
        """
        Fetch videos from a YouTube channel

        Args:
            channel_url: Channel URL or handle (e.g., @GregIsenberg or full URL)
            max_videos: Maximum number of videos to fetch
            filter_shorts: If True, exclude videos < 60 seconds
            days_back: Only fetch videos from last N days (None = all videos)

        Returns:
            List of video metadata dicts
        """

        print(f"\n{'='*60}")
        print(f"Extracting videos from: {channel_url}")
        print(f"{'='*60}")

        # Extract clean channel identifier
        channel_handle = self.extract_channel_handle(channel_url)
        if not channel_handle:
            channel_handle = channel_url

        # Build YouTube channel URL
        if not channel_url.startswith('http'):
            if channel_url.startswith('@'):
                full_url = f"https://www.youtube.com/{channel_url}/videos"
            else:
                full_url = f"https://www.youtube.com/c/{channel_url}/videos"
        else:
            full_url = channel_url if '/videos' in channel_url else f"{channel_url}/videos"

        print(f"Fetching from: {full_url}")

        # yt-dlp options for channel extraction
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download, just get metadata
            'playlistend': max_videos * 2,  # Fetch extra to account for filtering
            'ignoreerrors': True,
        }

        videos = []

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Fetching channel metadata...")
                info = ydl.extract_info(full_url, download=False)

                if not info:
                    raise ValueError("Could not extract channel information")

                channel_name = info.get('channel', info.get('uploader', 'Unknown'))
                entries = info.get('entries', [])

                print(f"Channel: {channel_name}")
                print(f"Found {len(entries)} videos")
                print(f"\nProcessing videos...")

                # Calculate cutoff date if specified
                cutoff_date = None
                if days_back:
                    cutoff_date = datetime.now() - timedelta(days=days_back)

                for idx, entry in enumerate(entries):
                    if not entry:
                        continue

                    # Get detailed video info
                    video_id = entry.get('id')
                    if not video_id:
                        continue

                    video_url = f"https://www.youtube.com/watch?v={video_id}"

                    # Fetch full metadata to get duration
                    try:
                        video_info = self._get_video_metadata(video_id)
                    except Exception as e:
                        print(f"  ⚠️  Skipping {video_id}: {e}")
                        continue

                    duration = video_info.get('duration', 0)
                    title = video_info.get('title', entry.get('title', 'Unknown'))
                    upload_date_str = video_info.get('upload_date', '')

                    # Filter: Check if it's a Short
                    is_short = duration > 0 and duration <= self.shorts_max_duration
                    if filter_shorts and is_short:
                        print(f"  ⏭️  Skipping Short: {title} ({duration}s)")
                        continue

                    # Filter: Check date if specified
                    if cutoff_date and upload_date_str:
                        try:
                            upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
                            if upload_date < cutoff_date:
                                print(f"  ⏭️  Skipping old video: {title}")
                                continue
                        except:
                            pass

                    # Valid video - add to list
                    video_data = {
                        'id': video_id,
                        'url': video_url,
                        'title': title,
                        'channel': channel_name,
                        'duration': duration,
                        'duration_formatted': self._format_duration(duration),
                        'upload_date': upload_date_str,
                        'view_count': video_info.get('view_count', 0),
                        'like_count': video_info.get('like_count', 0),
                        'description': (video_info.get('description', '') or '')[:500],
                        'tags': video_info.get('tags', [])[:10],
                        'thumbnail': video_info.get('thumbnail', ''),
                        'is_short': is_short,
                    }

                    videos.append(video_data)

                    print(f"  ✓ [{len(videos)}/{max_videos}] {title} ({video_data['duration_formatted']})")

                    # Stop if we've reached max_videos
                    if len(videos) >= max_videos:
                        break

                    # Rate limiting
                    time.sleep(0.5)

        except Exception as e:
            print(f"Error extracting channel: {e}")
            raise

        print(f"\n{'='*60}")
        print(f"✅ Extracted {len(videos)} videos")
        print(f"{'='*60}\n")

        return videos

    def _get_video_metadata(self, video_id: str) -> Dict:
        """Get detailed metadata for a single video"""

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False
            )
            return info

    def _format_duration(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS or MM:SS format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    def save_videos(self, videos: List[Dict], output_file: str) -> str:
        """Save extracted videos to JSON file"""

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata
        data = {
            'extracted_at': datetime.now().isoformat(),
            'total_videos': len(videos),
            'channel': videos[0]['channel'] if videos else 'Unknown',
            'videos': videos
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved to: {output_path}")
        return str(output_path)

    def get_cached_videos(self, channel_handle: str) -> Optional[List[Dict]]:
        """Check if we have cached videos for this channel"""

        cache_file = self.cache_dir / f"{channel_handle.replace('@', '')}_videos.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Check if cache is recent (< 24 hours)
                extracted_at = datetime.fromisoformat(data['extracted_at'])
                age = datetime.now() - extracted_at

                if age.days < 1:
                    print(f"✓ Using cached videos (age: {age.seconds // 3600}h)")
                    return data['videos']
            except:
                pass

        return None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Extract YouTube channel videos')
    parser.add_argument('channel', help='Channel URL or handle (e.g., @GregIsenberg)')
    parser.add_argument('--max-videos', type=int, default=50, help='Maximum videos to extract')
    parser.add_argument('--include-shorts', action='store_true', help='Include YouTube Shorts')
    parser.add_argument('--days-back', type=int, help='Only fetch videos from last N days')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--use-cache', action='store_true', help='Use cached results if available')

    args = parser.parse_args()

    extractor = YouTubeChannelExtractor()

    # Check cache if requested
    if args.use_cache:
        channel_handle = extractor.extract_channel_handle(args.channel) or args.channel
        cached = extractor.get_cached_videos(channel_handle)
        if cached:
            videos = cached
        else:
            videos = extractor.get_channel_videos(
                args.channel,
                max_videos=args.max_videos,
                filter_shorts=not args.include_shorts,
                days_back=args.days_back
            )
    else:
        videos = extractor.get_channel_videos(
            args.channel,
            max_videos=args.max_videos,
            filter_shorts=not args.include_shorts,
            days_back=args.days_back
        )

    # Save to file
    if args.output:
        output_file = args.output
    else:
        channel_handle = extractor.extract_channel_handle(args.channel) or 'channel'
        channel_handle = channel_handle.replace('@', '')
        output_file = f"/Users/yourox/AI-Workspace/data/youtube_channels/{channel_handle}_videos.json"

    extractor.save_videos(videos, output_file)

    # Print summary
    print(f"\n📊 Summary:")
    print(f"  Total videos: {len(videos)}")
    if videos:
        total_duration = sum(v['duration'] for v in videos)
        print(f"  Total duration: {total_duration // 3600}h {(total_duration % 3600) // 60}m")
        print(f"  Average duration: {total_duration // len(videos) // 60}m")
        print(f"  Date range: {videos[-1]['upload_date']} to {videos[0]['upload_date']}")


if __name__ == "__main__":
    main()
