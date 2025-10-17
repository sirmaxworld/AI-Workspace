#!/usr/bin/env python3
"""
Enhanced Batch Video Extraction Script (Production-Ready for 500+ videos)

Features:
1. Parallel processing with configurable workers
2. Progress tracking with ETA
3. Checkpoint/resume capability
4. Real-time statistics
5. Cost tracking
6. Failure recovery
7. Detailed logging
"""

import sys
import json
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime, timedelta
from browserbase_transcript_extractor import extract_youtube_transcript, save_transcript
from business_intelligence_extractor import BusinessIntelligenceExtractor


class EnhancedBatchExtractor:
    """Production-ready batch extractor for large-scale video processing"""

    def __init__(self, workspace_dir: str = "/Users/yourox/AI-Workspace"):
        self.workspace = Path(workspace_dir)
        self.transcripts_dir = self.workspace / "data" / "transcripts"
        self.insights_dir = self.workspace / "data" / "business_insights"
        self.checkpoint_file = self.workspace / "data" / "batch_checkpoint.json"
        self.failed_videos_file = self.workspace / "data" / "failed_videos.txt"

        # Ensure directories exist
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.insights_dir.mkdir(parents=True, exist_ok=True)

        # Shared state
        self.results = {
            'transcripts': {'success': 0, 'skipped': 0, 'failed': 0},
            'insights': {'success': 0, 'skipped': 0, 'failed': 0},
            'comments_extracted': 0,
            'videos_processed': 0,
            'failed_videos': [],
            'start_time': None,
            'current_batch_start': None,
            'processing_times': []
        }
        self.results_lock = Lock()
        self.start_time = None

    def load_checkpoint(self) -> dict:
        """Load previous checkpoint if exists"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_checkpoint(self, video_ids_remaining: list):
        """Save progress checkpoint"""
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'remaining_videos': video_ids_remaining,
            'elapsed_time': time.time() - self.start_time if self.start_time else 0
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def save_failed_videos(self):
        """Save list of failed videos for retry"""
        if self.results['failed_videos']:
            with open(self.failed_videos_file, 'w') as f:
                for video_id in self.results['failed_videos']:
                    f.write(f"{video_id}\n")

    def calculate_eta(self, videos_processed: int, total_videos: int) -> str:
        """Calculate estimated time remaining"""
        if videos_processed == 0 or not self.results['processing_times']:
            return "Calculating..."

        avg_time = sum(self.results['processing_times']) / len(self.results['processing_times'])
        remaining = total_videos - videos_processed
        seconds_remaining = avg_time * remaining

        eta = timedelta(seconds=int(seconds_remaining))
        return str(eta)

    def print_progress(self, current: int, total: int, video_id: str):
        """Print real-time progress with stats"""
        percent = (current / total * 100) if total > 0 else 0
        elapsed = time.time() - self.start_time if self.start_time else 0
        eta = self.calculate_eta(current, total)

        # Calculate costs
        browserbase_cost = self.results['transcripts']['success'] * 0.0242

        print(f"\n{'='*80}")
        print(f"📊 PROGRESS: {current}/{total} ({percent:.1f}%) | ETA: {eta}")
        print(f"{'='*80}")
        print(f"Current: {video_id}")
        print(f"Elapsed: {timedelta(seconds=int(elapsed))}")
        print(f"\n✅ Transcripts: {self.results['transcripts']['success']} | "
              f"⚡ Skipped: {self.results['transcripts']['skipped']} | "
              f"❌ Failed: {self.results['transcripts']['failed']}")
        print(f"✅ Insights: {self.results['insights']['success']} | "
              f"💬 Comments: {self.results['comments_extracted']}")
        print(f"💰 Cost so far: ${browserbase_cost:.2f} (Browserbase)")
        print(f"{'='*80}\n")

    def process_single_video(self, video_id: str, index: int, total: int, skip_existing: bool):
        """
        Process a single video with enhanced error handling

        Returns:
            tuple: (success: bool, processing_time: float)
        """
        video_start_time = time.time()

        self.print_progress(index, total, video_id)

        transcript_file = self.transcripts_dir / f"{video_id}_full.json"
        insights_file = self.insights_dir / f"{video_id}_insights.json"

        # Check if already processed
        if skip_existing and insights_file.exists():
            print(f"⚡ Skipping {video_id} - insights already exist")
            with self.results_lock:
                self.results['transcripts']['skipped'] += 1
                self.results['insights']['skipped'] += 1
                self.results['videos_processed'] += 1
            return True, 0

        # STEP 1: Extract transcript + comments
        print(f"📹 [{video_id}] Step 1/2: Extracting transcript + comments...")

        try:
            transcript_data = extract_youtube_transcript(video_id)

            if transcript_data.get('status') == 'success':
                save_transcript(video_id, transcript_data)

                comment_count = transcript_data.get('comments', {}).get('count', 0)
                print(f"✅ [{video_id}] Transcript + {comment_count} comments extracted")

                with self.results_lock:
                    self.results['comments_extracted'] += comment_count
                    self.results['transcripts']['success'] += 1
            else:
                error = transcript_data.get('error', 'Unknown error')
                print(f"❌ [{video_id}] Transcript failed: {error}")
                with self.results_lock:
                    self.results['transcripts']['failed'] += 1
                    self.results['failed_videos'].append(video_id)
                    self.results['videos_processed'] += 1
                return False, time.time() - video_start_time

        except Exception as e:
            print(f"❌ [{video_id}] Exception during transcript: {e}")
            with self.results_lock:
                self.results['transcripts']['failed'] += 1
                self.results['failed_videos'].append(video_id)
                self.results['videos_processed'] += 1
            return False, time.time() - video_start_time

        # STEP 2: Extract business intelligence
        print(f"🧠 [{video_id}] Step 2/2: Extracting business intelligence...")

        try:
            bi_extractor = BusinessIntelligenceExtractor()
            insights = bi_extractor.process_transcript(video_id)

            if insights and 'error' not in insights:
                print(f"✅ [{video_id}] Business intelligence extracted")
                with self.results_lock:
                    self.results['insights']['success'] += 1
            else:
                error = insights.get('error', 'No insights') if insights else 'No insights'
                print(f"❌ [{video_id}] BI failed: {error}")
                with self.results_lock:
                    self.results['insights']['failed'] += 1

        except Exception as e:
            print(f"❌ [{video_id}] Exception during BI: {e}")
            with self.results_lock:
                self.results['insights']['failed'] += 1

        processing_time = time.time() - video_start_time
        with self.results_lock:
            self.results['videos_processed'] += 1
            self.results['processing_times'].append(processing_time)
            # Keep only last 20 times for rolling average
            if len(self.results['processing_times']) > 20:
                self.results['processing_times'] = self.results['processing_times'][-20:]

        return True, processing_time

    def batch_extract(self, video_ids: list, skip_existing: bool = True, max_workers: int = 10,
                     checkpoint_interval: int = 10):
        """
        Extract transcripts and business intelligence for multiple videos

        Args:
            video_ids: List of YouTube video IDs
            skip_existing: Skip videos with existing insights
            max_workers: Number of parallel workers (1-15)
            checkpoint_interval: Save checkpoint every N videos
        """
        self.start_time = time.time()
        self.results['start_time'] = datetime.now().isoformat()
        self.results['current_batch_start'] = datetime.now().isoformat()

        # Check for resume
        checkpoint = self.load_checkpoint()
        if checkpoint and checkpoint.get('remaining_videos'):
            print(f"\n🔄 Found checkpoint from {checkpoint.get('timestamp')}")
            print(f"   Resuming from {len(checkpoint['remaining_videos'])} remaining videos")
            response = input("Resume from checkpoint? (y/n): ")
            if response.lower() == 'y':
                video_ids = checkpoint['remaining_videos']
                self.results = checkpoint['results']

        total_videos = len(video_ids)

        print(f"\n{'='*80}")
        print(f"🚀 ENHANCED BATCH VIDEO EXTRACTION")
        print(f"{'='*80}\n")
        print(f"Total videos: {total_videos}")
        print(f"Parallel workers: {max_workers}")
        print(f"Skip existing: {skip_existing}")
        print(f"Checkpoint interval: every {checkpoint_interval} videos")
        print(f"Expected cost: ${total_videos * 0.0242:.2f} (Browserbase)")
        print(f"Expected time: ~{total_videos * 235 / max_workers / 60:.1f} minutes")
        print(f"\n{'='*80}\n")

        processed_count = 0

        # Process in batches for checkpointing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for i, video_id in enumerate(video_ids, 1):
                future = executor.submit(
                    self.process_single_video,
                    video_id, i, total_videos, skip_existing
                )
                futures[future] = (video_id, i)

            # Process completions
            for future in as_completed(futures):
                video_id, index = futures[future]
                processed_count += 1

                try:
                    success, proc_time = future.result()
                except Exception as e:
                    print(f"❌ Unexpected error processing {video_id}: {e}")
                    with self.results_lock:
                        self.results['failed_videos'].append(video_id)

                # Checkpoint every N videos
                if processed_count % checkpoint_interval == 0:
                    remaining = [vid for vid in video_ids[processed_count:]]
                    self.save_checkpoint(remaining)
                    print(f"\n💾 Checkpoint saved ({processed_count}/{total_videos})\n")

        # Final results
        total_time = time.time() - self.start_time
        self.print_final_report(total_videos, total_time)

        # Save failed videos for retry
        self.save_failed_videos()

        # Clean up checkpoint
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

        return self.results

    def print_final_report(self, total_videos: int, total_time: float):
        """Print comprehensive final report"""
        print(f"\n{'='*80}")
        print(f"✅ BATCH EXTRACTION COMPLETE")
        print(f"{'='*80}\n")

        print(f"📊 FINAL RESULTS:\n")
        print(f"Total videos: {total_videos}")
        print(f"Time elapsed: {timedelta(seconds=int(total_time))}")
        print(f"Average per video: {total_time / total_videos:.1f}s")

        print(f"\n📹 Transcripts:")
        print(f"  ✅ Success: {self.results['transcripts']['success']}")
        print(f"  ⚡ Skipped: {self.results['transcripts']['skipped']}")
        print(f"  ❌ Failed: {self.results['transcripts']['failed']}")

        success_rate = (self.results['transcripts']['success'] / total_videos * 100) if total_videos > 0 else 0
        print(f"  Success rate: {success_rate:.1f}%")

        print(f"\n🧠 Business Intelligence:")
        print(f"  ✅ Success: {self.results['insights']['success']}")
        print(f"  ⚡ Skipped: {self.results['insights']['skipped']}")
        print(f"  ❌ Failed: {self.results['insights']['failed']}")

        print(f"\n💬 Comments:")
        print(f"  Total extracted: {self.results['comments_extracted']}")
        avg_comments = self.results['comments_extracted'] / max(self.results['transcripts']['success'], 1)
        print(f"  Average per video: {avg_comments:.1f}")

        print(f"\n💰 Costs:")
        browserbase_cost = self.results['transcripts']['success'] * 0.0242
        print(f"  Browserbase: ${browserbase_cost:.2f}")
        print(f"  Claude Sonnet 4: $0.00 (included in subscription)")
        print(f"  Total: ${browserbase_cost:.2f}")

        if self.results['failed_videos']:
            print(f"\n⚠️  Failed Videos ({len(self.results['failed_videos'])}):")
            for vid in self.results['failed_videos'][:10]:
                print(f"  - {vid}")
            if len(self.results['failed_videos']) > 10:
                print(f"  ... and {len(self.results['failed_videos']) - 10} more")
            print(f"\n  Failed videos saved to: {self.failed_videos_file}")

        print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description='Enhanced batch video extraction for YouTube videos')
    parser.add_argument('video_ids', nargs='*', help='YouTube video IDs to process')
    parser.add_argument('--file', '-f', help='File containing video IDs (one per line)')
    parser.add_argument('--workers', '-w', type=int, default=10,
                       help='Number of parallel workers (default: 10)')
    parser.add_argument('--skip-existing', '-s', action='store_true', default=True,
                       help='Skip videos with existing insights (default: True)')
    parser.add_argument('--no-skip', action='store_true',
                       help='Process all videos even if insights exist')
    parser.add_argument('--checkpoint-interval', '-c', type=int, default=10,
                       help='Save checkpoint every N videos (default: 10)')

    args = parser.parse_args()

    # Get video IDs
    video_ids = []

    if args.file:
        # Read from file
        with open(args.file, 'r') as f:
            video_ids = [line.strip() for line in f if line.strip()]
    elif args.video_ids:
        # From command line
        video_ids = args.video_ids
    else:
        print("Error: No video IDs provided")
        print("\nUsage:")
        print("  python3 batch_extract_videos_enhanced.py VIDEO_ID1 VIDEO_ID2 ...")
        print("  python3 batch_extract_videos_enhanced.py --file videos.txt --workers 10")
        print("\nOptions:")
        print("  --workers, -w N      Number of parallel workers (default: 10)")
        print("  --skip-existing, -s  Skip videos with existing insights (default: True)")
        print("  --no-skip           Process all videos even if insights exist")
        parser.print_help()
        sys.exit(1)

    skip_existing = not args.no_skip

    print(f"\n🎬 Loaded {len(video_ids)} videos for processing")

    # Create extractor and run
    extractor = EnhancedBatchExtractor()
    results = extractor.batch_extract(
        video_ids,
        skip_existing=skip_existing,
        max_workers=args.workers,
        checkpoint_interval=args.checkpoint_interval
    )

    # Save results
    results_file = Path("/Users/yourox/AI-Workspace/data/batch_extraction_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"📊 Results saved to: {results_file}\n")


if __name__ == "__main__":
    main()
