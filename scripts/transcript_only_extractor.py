#!/usr/bin/env python3
"""
Transcript-Only Extractor
Extracts transcripts WITHOUT using API for BI analysis
BI analysis will be done by Claude Code terminal instead
"""

import sys
import json
import time
from pathlib import Path
from browserbase_transcript_extractor import extract_youtube_transcript, save_transcript

def extract_transcript_only(video_id: str, workspace_dir: str = "/Users/yourox/AI-Workspace"):
    """
    Extract only the transcript (no BI analysis via API)

    Returns:
        dict: Transcript data or None if failed
    """
    workspace = Path(workspace_dir)
    transcripts_dir = workspace / "data" / "transcripts"

    transcript_file = transcripts_dir / f"{video_id}_full.json"

    # Check if already exists
    if transcript_file.exists():
        print(f"⚡ [{video_id}] Transcript already exists, loading...")
        with open(transcript_file, 'r') as f:
            return json.load(f)

    print(f"📹 [{video_id}] Extracting transcript...")
    start_time = time.time()

    try:
        transcript_data = extract_youtube_transcript(video_id)

        if transcript_data.get('status') == 'success':
            save_transcript(video_id, transcript_data)
            elapsed = time.time() - start_time

            comment_count = transcript_data.get('comments', {}).get('count', 0)
            print(f"✅ [{video_id}] Transcript + {comment_count} comments extracted in {elapsed:.1f}s")

            return transcript_data
        else:
            error = transcript_data.get('error', 'Unknown error')
            print(f"❌ [{video_id}] Failed: {error}")
            return None

    except Exception as e:
        print(f"❌ [{video_id}] Exception: {e}")
        return None


def batch_extract_transcripts(video_ids: list):
    """Extract transcripts for multiple videos (sequential, no API calls)"""

    print(f"\n{'='*80}")
    print(f"📹 TRANSCRIPT-ONLY EXTRACTION (No API Usage)")
    print(f"{'='*80}\n")
    print(f"Total videos: {len(video_ids)}")
    print(f"Mode: Sequential (to avoid Browserbase rate limits)")
    print(f"BI Analysis: Will be done by Claude Code terminal (free!)\n")

    results = {
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'transcripts': []
    }

    for i, video_id in enumerate(video_ids, 1):
        print(f"\n[{i}/{len(video_ids)}] Processing {video_id}...")

        transcript_data = extract_transcript_only(video_id)

        if transcript_data:
            if transcript_data.get('status') == 'success':
                results['success'] += 1
                results['transcripts'].append({
                    'video_id': video_id,
                    'title': transcript_data.get('title', 'Unknown'),
                    'segment_count': transcript_data.get('transcript', {}).get('segment_count', 0),
                    'comment_count': transcript_data.get('comments', {}).get('count', 0)
                })
            else:
                results['failed'] += 1
        else:
            results['skipped'] += 1

    print(f"\n{'='*80}")
    print(f"✅ EXTRACTION COMPLETE")
    print(f"{'='*80}\n")
    print(f"✅ Success: {results['success']}")
    print(f"⚡ Skipped: {results['skipped']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"\n💡 Next: Feed these transcripts to Claude Code terminal for BI analysis (FREE!)")
    print(f"{'='*80}\n")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 transcript_only_extractor.py VIDEO_ID1 VIDEO_ID2 ...")
        print("   or: python3 transcript_only_extractor.py --file VIDEO_IDS.txt")
        sys.exit(1)

    if sys.argv[1] == "--file":
        with open(sys.argv[2], 'r') as f:
            video_ids = [line.strip() for line in f if line.strip()]
    else:
        video_ids = sys.argv[1:]

    results = batch_extract_transcripts(video_ids)

    # Save results
    results_file = Path("/Users/yourox/AI-Workspace/data/transcript_extraction_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"📊 Results saved to: {results_file}\n")
