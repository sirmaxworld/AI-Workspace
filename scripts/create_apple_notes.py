#!/usr/bin/env python3.11
"""
Create Apple Notes for all TubeDB videos
"""
import json
from pathlib import Path

def format_timestamp(seconds):
    """Convert seconds to MM:SS format"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"[{mins:02d}:{secs:02d}]"

def create_video_note(video):
    """Format a video into a nice Apple Note structure"""
    
    # Extract metadata
    video_id = video['video_id']
    title = video['title']
    url = f"https://youtube.com/watch?v={video_id}"
    
    # Transcript data
    transcript = video['transcript']
    segments = transcript['segments']
    segment_count = len(segments)
    
    # Calculate duration from last segment
    if segments:
        last_seg = segments[-1]
        duration_secs = last_seg['start'] + last_seg['duration']
        duration_mins = int(duration_secs // 60)
    else:
        duration_mins = 0
    
    # QC data if available
    qc = video.get('qc_verification', {})
    quality = qc.get('quality_score', 'N/A')
    topics = qc.get('key_topics', [])
    summary = qc.get('summary', 'No summary available')
    
    # Build the note content
    note = f"""🎬 {title}

📊 METADATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Video ID: {video_id}
URL: {url}
Duration: ~{duration_mins} minutes
Segments: {segment_count:,}
Quality Score: {quality} {'⭐' if isinstance(quality, (int, float)) and quality >= 0.8 else ''}

📝 AI SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{summary}

🎯 KEY TOPICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Add topics
    if topics:
        for topic in topics:
            note += f"• {topic}\n"
    else:
        note += "• No topics extracted\n"
    
    note += "\n📜 FULL TRANSCRIPT\n"
    note += "━" * 40 + "\n\n"
    
    # Add all transcript segments with timestamps
    for segment in segments:
        timestamp = format_timestamp(segment['start'])
        text = segment['text']
        note += f"{timestamp} {text}\n"
    
    return note

def main():
    # Load the transcript data
    transcript_file = Path("/Users/yourox/AI-Workspace/data/transcripts/batch_20251015_193743.json")
    
    with open(transcript_file, 'r') as f:
        videos = json.load(f)
    
    print(f"📹 Processing {len(videos)} videos...")
    print()
    
    # Process each video
    for i, video in enumerate(videos, 1):
        title = video['title']
        note_content = create_video_note(video)
        
        # Save to a temp file that we can use to create the Apple Note
        output_file = Path(f"/tmp/tubedb_video_{i}.txt")
        with open(output_file, 'w') as f:
            f.write(note_content)
        
        print(f"✅ {i}. {title}")
        print(f"   📝 Saved to: {output_file}")
        print(f"   📏 Size: {len(note_content):,} characters")
        print()
    
    print("🎉 All videos processed!")
    print("\nNote files created in /tmp/ directory")

if __name__ == "__main__":
    main()
