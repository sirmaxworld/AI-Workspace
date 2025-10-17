#!/usr/bin/env python3
"""
Batch Video Extraction Script (Parallel Version)
Extracts transcripts + comments from multiple YouTube videos, then extracts business intelligence

Features:
1. Parallel processing with ThreadPoolExecutor
2. Optimized comment extraction
3. Full pipeline (transcript -> BI)
"""

import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from browserbase_transcript_extractor import extract_youtube_transcript, save_transcript
from business_intelligence_extractor import BusinessIntelligenceExtractor

def process_single_video(video_id: str, index: int, total: int, skip_existing: bool, workspace: Path, results_lock: Lock, results: dict):
    """
    Process a single video (thread-safe)

    Args:
        video_id: YouTube video ID
        index: Video index (for logging)
        total: Total videos
        skip_existing: Skip if insights exist
        workspace: Workspace directory
        results_lock: Thread lock for results dict
        results: Shared results dict
    """
    transcripts_dir = workspace / "data" / "transcripts"
    insights_dir = workspace / "data" / "business_insights"

    print(f"\n{'='*80}")
    print(f"[{index}/{total}] Processing: {video_id}")
    print(f"{'='*80}\n")

    transcript_file = transcripts_dir / f"{video_id}_full.json"
    insights_file = insights_dir / f"{video_id}_insights.json"

    # Check if already processed
    if skip_existing and insights_file.exists():
        print(f"⚡ Skipping {video_id} - insights already exist")
        with results_lock:
            results['transcripts']['skipped'] += 1
            results['insights']['skipped'] += 1
        return

    # STEP 1: Extract transcript + comments via Browserbase
    print(f"📹 Step 1/2: Extracting transcript + comments...")
    transcript_start = time.time()

    try:
        transcript_data = extract_youtube_transcript(video_id)

        if transcript_data.get('status') == 'success':
            # Save transcript
            save_transcript(video_id, transcript_data)

            transcript_time = time.time() - transcript_start
            print(f"✅ [{video_id}] Transcript extracted in {transcript_time:.1f}s")

            # Check comments
            comments = transcript_data.get('comments', {})
            comment_count = comments.get('count', 0)
            print(f"💬 [{video_id}] Comments extracted: {comment_count}")

            with results_lock:
                results['comments_extracted'] += comment_count
                results['transcripts']['success'] += 1
                results['rate_limit_tests'].append({
                    'video_id': video_id,
                    'time': transcript_time,
                    'success': True,
                    'comments': comment_count
                })
        else:
            print(f"❌ [{video_id}] Transcript extraction failed: {transcript_data.get('error')}")
            with results_lock:
                results['transcripts']['failed'] += 1
            return

    except Exception as e:
        print(f"❌ [{video_id}] Exception during transcript extraction: {e}")
        with results_lock:
            results['transcripts']['failed'] += 1
        return

    # STEP 2: Extract business intelligence
    print(f"\n🧠 [{video_id}] Step 2/2: Extracting business intelligence...")
    insights_start = time.time()

    try:
        bi_extractor = BusinessIntelligenceExtractor()
        insights = bi_extractor.process_transcript(video_id)

        if insights and 'error' not in insights:
            insights_time = time.time() - insights_start
            print(f"✅ [{video_id}] Business intelligence extracted in {insights_time:.1f}s")
            with results_lock:
                results['insights']['success'] += 1
        else:
            print(f"❌ [{video_id}] BI extraction failed: {insights.get('error') if insights else 'No insights'}")
            with results_lock:
                results['insights']['failed'] += 1

    except Exception as e:
        print(f"❌ [{video_id}] Exception during BI extraction: {e}")
        with results_lock:
            results['insights']['failed'] += 1


