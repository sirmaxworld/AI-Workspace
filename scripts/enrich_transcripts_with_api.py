#!/usr/bin/env python3
"""
Batch enrich existing transcripts with YouTube API metadata and comments
"""

import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from youtube_api_comment_extractor import YouTubeAPIExtractor


def enrich_single_transcript(transcript_file: Path, max_comments: int = 100) -> dict:
    """Enrich a single transcript file"""
    try:
        extractor = YouTubeAPIExtractor()

        with open(transcript_file) as f:
            data = json.load(f)

        video_id = data.get('video_id')
        if not video_id:
            return {'file': transcript_file.name, 'status': 'skipped', 'reason': 'no_video_id'}

        # Check if already enriched with good comment data
        existing_comments = data.get('comments', [])
        if isinstance(existing_comments, list):
            comment_count = len(existing_comments)
        elif isinstance(existing_comments, dict):
            comment_count = len(existing_comments.get('top_comments', []))
        else:
            comment_count = 0

        # Skip if we already have 20+ comments (good quality)
        if comment_count >= 20 and data.get('extraction_method') == 'youtube_api_v3':
            return {'file': transcript_file.name, 'status': 'skipped', 'reason': 'already_enriched'}

        # Get API data
        api_data = extractor.get_video_full_data(video_id, max_comments)

        if api_data.get('status') == 'error':
            return {'file': transcript_file.name, 'status': 'error', 'error': api_data.get('error')}

        # Merge data
        enriched = {
            **data,  # Keep transcript
            'title': api_data.get('title', data.get('title', '')),
            'channel': api_data.get('channel', data.get('channel', '')),
            'metadata': {
                'channel_id': api_data.get('channel_id', ''),
                'description': api_data.get('description', ''),
                'published_at': api_data.get('published_at', ''),
                'tags': api_data.get('tags', []),
                'duration': api_data.get('duration', ''),
                'views': api_data.get('views', 0),
                'likes': api_data.get('likes', 0),
                'comment_count_total': api_data.get('comment_count', 0),
                'thumbnail': api_data.get('thumbnail', '')
            },
            'comments': api_data.get('comments', []),
            'comments_extracted': len(api_data.get('comments', [])),
            'extraction_method': 'youtube_api_v3'
        }

        # Save
        with open(transcript_file, 'w') as f:
            json.dump(enriched, f, indent=2)

        return {
            'file': transcript_file.name,
            'status': 'success',
            'comments_before': comment_count,
            'comments_after': len(api_data.get('comments', [])),
            'quota_used': api_data.get('quota_used', 0)
        }

    except Exception as e:
        return {'file': transcript_file.name, 'status': 'error', 'error': str(e)}


def batch_enrich_transcripts(
    transcripts_dir: str = "/Users/yourox/AI-Workspace/data/transcripts",
    max_workers: int = 10,
    max_comments_per_video: int = 100,
    limit: int = None
):
    """
    Batch enrich transcripts with API data

    Args:
        max_workers: Number of parallel workers (be careful with API quota)
        max_comments_per_video: Max comments to fetch per video
        limit: Limit number of files to process (for testing)
    """

    print(f"\n{'='*70}")
    print(f"🚀 BATCH TRANSCRIPT ENRICHMENT")
    print(f"{'='*70}\n")

    transcripts_path = Path(transcripts_dir)
    all_files = list(transcripts_path.glob('*_full.json'))

    if limit:
        all_files = all_files[:limit]

    print(f"📁 Found {len(all_files)} transcript files")
    print(f"⚙️  Workers: {max_workers}")
    print(f"💬 Max comments per video: {max_comments_per_video}")

    # Daily API quota: 10,000 units
    # Cost per video: ~2-3 units (1 metadata + 1-2 comments)
    # Max videos per day: ~3,000-5,000
    estimated_quota = len(all_files) * 3
    print(f"📊 Estimated quota usage: {estimated_quota:,} units")

    if estimated_quota > 10000:
        print(f"⚠️  WARNING: Estimated quota exceeds daily limit!")
        print(f"   Consider processing in batches or reducing max_comments")

    print(f"\n{'='*70}\n")

    results = {
        'success': 0,
        'skipped': 0,
        'error': 0,
        'total_quota': 0,
        'comments_improved': 0
    }

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(enrich_single_transcript, file, max_comments_per_video): file
            for file in all_files
        }

        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()

            status = result.get('status')
            results[status] = results.get(status, 0) + 1

            if status == 'success':
                results['total_quota'] += result.get('quota_used', 0)
                before = result.get('comments_before', 0)
                after = result.get('comments_after', 0)
                if after > before:
                    results['comments_improved'] += 1
                    print(f"✅ [{i}/{len(all_files)}] {result['file']}: {before} → {after} comments")
                else:
                    print(f"✅ [{i}/{len(all_files)}] {result['file']}: {after} comments")
            elif status == 'skipped':
                print(f"⏭️  [{i}/{len(all_files)}] {result['file']}: {result.get('reason')}")
            else:
                print(f"❌ [{i}/{len(all_files)}] {result['file']}: {result.get('error')}")

            # Progress report every 50 files
            if i % 50 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                remaining = (len(all_files) - i) / rate if rate > 0 else 0
                print(f"\n📊 Progress: {i}/{len(all_files)} ({i/len(all_files)*100:.1f}%)")
                print(f"⏱️  Rate: {rate:.1f} files/sec | ETA: {remaining/60:.1f} min")
                print(f"📈 Quota used: {results['total_quota']:,} units\n")

    elapsed = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"📊 ENRICHMENT COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Success: {results['success']}")
    print(f"⏭️  Skipped: {results['skipped']}")
    print(f"❌ Errors: {results['error']}")
    print(f"💬 Comments improved: {results['comments_improved']}")
    print(f"📈 Total quota used: {results['total_quota']:,} units")
    print(f"⏱️  Time: {elapsed/60:.1f} minutes")
    print(f"{'='*70}\n")

    return results


if __name__ == "__main__":
    import sys

    # Allow command-line arguments
    max_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None

    # Run batch enrichment
    batch_enrich_transcripts(
        max_workers=max_workers,
        max_comments_per_video=100,
        limit=limit
    )
