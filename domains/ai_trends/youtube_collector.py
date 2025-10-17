#!/usr/bin/env python3
"""
YouTube Collector for Domain Knowledge Bases
Collects videos and transcripts from configured channels
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from googleapiclient.discovery import build
except ImportError:
    print("⚠️  Missing dependencies. Installing...")
    os.system("pip install youtube-transcript-api google-api-python-client")
    from youtube_transcript_api import YouTubeTranscriptApi
    from googleapiclient.discovery import build

# Load environment
load_dotenv(project_root / '.env')


class DomainYouTubeCollector:
    """Collects YouTube content for a specific domain"""
    
    def __init__(self, domain_path: Path):
        self.domain_path = Path(domain_path)
        self.config = self._load_config()
        self.youtube_api = self._init_youtube_api()
        
        # Directories
        self.youtube_dir = self.domain_path / 'youtube'
        self.transcripts_dir = self.youtube_dir / 'transcripts'
        self.metadata_file = self.youtube_dir / 'videos.json'
        
        # Ensure directories exist
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📺 YouTube Collector for: {self.config['display_name']}")
        print(f"   Channels: {len(self.config['youtube']['channels'])}")
    
    def _load_config(self) -> Dict:
        """Load domain configuration"""
        config_file = self.domain_path / 'config.json'
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def _init_youtube_api(self):
        """Initialize YouTube Data API"""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            print("⚠️  YOUTUBE_API_KEY not found in .env")
            print("   Get one at: https://console.cloud.google.com/")
            return None
        
        return build('youtube', 'v3', developerKey=api_key)
    
    def get_channel_id(self, handle: str) -> Optional[str]:
        """Convert @handle to channel ID"""
        if not self.youtube_api:
            return None
        
        try:
            # Remove @ if present
            handle = handle.replace('@', '')
            
            request = self.youtube_api.search().list(
                part='snippet',
                q=handle,
                type='channel',
                maxResults=1
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]['snippet']['channelId']
        except Exception as e:
            print(f"✗ Error getting channel ID for {handle}: {e}")
        
        return None
    
    def get_recent_videos(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """Get recent videos from a channel"""
        if not self.youtube_api:
            return []
        
        videos = []
        days_back = self.config['youtube'].get('days_back', 30)
        published_after = (datetime.now() - timedelta(days=days_back)).isoformat() + 'Z'
        
        try:
            request = self.youtube_api.search().list(
                part='snippet',
                channelId=channel_id,
                type='video',
                order='date',
                publishedAfter=published_after,
                maxResults=min(max_results, 50)
            )
            response = request.execute()
            
            for item in response['items']:
                video_data = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': channel_id,
                    'channel_title': item['snippet']['channelTitle']
                }
                videos.append(video_data)
        
        except Exception as e:
            print(f"✗ Error getting videos: {e}")
        
        return videos
    
    def download_transcript(self, video_id: str) -> Optional[str]:
        """Download transcript for a video"""
        transcript_file = self.transcripts_dir / f"{video_id}.txt"
        
        # Skip if already exists
        if transcript_file.exists():
            return transcript_file.read_text()
        
        try:
            # Try to get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([item['text'] for item in transcript_list])
            
            # Save transcript
            transcript_file.write_text(transcript_text)
            print(f"  ✓ Transcript: {video_id}")
            return transcript_text
            
        except Exception as e:
            print(f"  ✗ No transcript: {video_id} ({str(e)[:50]})")
            return None
    
    def collect_all(self) -> Dict:
        """Collect videos from all configured channels"""
        print(f"\n{'='*60}")
        print(f"Starting collection for: {self.config['display_name']}")
        print(f"{'='*60}\n")
        
        all_videos = []
        stats = {
            'channels_processed': 0,
            'videos_found': 0,
            'transcripts_downloaded': 0,
            'transcripts_failed': 0
        }
        
        for channel_config in self.config['youtube']['channels']:
            channel_handle = channel_config['id']
            channel_name = channel_config['name']
            
            print(f"📺 Processing: {channel_name}")
            
            # Get channel ID
            channel_id = self.get_channel_id(channel_handle)
            if not channel_id:
                print(f"  ✗ Could not find channel")
                continue
            
            # Get recent videos
            max_videos = self.config['youtube'].get('max_videos_per_channel', 50)
            videos = self.get_recent_videos(channel_id, max_videos)
            print(f"  Found {len(videos)} videos")
            
            # Download transcripts
            for video in videos:
                transcript = self.download_transcript(video['video_id'])
                video['has_transcript'] = transcript is not None
                
                if transcript:
                    stats['transcripts_downloaded'] += 1
                else:
                    stats['transcripts_failed'] += 1
                
                all_videos.append(video)
            
            stats['channels_processed'] += 1
            stats['videos_found'] += len(videos)
            print()
        
        # Save metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(all_videos, f, indent=2)
        
        # Print summary
        print(f"{'='*60}")
        print(f"✅ Collection Complete!")
        print(f"{'='*60}")
        print(f"Channels processed: {stats['channels_processed']}")
        print(f"Videos found: {stats['videos_found']}")
        print(f"Transcripts downloaded: {stats['transcripts_downloaded']}")
        print(f"Transcripts failed: {stats['transcripts_failed']}")
        print(f"\n📁 Saved to: {self.metadata_file}")
        print(f"{'='*60}\n")
        
        return stats


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python youtube_collector.py <domain_path>")
        print("Example: python youtube_collector.py /Users/yourox/AI-Workspace/domains/ai_trends")
        sys.exit(1)
    
    domain_path = Path(sys.argv[1])
    
    if not domain_path.exists():
        print(f"✗ Domain path does not exist: {domain_path}")
        sys.exit(1)
    
    collector = DomainYouTubeCollector(domain_path)
    collector.collect_all()


if __name__ == '__main__':
    main()