def batch_extract(video_ids: list, skip_existing: bool = True, max_workers: int = 3):
    """
    Extract transcripts and business intelligence for multiple videos in parallel

    Args:
        video_ids: List of YouTube video IDs
        skip_existing: Skip videos that already have insights
        max_workers: Number of parallel workers (default: 3)
    """
    workspace = Path("/Users/yourox/AI-Workspace")

    print(f"\n{'='*80}")
    print(f"🚀 PARALLEL BATCH VIDEO EXTRACTION")
    print(f"{'='*80}\n")
    print(f"Total videos to process: {len(video_ids)}")
    print(f"Parallel workers: {max_workers}")
    print(f"Skip existing: {skip_existing}\n")

    results = {
        'transcripts': {'success': 0, 'skipped': 0, 'failed': 0},
        'insights': {'success': 0, 'skipped': 0, 'failed': 0},
        'rate_limit_tests': [],
        'comments_extracted': 0,
        'total_time': 0
    }
    results_lock = Lock()

    start_time = time.time()

    # Process videos in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(
                process_single_video,
                video_id,
                i,
                len(video_ids),
                skip_existing,
                workspace,
                results_lock,
                results
            ): video_id
            for i, video_id in enumerate(video_ids, 1)
        }

        # Wait for completion
        for future in as_completed(futures):
            video_id = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"❌ Unexpected error processing {video_id}: {e}")

    # Calculate total time
    results['total_time'] = time.time() - start_time

    # Print summary
    print(f"\n{'='*80}")
    print(f"✅ BATCH EXTRACTION COMPLETE")
    print(f"{'='*80}\n")

    print(f"📊 RESULTS:")
    print(f"\nTranscripts:")
    print(f"  ✅ Success: {results['transcripts']['success']}")
    print(f"  ⚡ Skipped: {results['transcripts']['skipped']}")
    print(f"  ❌ Failed: {results['transcripts']['failed']}")

    print(f"\nBusiness Intelligence:")
    print(f"  ✅ Success: {results['insights']['success']}")
    print(f"  ⚡ Skipped: {results['insights']['skipped']}")
    print(f"  ❌ Failed: {results['insights']['failed']}")

    print(f"\n💬 Comments:")
    print(f"  Total comments extracted: {results['comments_extracted']}")
    print(f"  Average per video: {results['comments_extracted'] / max(results['transcripts']['success'], 1):.1f}")

    print(f"\n🔥 Rate Limiting Test:")
    if results['rate_limit_tests']:
        successful_extractions = [t for t in results['rate_limit_tests'] if t['success']]
        if successful_extractions:
            avg_time = sum(t['time'] for t in successful_extractions) / len(successful_extractions)
            print(f"  ✅ {len(successful_extractions)} successful extractions")
            print(f"  ⏱️  Average time: {avg_time:.1f}s per video")
            print(f"  🎯 Rate limiting: {'BYPASSED ✅' if len(successful_extractions) > 3 else 'NEEDS MORE TESTS'}")
        else:
            print(f"  ❌ No successful extractions to analyze")

    print(f"\n⏱️  Total Time: {results['total_time'] / 60:.1f} minutes")
    print(f"{'='*80}\n")

    return results


def get_greg_isenberg_videos(limit: int = 10) -> list:
    """
    Get list of Greg Isenberg video IDs to extract

    For now, returns a curated list of recent videos
    In production, you'd fetch from YouTube API or channel page
    """
    # Recent Greg Isenberg videos (replace with your own list or API call)
    videos = [
        # Add video IDs here
        # Format: "VIDEO_ID",
    ]

    # If no videos provided, return empty list
    if not videos:
        print("⚠️  No video IDs provided")
        print("Add video IDs to the script or pass them as arguments")
        return []

    return videos[:limit]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Video IDs provided as arguments
        video_ids = sys.argv[1:]
        print(f"Processing {len(video_ids)} videos from arguments")
    else:
        # Use default list
        video_ids = get_greg_isenberg_videos(limit=10)
        if not video_ids:
            print("\nUsage:")
            print("  python3 batch_extract_videos.py VIDEO_ID1 VIDEO_ID2 VIDEO_ID3 ...")
            print("\nExample:")
            print("  python3 batch_extract_videos.py dQw4w9WgXcQ abc123xyz")
            print("\nOr edit the script to add video IDs to get_greg_isenberg_videos()")
            sys.exit(1)

    # Use 3 parallel workers for optimal performance
    results = batch_extract(video_ids, skip_existing=False, max_workers=3)

    # Save results
    results_file = Path("/Users/yourox/AI-Workspace/data/batch_extraction_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"📊 Results saved to: {results_file}\n")
