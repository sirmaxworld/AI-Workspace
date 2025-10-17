#!/usr/bin/env python3
"""
Quick extraction: Channel → QC → Transcribe → Mem0
Streamlined pipeline for rapid testing
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from source_adapters import YouTubeAdapter, ExtractionConfig
from quality_control import QualityControlSystem
from youtube_transcriber_pro import YouTubeTranscriberPro


async def extract_and_store(channel_handle: str, max_videos: int = 5):
    """
    Complete pipeline: Extract → QC → Transcribe → Store in Mem0

    Args:
        channel_handle: YouTube channel handle (e.g., @GregIsenberg)
        max_videos: Maximum videos to process
    """

    print(f"\n{'='*80}")
    print(f"🚀 RAPID EXTRACTION TO MEM0")
    print(f"   Channel: {channel_handle}")
    print(f"   Videos: {max_videos}")
    print(f"{'='*80}\n")

    # Step 1: Extract videos using adapter
    print(f"📺 STEP 1: Extracting videos...")
    config = ExtractionConfig(
        max_items=max_videos,
        filters={
            'exclude_shorts': True,
            'min_duration': 300  # 5 minutes minimum
        }
    )

    adapter = YouTubeAdapter(config)
    items = adapter.extract_batch({
        'handle': channel_handle,
        'max_videos': max_videos
    })

    if not items:
        print("❌ No videos extracted")
        return

    print(f"✓ Extracted {len(items)} videos\n")

    # Step 2: Quality Control (automated only for speed)
    print(f"🔍 STEP 2: Running quality control...")
    qc = QualityControlSystem()

    validated_items = []
    for item in items:
        # Run automated QC only (fast)
        result = qc.validate(item.to_dict(), enable_ai_qc=False)

        status = "✓" if result.passed else "⏭"
        confidence = result.confidence
        print(f"   {status} {item.title[:60]} - Confidence: {confidence:.2f}")

        if result.passed:
            validated_items.append(item)

    print(f"\n✓ QC Complete: {len(validated_items)}/{len(items)} passed\n")

    # Step 3: Transcribe and store in Mem0
    print(f"📝 STEP 3: Transcribing and storing in Mem0...")

    transcriber = YouTubeTranscriberPro(
        user_id="greg_isenberg_knowledge",
        use_whisper_fallback=True
    )

    results = []
    for idx, item in enumerate(validated_items, 1):
        print(f"\n[{idx}/{len(validated_items)}] Processing: {item.title[:60]}")

        try:
            result = await transcriber.process_video(item.url)

            if result['status'] == 'success':
                results.append({
                    'video_id': item.id,
                    'title': item.title,
                    'status': 'success',
                    'chunks': result.get('chunks', 0),
                    'method': result.get('method', 'unknown')
                })
                print(f"   ✓ Stored {result.get('chunks', 0)} chunks in Mem0")
            else:
                results.append({
                    'video_id': item.id,
                    'title': item.title,
                    'status': 'failed',
                    'error': result.get('message', 'Unknown error')
                })
                print(f"   ❌ Failed: {result.get('message', 'Unknown error')}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'video_id': item.id,
                'title': item.title,
                'status': 'error',
                'error': str(e)
            })

    # Summary
    print(f"\n{'='*80}")
    print(f"📊 PIPELINE COMPLETE")
    print(f"{'='*80}")

    successful = sum(1 for r in results if r['status'] == 'success')
    total_chunks = sum(r.get('chunks', 0) for r in results if r['status'] == 'success')

    print(f"\n✅ Summary:")
    print(f"   Videos extracted: {len(items)}")
    print(f"   Passed QC: {len(validated_items)}")
    print(f"   Successfully transcribed: {successful}")
    print(f"   Total chunks in Mem0: {total_chunks}")

    # Save report
    report = {
        'channel': channel_handle,
        'timestamp': datetime.now().isoformat(),
        'videos_extracted': len(items),
        'videos_validated': len(validated_items),
        'videos_stored': successful,
        'total_chunks': total_chunks,
        'results': results
    }

    report_path = Path('/Users/yourox/AI-Workspace/data/extraction_reports')
    report_path.mkdir(parents=True, exist_ok=True)

    report_file = report_path / f"quick_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved: {report_file}")
    print(f"\n{'='*80}\n")

    return report


async def main():
    import argparse

    parser = argparse.ArgumentParser(description='Quick extraction to Mem0')
    parser.add_argument('--channel', default='@GregIsenberg', help='Channel handle')
    parser.add_argument('--max-videos', type=int, default=5, help='Max videos')

    args = parser.parse_args()

    report = await extract_and_store(args.channel, args.max_videos)

    # Show how to search
    if report and report['videos_stored'] > 0:
        print(f"🔍 To search the knowledge base:")
        print(f"   from youtube_transcriber_pro import YouTubeTranscriberPro")
        print(f"   transcriber = YouTubeTranscriberPro(user_id='greg_isenberg_knowledge')")
        print(f"   results = transcriber.search('your query', limit=5)")


if __name__ == '__main__':
    asyncio.run(main())
