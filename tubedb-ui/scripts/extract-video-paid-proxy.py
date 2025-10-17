#!/usr/bin/env python3
"""
Extract YouTube video transcript using paid proxy service
Supports authenticated HTTP/HTTPS and SOCKS5 proxies
"""
import sys
import json
import subprocess
import os
import requests
from datetime import datetime
from pathlib import Path

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    import re
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'^([a-zA-Z0-9_-]{11})$'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def test_proxy(proxy_url):
    """Test if proxy is working"""
    print(f"Testing proxy: {proxy_url}")

    # Mask password in output
    display_url = proxy_url
    if '@' in proxy_url:
        parts = proxy_url.split('@')
        if ':' in parts[0]:
            protocol = parts[0].split('//')[0] if '//' in parts[0] else ''
            display_url = f"{protocol}//***:***@{parts[1]}"

    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    try:
        response = requests.get('https://www.google.com', proxies=proxies, timeout=10)
        if response.status_code == 200:
            print(f"✓ Proxy is working")
            return True
        else:
            print(f"✗ Proxy returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Proxy test failed: {e}")
        return False

def download_with_proxy(video_id, output_dir, proxy_url, retries=3):
    """Download transcript using yt-dlp with authenticated proxy"""
    print(f"\nDownloading transcript for {video_id}...")

    # Mask password in output
    display_url = proxy_url
    if '@' in proxy_url:
        parts = proxy_url.split('@')
        if ':' in parts[0]:
            protocol = parts[0].split('//')[0] if '//' in parts[0] else ''
            display_url = f"{protocol}//***:***@{parts[1]}"

    print(f"Using proxy: {display_url}")

    cmd = [
        'yt-dlp',
        '--proxy', proxy_url,
        '--write-auto-sub',
        '--write-sub',
        '--sub-lang', 'en',
        '--sub-format', 'json3',
        '--skip-download',
        '--no-warnings',
        '--extractor-retries', str(retries),
        '--socket-timeout', '30',
        '--output', f'{output_dir}/{video_id}',
        f'https://www.youtube.com/watch?v={video_id}'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=90)
        print(result.stdout)
        return True
    except subprocess.TimeoutExpired:
        print("✗ Download timed out after 90 seconds")
        return False
    except subprocess.CalledProcessError as e:
        print(f"✗ Error downloading: {e.stderr}")
        return False

def get_video_info(video_id, proxy_url=None):
    """Get video metadata using yt-dlp"""
    print(f"\nFetching video info for {video_id}...")

    cmd = [
        'yt-dlp',
        '--dump-json',
        '--skip-download',
        '--no-warnings',
        '--socket-timeout', '30',
        f'https://www.youtube.com/watch?v={video_id}'
    ]

    if proxy_url:
        cmd.insert(1, '--proxy')
        cmd.insert(2, proxy_url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"✗ Error getting video info: {e}")
        return None

def process_transcript(video_id, transcript_dir):
    """Process transcript JSON into TubeDB format"""
    # Try different subtitle file patterns
    patterns = [
        f'{video_id}.en.json3',
        f'{video_id}.en-US.json3',
        f'{video_id}.en-GB.json3',
    ]

    transcript_file = None
    for pattern in patterns:
        test_file = Path(transcript_dir) / pattern
        if test_file.exists():
            transcript_file = test_file
            break

    if not transcript_file:
        print(f"\n✗ Transcript file not found. Tried:")
        for pattern in patterns:
            print(f"  - {transcript_dir}/{pattern}")
        return None

    print(f"✓ Found transcript: {transcript_file.name}")

    with open(transcript_file, 'r') as f:
        data = json.load(f)

    segments = []
    for event in data.get('events', []):
        if 'segs' in event:
            text = ''.join([seg.get('utf8', '') for seg in event['segs']])
            if text.strip():
                segments.append({
                    'text': text.strip(),
                    'start': event.get('tStartMs', 0) / 1000.0,
                    'duration': event.get('dDurationMs', 0) / 1000.0
                })

    return {
        'language': 'en',
        'segments': segments,
        'segment_count': len(segments)
    }

def create_video_entry(video_id, video_info, transcript):
    """Create a video entry in TubeDB format"""
    return {
        'video_id': video_id,
        'title': video_info.get('title', 'Unknown Title'),
        'agent_id': 99,  # Manual extraction
        'method': 'youtube_captions',
        'transcript': transcript,
        'qc_verification': {
            'quality_score': 0.0,  # To be verified
            'key_topics': [],
            'summary': 'Pending analysis',
            'verifier': 'manual_extraction'
        }
    }

