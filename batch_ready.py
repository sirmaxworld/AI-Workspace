#!/usr/bin/env python3
"""
Prepare and analyze what needs to be processed
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_PATH = Path('/Users/yourox/AI-Workspace')
TRANSCRIPTS_PATH = BASE_PATH / 'data' / 'transcripts'
QC_REPORTS_PATH = BASE_PATH / 'data' / 'qc_reports'

def get_processed_videos():
    """Get list of already processed video IDs"""
    processed = set()

    # Check all JSON files
    for file_path in TRANSCRIPTS_PATH.glob('*.json'):
        filename = file_path.stem

        # Skip batch files
        if filename.startswith('batch_'):
            continue

        # Extract video ID
        if filename.endswith('_full'):
            video_id = filename[:-5]
        elif filename.endswith('_insights'):
            continue
        elif len(filename) == 11:  # Standard YouTube ID length
            video_id = filename
        else:
            continue

        processed.add(video_id)

    return processed

def analyze_greg_isenberg_videos():
    """Analyze what Greg Isenberg videos we have"""

    # Get the QC report to see what videos were listed
    qc_report_path = QC_REPORTS_PATH / 'Greg_Isenberg_pipeline_20251015_164417.json'

    if qc_report_path.exists():
        with open(qc_report_path, 'r') as f:
            qc_data = json.load(f)

        all_videos = qc_data.get('videos', [])
        print(f"\n📺 Found {len(all_videos)} Greg Isenberg videos in QC report")

        # Get processed videos
        processed = get_processed_videos()
        print(f"✅ Already processed: {len(processed)} videos total")

        # Check which Greg videos are processed
        greg_processed = []
        greg_unprocessed = []

        for video in all_videos:
            video_id = video['id']
            if video_id in processed:
                greg_processed.append(video)
            else:
                greg_unprocessed.append(video)

        print(f"\n📊 Greg Isenberg Channel Status:")
        print(f"  • Processed: {len(greg_processed)}")
        print(f"  • Unprocessed: {len(greg_unprocessed)}")

        if greg_unprocessed:
            print(f"\n🎯 Next 5 videos to process:")
            for i, video in enumerate(greg_unprocessed[:5], 1):
                print(f"  {i}. {video['title'][:60]}...")
                print(f"     ID: {video['id']}")
                print(f"     Duration: {video['duration_formatted']}")
                print(f"     Views: {video.get('view_count', 'N/A'):,}")

        return all_videos, greg_processed, greg_unprocessed
    else:
        print("❌ No QC report found")
        return [], [], []

def create_processing_script(unprocessed_videos):
    """Create a ready-to-run script for processing specific videos"""

    if not unprocessed_videos:
        print("\n✅ All videos already processed!")
        return

    # Take next 5 videos
    to_process = unprocessed_videos[:5]

    script_content = f'''#!/usr/bin/env python3
"""
Auto-generated script to process next 5 videos
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import asyncio
import sys
sys.path.insert(0, '/Users/yourox/AI-Workspace/scripts')

from youtube_transcriber_pro import YouTubeTranscriberPro
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

async def process_videos():
    """Process the next batch of videos"""

    videos = {json.dumps([{"id": v["id"], "title": v["title"], "url": v["url"]} for v in to_process], indent=8)}

    transcriber = YouTubeTranscriberPro(
        user_id="yourox_batch_process",
        use_whisper_fallback=True
    )

    results = []
    for video in videos:
        print(f"\\nProcessing: {{video['title'][:60]}}...")
        result = await transcriber.process_video(video['url'])
        results.append(result)

        if result['status'] == 'success':
            print(f"✅ Success: {{result.get('method')}} - {{result.get('chunks')}} chunks")
        else:
            print(f"❌ Failed: {{result.get('message')}}")

    # Print summary
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"\\n{'='*60}}")
    print(f"BATCH COMPLETE: {{successful}}/{{len(videos)}} successful")
    print(f"{'='*60}}")

    transcriber.print_stats()
    return results

if __name__ == "__main__":
    results = asyncio.run(process_videos())
'''

    script_path = BASE_PATH / 'process_next_5.py'
    with open(script_path, 'w') as f:
        f.write(script_content)

    print(f"\n✅ Created processing script: {script_path}")
    print(f"   Run with: python3 {script_path}")

    return to_process

def main():
    print("\n" + "="*80)
    print("📊 YOUTUBE DATABASE BATCH PREPARATION")
    print("="*80)

    # Analyze current state
    all_videos, processed, unprocessed = analyze_greg_isenberg_videos()

    if unprocessed:
        # Create processing script
        to_process = create_processing_script(unprocessed)

        # Create summary report
        report = {
            "timestamp": datetime.now().isoformat(),
            "channel": "Greg Isenberg",
            "total_videos_found": len(all_videos),
            "already_processed": len(processed),
            "unprocessed": len(unprocessed),
            "next_batch": [
                {
                    "id": v["id"],
                    "title": v["title"],
                    "duration": v["duration_formatted"],
                    "url": v["url"]
                } for v in to_process
            ] if unprocessed else []
        }

        report_path = BASE_PATH / 'batch_preparation_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📋 Batch Preparation Report saved to: {report_path}")

        print("\n" + "="*80)
        print("✅ READY TO PROCESS")
        print("="*80)
        print("\nTo process the next 5 videos, run:")
        print("  python3 process_next_5.py")
        print("\nOr use the improved batch processor:")
        print("  python3 process_youtube_batch.py")
    else:
        print("\n✅ All videos from the QC report have been processed!")
        print("   To get more videos, run the channel extractor with a higher limit.")

    return report if unprocessed else None

if __name__ == "__main__":
    report = main()