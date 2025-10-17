#!/usr/bin/env python3.11
"""
Efficiently create Apple Notes from transcript files
"""
import subprocess
import os
from pathlib import Path

def create_apple_note(title, content):
    """Create an Apple Note using osascript"""
    # Escape quotes in content
    content_escaped = content.replace('"', '\\"').replace('`', '\\`')
    title_escaped = title.replace('"', '\\"')
    
    applescript = f'''
    tell application "Notes"
        tell folder "Notes"
            make new note with properties {{name:"{title_escaped}", body:"{content_escaped}"}}
        end tell
    end tell
    '''
    
    subprocess.run(['osascript', '-e', applescript])

# Process all 5 video files
video_files = [
    "/tmp/tubedb_video_1.txt",
    "/tmp/tubedb_video_2.txt", 
    "/tmp/tubedb_video_3.txt",
    "/tmp/tubedb_video_4.txt",
    "/tmp/tubedb_video_5.txt"
]

print("📝 Creating Apple Notes...")
print()

for i, filepath in enumerate(video_files, 1):
    if Path(filepath).exists():
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract title from first line
        title = content.split('\n')[0].replace('🎬 ', 'TubeDB - ')
        
        print(f"✅ Creating note {i}: {title}")
        create_apple_note(title, content)
    else:
        print(f"⚠️ File not found: {filepath}")

print()
print("🎉 All notes created in Apple Notes!")