def add_to_batch(video_entry, batch_file):
    """Add video entry to batch JSON file"""
    print(f"\nAdding video to {batch_file}...")

    # Load existing batch
    with open(batch_file, 'r') as f:
        videos = json.load(f)

    # Check if video already exists
    if any(v['video_id'] == video_entry['video_id'] for v in videos):
        print(f"ℹ Video {video_entry['video_id']} already exists in batch file")
        return False

    # Add new video
    videos.append(video_entry)

    # Save back to file
    with open(batch_file, 'w') as f:
        json.dump(videos, f, indent=2)

    print(f"✓ Successfully added video! Total videos: {len(videos)}")
    return True

def load_proxy_config():
    """Load proxy configuration from proxy-config.py"""
    try:
        # Try to import proxy config
        sys.path.insert(0, os.path.dirname(__file__))
        import proxy_config
        return {
            'url': proxy_config.PROXY_URL,
            'test': getattr(proxy_config, 'TEST_PROXY', True),
            'timeout': getattr(proxy_config, 'PROXY_TIMEOUT', 30),
            'retries': getattr(proxy_config, 'PROXY_RETRIES', 3)
        }
    except ImportError:
        return None

def main():
    print("=" * 70)
    print("TubeDB Video Extractor - Paid Proxy Edition")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  1. With proxy-config.py file:")
        print("     python3 extract-video-paid-proxy.py <youtube_url>")
        print("\n  2. With command-line proxy:")
        print("     python3 extract-video-paid-proxy.py <youtube_url> <proxy_url>")
        print("\nExample proxy formats:")
        print("  HTTP:   http://user:pass@proxy.com:8080")
        print("  SOCKS5: socks5://user:pass@proxy.com:1080")
        sys.exit(1)

    url = sys.argv[1]

    # Get proxy configuration
    proxy_config = None
    proxy_url = None

    if len(sys.argv) > 2:
        # Proxy provided via command line
        proxy_url = sys.argv[2]
        proxy_config = {
            'url': proxy_url,
            'test': True,
            'timeout': 30,
            'retries': 3
        }
        print("\n✓ Using proxy from command line")
    else:
        # Try to load from config file
        proxy_config = load_proxy_config()
        if proxy_config:
            proxy_url = proxy_config['url']
            print("\n✓ Loaded proxy configuration from proxy-config.py")
        else:
            print("\n⚠ No proxy configuration found!")
            print("\nOptions:")
            print("  1. Create scripts/proxy-config.py (see proxy-config.example.py)")
            print("  2. Pass proxy as command line argument")
            sys.exit(1)

    # Test proxy if requested
    if proxy_config['test']:
        print("\n" + "-" * 70)
        if not test_proxy(proxy_url):
            print("\n✗ Proxy test failed. Please check your proxy configuration.")
            sys.exit(1)
        print("-" * 70)

    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        print("\n✗ Invalid YouTube URL")
        sys.exit(1)

    print(f"\n✓ Processing video ID: {video_id}")

    # Setup directories
    data_dir = Path('/Users/yourox/AI-Workspace/data/transcripts')
    data_dir.mkdir(parents=True, exist_ok=True)

    batch_file = data_dir / 'batch_20251015_201035.json'

    print("\n" + "=" * 70)
    print("Step 1: Fetching Video Information")
    print("=" * 70)

    # Get video info
    video_info = get_video_info(video_id, proxy_url)
    if not video_info:
        print("\n✗ Failed to get video information")
        sys.exit(1)

    print(f"✓ Title: {video_info.get('title')}")
    print(f"✓ Duration: {video_info.get('duration')}s")
    print(f"✓ Channel: {video_info.get('channel', 'Unknown')}")

    print("\n" + "=" * 70)
    print("Step 2: Downloading Transcript")
    print("=" * 70)

    # Download transcript with proxy
    if not download_with_proxy(video_id, data_dir, proxy_url, proxy_config['retries']):
        print("\n✗ Failed to download transcript")
        print("\nTroubleshooting:")
        print("  - Check your proxy service subscription status")
        print("  - Verify proxy credentials are correct")
        print("  - Try a different proxy server/location")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("Step 3: Processing Transcript")
    print("=" * 70)

    # Process transcript
    transcript = process_transcript(video_id, data_dir)
    if not transcript:
        print("\n✗ Failed to process transcript")
        sys.exit(1)

    print(f"✓ Processed {transcript['segment_count']} segments")

    print("\n" + "=" * 70)
    print("Step 4: Adding to TubeDB")
    print("=" * 70)

    # Create video entry
    video_entry = create_video_entry(video_id, video_info, transcript)

    # Add to batch file
    if add_to_batch(video_entry, batch_file):
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Video added to TubeDB")
        print("=" * 70)
        print(f"Video ID: {video_id}")
        print(f"Title: {video_info.get('title')}")
        print(f"Segments: {transcript['segment_count']}")
        print(f"\n🌐 Refresh http://localhost:4000 to see the new video!")
    else:
        print("\n✗ Failed to add video to batch file (may already exist)")
        sys.exit(1)

if __name__ == '__main__':
    main()
