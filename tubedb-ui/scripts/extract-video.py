#!/usr/bin/env python3
"""
Extract YouTube video transcript and add to TubeDB
"""
import sys
import json
import subprocess
import os
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

def download_transcript(video_id, output_dir):
    """Download transcript using yt-dlp"""
    print(f"Downloading transcript for {video_id}...")

    cmd = [
        'yt-dlp',
        '--write-auto-sub',
        '--write-sub',
        '--sub-lang', 'en',
        '--sub-format', 'json3',
        '--skip-download',
        '--output', f'{output_dir}/{video_id}',
        f'https://www.youtube.com/watch?v={video_id}'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading: {e.stderr}")
        return False

def get_video_info(video_id):
    """Get video metadata using yt-dlp"""
    print(f"Fetching video info for {video_id}...")

    cmd = [
        'yt-dlp',
        '--dump-json',
        '--skip-download',
        f'https://www.youtube.com/watch?v={video_id}'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def process_transcript(video_id, transcript_dir):
    """Process transcript JSON into TubeDB format"""
    transcript_file = Path(transcript_dir) / f'{video_id}.en.json3'

    if not transcript_file.exists():
        print(f"Transcript file not found: {transcript_file}")
        return None

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
    print(f"Adding video to {batch_file}...")

    # Load existing batch
    with open(batch_file, 'r') as f:
        videos = json.load(f)

    # Check if video already exists
    if any(v['video_id'] == video_entry['video_id'] for v in videos):
        print(f"Video {video_entry['video_id']} already exists in batch file")
        return False

    # Add new video
    videos.append(video_entry)

    # Save back to file
    with open(batch_file, 'w') as f:
        json.dump(videos, f, indent=2)

    print(f"Successfully added video! Total videos: {len(videos)}")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract-video.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]
    video_id = extract_video_id(url)

    if not video_id:
        print("Invalid YouTube URL")
        sys.exit(1)

    print(f"Processing video ID: {video_id}")

    # Setup directories
    data_dir = Path('/Users/yourox/AI-Workspace/data/transcripts')
    data_dir.mkdir(parents=True, exist_ok=True)

    batch_file = data_dir / 'batch_20251015_201035.json'

    # Get video info
    video_info = get_video_info(video_id)
    if not video_info:
        print("Failed to get video information")
        sys.exit(1)

    print(f"Title: {video_info.get('title')}")
    print(f"Duration: {video_info.get('duration')}s")

    # Download transcript
    if not download_transcript(video_id, data_dir):
        print("Failed to download transcript")
        sys.exit(1)

    # Process transcript
    transcript = process_transcript(video_id, data_dir)
    if not transcript:
        print("Failed to process transcript")
        sys.exit(1)

    print(f"Processed {transcript['segment_count']} segments")

    # Create video entry
    video_entry = create_video_entry(video_id, video_info, transcript)

    # Add to batch file
    if add_to_batch(video_entry, batch_file):
        print("\n✅ Video successfully added to TubeDB!")
        print(f"Video ID: {video_id}")
        print(f"Segments: {transcript['segment_count']}")
        print("\nRefresh your browser to see the new video!")
    else:
        print("\n❌ Failed to add video to batch file")
        sys.exit(1)

if __name__ == '__main__':
    main()
