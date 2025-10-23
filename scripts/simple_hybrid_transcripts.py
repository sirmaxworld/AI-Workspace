#!/usr/bin/env python3
"""Simple batch transcript extractor using hybrid method - transcripts only, no enrichment"""

import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
sys.path.insert(0, '/Users/yourox/AI-Workspace/scripts')

from hybrid_transcript_extractor import HybridTranscriptExtractor

def process_video(video_id: str, index: int, total: int):
    """Extract transcript for one video"""
    print(f"[{index}/{total}] Processing {video_id}...")

    extractor = HybridTranscriptExtractor()
    result = extractor.extract_transcript(video_id)

    if result.get('status') == 'success':
        extractor.save_transcript(video_id, result)
        segments = result.get('transcript', {}).get('segment_count', 0)
        print(f"[{index}/{total}] ✅ {video_id}: {segments} segments")
        return True
    else:
        print(f"[{index}/{total}] ❌ {video_id}: {result.get('error')}")
        return False

# Read video IDs
video_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/tier2_3_videos.txt'
max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 30

with open(video_file) as f:
    video_ids = [line.strip() for line in f if line.strip()]

print(f"\n🚀 Simple Hybrid Transcript Extractor")
print(f"Videos: {len(video_ids)} | Workers: {max_workers}\n")

start = time.time()
success = 0
failed = 0

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {
        executor.submit(process_video, vid, i, len(video_ids)): vid
        for i, vid in enumerate(video_ids, 1)
    }

    for future in as_completed(futures):
        if future.result():
            success += 1
        else:
            failed += 1

elapsed = time.time() - start

print(f"\n{'='*70}")
print(f"✅ COMPLETE")
print(f"Time: {elapsed/60:.1f} min | Success: {success} | Failed: {failed}")
print(f"Success rate: {success/len(video_ids)*100:.1f}%")
print(f"{'='*70}")
