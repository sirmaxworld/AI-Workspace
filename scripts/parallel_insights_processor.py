#!/usr/bin/env python3
"""
Parallel Insights Processor
Monitors transcripts and processes them with OpenRouter workers in parallel
"""

import os
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set
from openrouter_bi_extractor import OpenRouterBIExtractor


class ParallelInsightsProcessor:
    """Process transcripts with multiple OpenRouter workers"""

    def __init__(self, max_workers: int = 50):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.transcripts_dir = self.workspace_dir / "data" / "transcripts"
        self.insights_dir = self.workspace_dir / "data" / "business_insights"
        self.max_workers = max_workers
        self.extractor = OpenRouterBIExtractor()

    def get_transcripts_needing_insights(self) -> List[str]:
        """Find all transcripts that don't have insights yet"""
        transcript_files = list(self.transcripts_dir.glob("*_full.json"))
        needing_insights = []

        for tf in transcript_files:
            video_id = tf.stem.replace("_full", "")
            insights_file = self.insights_dir / f"{video_id}_insights.json"

            if not insights_file.exists():
                needing_insights.append(video_id)

        return needing_insights

    def process_single_video(self, video_id: str) -> tuple:
        """Process a single video and return result"""
        try:
            start = time.time()
            insights = self.extractor.process_transcript(video_id)
            elapsed = time.time() - start

            if insights and 'error' not in insights:
                return (video_id, True, elapsed, None)
            else:
                error = insights.get('error', 'Unknown error') if insights else 'No insights returned'
                return (video_id, False, elapsed, error)
        except Exception as e:
            return (video_id, False, 0, str(e))

    def process_batch(self, video_ids: List[str]) -> dict:
        """Process a batch of videos with parallel workers"""
        print(f"\n{'='*80}")
        print(f"🚀 PARALLEL INSIGHTS PROCESSING - OpenRouter")
        print(f"{'='*80}\n")
        print(f"Videos to process: {len(video_ids)}")
        print(f"Workers: {self.max_workers}")
        print(f"Model: {self.extractor.model}\n")

        results = {
            'success': 0,
            'failed': 0,
            'total_time': 0,
            'errors': []
        }

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            futures = {executor.submit(self.process_single_video, vid): vid
                      for vid in video_ids}

            # Process results as they complete
            for i, future in enumerate(as_completed(futures), 1):
                video_id = futures[future]

                try:
                    vid, success, elapsed, error = future.result()

                    if success:
                        results['success'] += 1
                        print(f"✅ [{i}/{len(video_ids)}] {vid} ({elapsed:.1f}s)")
                    else:
                        results['failed'] += 1
                        results['errors'].append({'video_id': vid, 'error': error})
                        print(f"❌ [{i}/{len(video_ids)}] {vid}: {error}")

                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({'video_id': video_id, 'error': str(e)})
                    print(f"❌ [{i}/{len(video_ids)}] {video_id}: Exception: {e}")

                # Show progress every 10 videos
                if i % 10 == 0:
                    elapsed_total = time.time() - start_time
                    avg_time = elapsed_total / i
                    remaining = (len(video_ids) - i) * avg_time
                    print(f"\n📊 Progress: {i}/{len(video_ids)} ({i/len(video_ids)*100:.1f}%)")
                    print(f"   Success: {results['success']} | Failed: {results['failed']}")
                    print(f"   Avg time: {avg_time:.1f}s/video | ETA: {remaining/60:.1f}m\n")

        results['total_time'] = time.time() - start_time

        print(f"\n{'='*80}")
        print(f"✅ PARALLEL PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"Success: {results['success']}")
        print(f"Failed: {results['failed']}")
        print(f"Total time: {results['total_time']:.1f}s ({results['total_time']/60:.1f} minutes)")
        print(f"Average: {results['total_time']/len(video_ids):.1f}s per video")
        print(f"{'='*80}\n")

        return results

    def monitor_and_process(self, check_interval: int = 30):
        """
        Monitor for new transcripts and process them continuously
        """
        print(f"\n{'='*80}")
        print(f"👀 MONITORING MODE - Processing transcripts as they appear")
        print(f"{'='*80}\n")
        print(f"Check interval: {check_interval}s")
        print(f"Workers: {self.max_workers}")
        print(f"Press Ctrl+C to stop\n")

        processed: Set[str] = set()

        # Get initial state
        initial_needing = set(self.get_transcripts_needing_insights())
        print(f"Found {len(initial_needing)} transcripts needing insights\n")

        try:
            while True:
                # Check for new transcripts
                current_needing = set(self.get_transcripts_needing_insights())
                new_transcripts = current_needing - processed

                if new_transcripts:
                    print(f"🆕 Found {len(new_transcripts)} new transcripts to process")
                    new_list = list(new_transcripts)

                    # Process them
                    self.process_batch(new_list)

                    # Mark as processed
                    processed.update(new_transcripts)

                # Wait before next check
                time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            print(f"Processed {len(processed)} videos total")


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Parallel Insights Processing via OpenRouter')
    parser.add_argument('--workers', type=int, default=50, help='Number of parallel workers (default: 50)')
    parser.add_argument('--monitor', action='store_true', help='Monitor mode: continuously process new transcripts')
    parser.add_argument('--interval', type=int, default=30, help='Monitor check interval in seconds (default: 30)')
    parser.add_argument('--batch', type=str, help='Process specific batch of video IDs from file')

    args = parser.parse_args()

    processor = ParallelInsightsProcessor(max_workers=args.workers)

    if args.monitor:
        # Monitor mode
        processor.monitor_and_process(check_interval=args.interval)
    elif args.batch:
        # Process specific batch
        with open(args.batch, 'r') as f:
            video_ids = [line.strip() for line in f if line.strip()]
        processor.process_batch(video_ids)
    else:
        # Process all transcripts needing insights
        video_ids = processor.get_transcripts_needing_insights()
        if video_ids:
            processor.process_batch(video_ids)
        else:
            print("✅ All transcripts already have insights!")


if __name__ == "__main__":
    main()
