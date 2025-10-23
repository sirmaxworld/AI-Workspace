#!/usr/bin/env python3
"""
Hybrid Batch Processor for Tier 2-3 Videos
Combines: Hybrid transcript extraction + YouTube API enrichment + Business Intelligence
"""

import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys
sys.path.insert(0, '/Users/yourox/AI-Workspace/scripts')

from hybrid_transcript_extractor import HybridTranscriptExtractor
from youtube_api_comment_extractor import YouTubeAPIExtractor
from business_intelligence_extractor import BusinessIntelligenceExtractor


class HybridBatchProcessor:
    """Complete pipeline: Hybrid transcript + API enrichment + BI insights"""

    def __init__(self):
        self.transcript_extractor = HybridTranscriptExtractor()
        self.api_extractor = YouTubeAPIExtractor()
        self.bi_extractor = BusinessIntelligenceExtractor()

        self.transcripts_dir = Path('/Users/yourox/AI-Workspace/data/transcripts')
        self.insights_dir = Path('/Users/yourox/AI-Workspace/data/business_insights')

        self.stats = {
            'transcripts': {'success': 0, 'failed': 0},
            'api_enrichment': {'success': 0, 'failed': 0},
            'insights': {'success': 0, 'failed': 0},
            'total_comments': 0,
            'failed_videos': []
        }

    def process_single_video(self, video_id: str, index: int, total: int) -> dict:
        """Process one video through complete pipeline"""

        start_time = time.time()
        print(f"\n{'='*70}")
        print(f"📹 VIDEO {index}/{total}: {video_id}")
        print(f"{'='*70}\n")

        transcript_file = self.transcripts_dir / f"{video_id}_full.json"
        insights_file = self.insights_dir / f"{video_id}_insights.json"

        # Check if already processed
        if insights_file.exists():
            print(f"⚡ Skipping {video_id} - already processed")
            return {'status': 'skipped', 'time': 0}

        # STEP 1: Extract transcript (hybrid: API → Browserbase)
        print(f"🎯 Step 1/3: Extracting transcript (hybrid API/Browserbase)...")
        transcript_result = self.transcript_extractor.extract_transcript(video_id)

        if transcript_result.get('status') != 'success':
            print(f"❌ Transcript extraction failed: {transcript_result.get('error')}")
            self.stats['transcripts']['failed'] += 1
            self.stats['failed_videos'].append(video_id)
            return {'status': 'failed', 'step': 'transcript', 'time': time.time() - start_time}

        self.transcript_extractor.save_transcript(video_id, transcript_result)
        self.stats['transcripts']['success'] += 1
        print(f"✅ Transcript extracted: {transcript_result.get('transcript', {}).get('segment_count', 0)} segments")

        # STEP 2: Enrich with YouTube API (metadata + comments)
        print(f"\n📊 Step 2/3: Enriching with YouTube API (metadata + comments)...")
        try:
            api_data = self.api_extractor.get_video_full_data(video_id, max_comments=100)

            if api_data.get('status') == 'success':
                # Merge API data into transcript
                with open(transcript_file) as f:
                    transcript_content = json.load(f)

                enriched = {
                    **transcript_content,
                    'title': api_data.get('title', transcript_content.get('title', '')),
                    'channel': api_data.get('channel', transcript_content.get('channel', '')),
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
                    'extraction_method': f"{transcript_result.get('method', 'hybrid')} + youtube_api_v3"
                }

                with open(transcript_file, 'w') as f:
                    json.dump(enriched, f, indent=2)

                comment_count = len(api_data.get('comments', []))
                self.stats['api_enrichment']['success'] += 1
                self.stats['total_comments'] += comment_count
                print(f"✅ API enrichment complete: {comment_count} comments + metadata")
            else:
                print(f"⚠️  API enrichment failed: {api_data.get('error')}")
                self.stats['api_enrichment']['failed'] += 1

        except Exception as e:
            print(f"⚠️  API enrichment exception: {e}")
            self.stats['api_enrichment']['failed'] += 1

        # STEP 3: Generate business intelligence insights
        print(f"\n🧠 Step 3/3: Generating business intelligence insights...")
        try:
            insights = self.bi_extractor.process_transcript(video_id)

            if insights and 'error' not in insights:
                self.stats['insights']['success'] += 1
                print(f"✅ Business intelligence generated")
            else:
                self.stats['insights']['failed'] += 1
                print(f"⚠️  BI generation failed")

        except Exception as e:
            print(f"⚠️  BI exception: {e}")
            self.stats['insights']['failed'] += 1

        elapsed = time.time() - start_time
        print(f"\n⏱️  Total time: {elapsed:.1f}s")

        return {'status': 'success', 'time': elapsed}

    def process_batch(self, video_ids: list, max_workers: int = 20):
        """Process batch of videos with parallel workers"""

        print(f"\n{'='*70}")
        print(f"🚀 HYBRID BATCH PROCESSOR - TIER 2-3")
        print(f"{'='*70}\n")
        print(f"Total videos: {len(video_ids)}")
        print(f"Workers: {max_workers}")
        print(f"Pipeline: Hybrid Transcript → API Enrichment → BI Insights\n")
        print(f"{'='*70}\n")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.process_single_video, vid, i, len(video_ids)): vid
                for i, vid in enumerate(video_ids, 1)
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    vid = futures[future]
                    print(f"❌ Exception processing {vid}: {e}")
                    self.stats['failed_videos'].append(vid)

        total_time = time.time() - start_time

        # Print final report
        self.print_report(len(video_ids), total_time)

        return self.stats

    def print_report(self, total_videos: int, total_time: float):
        """Print comprehensive final report"""

        print(f"\n{'='*70}")
        print(f"✅ BATCH PROCESSING COMPLETE")
        print(f"{'='*70}\n")

        print(f"📊 RESULTS:")
        print(f"  Total videos: {total_videos}")
        print(f"  Time: {total_time/60:.1f} minutes")
        print(f"  Avg per video: {total_time/total_videos:.1f}s\n")

        print(f"📹 Transcripts:")
        print(f"  ✅ Success: {self.stats['transcripts']['success']}")
        print(f"  ❌ Failed: {self.stats['transcripts']['failed']}")
        success_rate = self.stats['transcripts']['success'] / total_videos * 100
        print(f"  Success rate: {success_rate:.1f}%\n")

        print(f"📊 API Enrichment:")
        print(f"  ✅ Success: {self.stats['api_enrichment']['success']}")
        print(f"  ❌ Failed: {self.stats['api_enrichment']['failed']}")
        print(f"  💬 Total comments: {self.stats['total_comments']}")
        if self.stats['api_enrichment']['success'] > 0:
            avg_comments = self.stats['total_comments'] / self.stats['api_enrichment']['success']
            print(f"  Avg comments per video: {avg_comments:.1f}\n")

        print(f"🧠 Business Intelligence:")
        print(f"  ✅ Success: {self.stats['insights']['success']}")
        print(f"  ❌ Failed: {self.stats['insights']['failed']}\n")

        print(f"📈 Extraction Methods:")
        self.transcript_extractor.print_stats()

        if self.stats['failed_videos']:
            print(f"\n⚠️  Failed Videos ({len(self.stats['failed_videos'])}):")
            for vid in self.stats['failed_videos'][:10]:
                print(f"  - {vid}")
            if len(self.stats['failed_videos']) > 10:
                print(f"  ... and {len(self.stats['failed_videos']) - 10} more")

        print(f"\n{'='*70}\n")


if __name__ == "__main__":
    # Read video IDs from file
    video_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/tier2_3_videos.txt'
    max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    with open(video_file) as f:
        video_ids = [line.strip() for line in f if line.strip()]

    print(f"📁 Loaded {len(video_ids)} videos from {video_file}")

    processor = HybridBatchProcessor()
    stats = processor.process_batch(video_ids, max_workers=max_workers)

    # Save results
    results_file = Path('/Users/yourox/AI-Workspace/data/tier2_3_hybrid_results.json')
    with open(results_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"💾 Results saved to: {results_file}")
