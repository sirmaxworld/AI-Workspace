#!/usr/bin/env python3
"""
Simple test to verify batch processing works
"""

import json
from pathlib import Path
from datetime import datetime

# Check what we have
TRANSCRIPTS_PATH = Path('/Users/yourox/AI-Workspace/data/transcripts')

def analyze_current_state():
    """Analyze current state of transcripts"""
    print("\n" + "="*80)
    print("CURRENT TRANSCRIPT STATE ANALYSIS")
    print("="*80 + "\n")

    # Count different file types
    json_files = list(TRANSCRIPTS_PATH.glob("*.json"))
    full_json_files = list(TRANSCRIPTS_PATH.glob("*_full.json"))
    audio_files = list(TRANSCRIPTS_PATH.glob("*_audio.*"))
    batch_files = list(TRANSCRIPTS_PATH.glob("batch_*.json"))

    print(f"📁 Transcript Directory: {TRANSCRIPTS_PATH}")
    print(f"\n📊 File Counts:")
    print(f"  • Total JSON files: {len(json_files)}")
    print(f"  • Full transcript files (*_full.json): {len(full_json_files)}")
    print(f"  • Batch files: {len(batch_files)}")
    print(f"  • Audio files: {len(audio_files)}")

    # Extract unique video IDs
    video_ids = set()
    for file_path in TRANSCRIPTS_PATH.glob("*.json"):
        filename = file_path.stem

        # Skip batch files
        if filename.startswith('batch_'):
            continue

        # Extract video ID
        if filename.endswith('_full'):
            video_id = filename[:-5]
        elif filename.endswith('_insights'):
            video_id = filename[:-9]
        elif not filename.endswith('_audio'):
            video_id = filename
        else:
            continue

        # Validate it looks like a YouTube ID
        if len(video_id) == 11:
            video_ids.add(video_id)

    print(f"\n🎥 Unique Videos Processed: {len(video_ids)}")

    # Check cache naming issues
    naming_issues = []
    for vid_id in video_ids:
        standard = TRANSCRIPTS_PATH / f"{vid_id}.json"
        full = TRANSCRIPTS_PATH / f"{vid_id}_full.json"

        if full.exists() and not standard.exists():
            naming_issues.append(vid_id)

    if naming_issues:
        print(f"\n⚠️ Cache Naming Issues Found: {len(naming_issues)} videos")
        print("  These have _full.json but missing standard .json:")
        for vid in naming_issues[:5]:
            print(f"    • {vid}")
    else:
        print(f"\n✅ No cache naming issues found")

    # Show recent files
    all_files = list(TRANSCRIPTS_PATH.glob("*.json"))
    all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    print(f"\n🆕 Most Recent Files:")
    for file_path in all_files[:5]:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"  • {file_path.name}")
        print(f"    Modified: {mtime.strftime('%Y-%m-%d %H:%M')}, Size: {size_mb:.2f} MB")

    # Check a sample transcript
    if full_json_files:
        sample_file = full_json_files[0]
        print(f"\n📝 Sample Transcript: {sample_file.name}")

        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list) and len(data) > 0:
                # It's a batch file
                video = data[0]
                print(f"  Type: Batch file with {len(data)} videos")
                print(f"  First video: {video.get('title', 'Unknown')[:50]}...")
            else:
                # It's a single video
                print(f"  Video ID: {data.get('video_id', 'Unknown')}")
                print(f"  Title: {data.get('title', 'Unknown')[:50]}...")
                print(f"  Method: {data.get('method', 'Unknown')}")

                transcript = data.get('transcript', {})
                if isinstance(transcript, dict):
                    segments = transcript.get('segments', [])
                    print(f"  Segments: {len(segments)}")
                elif isinstance(transcript, list):
                    print(f"  Segments: {len(transcript)}")

        except Exception as e:
            print(f"  Error reading sample: {e}")

    return video_ids, naming_issues


def fix_naming_issues(naming_issues):
    """Fix cache file naming issues"""
    if not naming_issues:
        print("\n✅ No naming issues to fix")
        return

    print(f"\n🔧 Fixing {len(naming_issues)} naming issues...")

    import shutil
    fixed = 0

    for vid_id in naming_issues:
        full_path = TRANSCRIPTS_PATH / f"{vid_id}_full.json"
        standard_path = TRANSCRIPTS_PATH / f"{vid_id}.json"

        if full_path.exists() and not standard_path.exists():
            try:
                shutil.copy2(full_path, standard_path)
                print(f"  ✓ Fixed: {vid_id}")
                fixed += 1
            except Exception as e:
                print(f"  ✗ Failed to fix {vid_id}: {e}")

    print(f"\n✅ Fixed {fixed}/{len(naming_issues)} files")


def main():
    """Main test function"""
    print("\n🔍 Testing YouTube Batch Processing Setup\n")

    # Analyze current state
    video_ids, naming_issues = analyze_current_state()

    # Fix naming issues if any
    if naming_issues:
        response = input("\n❓ Fix naming issues? (y/n): ")
        if response.lower() == 'y':
            fix_naming_issues(naming_issues)
            # Re-analyze
            print("\n🔄 Re-analyzing after fixes...")
            video_ids, naming_issues = analyze_current_state()

    print("\n" + "="*80)
    print("✅ Analysis Complete")
    print("="*80 + "\n")

    print("📌 Summary:")
    print(f"  • Total unique videos: {len(video_ids)}")
    print(f"  • Naming issues remaining: {len(naming_issues)}")
    print(f"\n💡 Ready to process new videos!")


if __name__ == "__main__":
    main()