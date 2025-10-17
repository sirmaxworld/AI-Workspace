#!/usr/bin/env python3
import json
import glob
from pathlib import Path

transcript_files = glob.glob('/Users/yourox/AI-Workspace/data/transcripts/*.json')

print(f"Found {len(transcript_files)} transcript files\n")
print("Checking transcript durations:")
print("-" * 60)

for file_path in transcript_files[:10]:  # Check first 10
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        segments = data.get('transcript', {}).get('segments', [])
        if segments:
            last_timestamp = segments[-1]['start']
            duration_minutes = int(last_timestamp / 60)
            title = data.get('title', 'Unknown')[:50]

            print(f"Video: {Path(file_path).stem}")
            print(f"  Title: {title}...")
            print(f"  Segments: {len(segments)}")
            print(f"  Duration: ~{duration_minutes} minutes ({last_timestamp:.1f} seconds)")
            print()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")