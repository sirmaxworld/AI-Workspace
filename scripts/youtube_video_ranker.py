#!/usr/bin/env python3
"""
YouTube Video Ranker & Prioritizer
Ranks videos by multiple criteria for optimal transcript extraction
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class YouTubeVideoRanker:
    """Rank and prioritize videos for transcript extraction"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.channels_dir = self.workspace_dir / "data" / "youtube_channels"

    def load_channel_videos(self, channel_file: Path) -> List[Dict]:
        """Load videos from channel JSON"""
        with open(channel_file, 'r') as f:
            data = json.load(f)
        return data.get('videos', [])

    def calculate_priority_score(self, video: Dict) -> float:
        """
        Calculate priority score for a video based on:
        - View count (40%)
        - Recency (30%)
        - Duration (20% - longer videos = more insights)
        - Engagement (10% - likes/views ratio)
        """
        score = 0

        # View count (normalized 0-100)
        view_count = video.get('view_count', 0)
        if view_count > 0:
            # Log scale for views (10K = 40, 100K = 60, 1M = 80, 10M+ = 100)
            import math
            view_score = min(100, math.log10(view_count) * 15)
            score += view_score * 0.4

        # Recency (0-100, newest = 100)
        upload_date_str = video.get('upload_date', '')
        if upload_date_str:
            try:
                upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
                days_old = (datetime.now() - upload_date).days
                # Recent videos score higher (0-365 days mapped to 0-100)
                recency_score = max(0, 100 - (days_old / 3.65))
                score += recency_score * 0.3
            except:
                pass

        # Duration (10-60 min optimal, 0-100)
        duration = video.get('duration', 0)
        if duration > 0:
            duration_min = duration / 60
            if 10 <= duration_min <= 60:
                duration_score = 100
            elif duration_min < 10:
                duration_score = (duration_min / 10) * 100
            else:  # > 60 min
                duration_score = max(50, 100 - (duration_min - 60))
            score += duration_score * 0.2

        # Engagement (likes/views ratio, 0-100)
        like_count = video.get('like_count', 0)
        if view_count > 0 and like_count > 0:
            engagement_ratio = (like_count / view_count) * 100
            # Typical good engagement is 2-5%
            engagement_score = min(100, engagement_ratio * 20)
            score += engagement_score * 0.1

        return round(score, 2)

    def rank_videos(
        self,
        videos: List[Dict],
        top_n: int = None
    ) -> List[Dict]:
        """
        Rank videos by priority score

        Args:
            videos: List of video dicts
            top_n: Return only top N videos (None = all)

        Returns:
            Sorted list of videos with priority scores
        """
        # Add priority score to each video
        for video in videos:
            video['priority_score'] = self.calculate_priority_score(video)

        # Sort by priority score (descending)
        ranked = sorted(videos, key=lambda v: v['priority_score'], reverse=True)

        if top_n:
            ranked = ranked[:top_n]

        return ranked

    def get_top_by_views(self, videos: List[Dict], top_n: int = 50) -> List[Dict]:
        """Get top N videos by view count"""
        sorted_videos = sorted(
            videos,
            key=lambda v: v.get('view_count', 0),
            reverse=True
        )
        return sorted_videos[:top_n]

    def merge_video_lists(self, *video_lists) -> List[Dict]:
        """Merge multiple video lists, removing duplicates by ID"""
        seen_ids = set()
        merged = []

        for video_list in video_lists:
            for video in video_list:
                video_id = video.get('id')
                if video_id and video_id not in seen_ids:
                    seen_ids.add(video_id)
                    merged.append(video)

        return merged

    def generate_channel_summary(
        self,
        channel_name: str,
        videos: List[Dict],
        ranked_videos: List[Dict]
    ) -> Dict:
        """Generate summary statistics for a channel"""

        total_duration = sum(v.get('duration', 0) for v in videos)
        total_views = sum(v.get('view_count', 0) for v in videos)
        total_likes = sum(v.get('like_count', 0) for v in videos)

        return {
            "channel": channel_name,
            "total_videos": len(videos),
            "selected_videos": len(ranked_videos),
            "total_duration_hours": round(total_duration / 3600, 1),
            "avg_duration_minutes": round(total_duration / len(videos) / 60, 1) if videos else 0,
            "total_views": total_views,
            "avg_views": total_views // len(videos) if videos else 0,
            "total_likes": total_likes,
            "engagement_rate": round((total_likes / total_views * 100), 3) if total_views > 0 else 0,
            "top_video": ranked_videos[0] if ranked_videos else None,
            "avg_priority_score": round(
                sum(v.get('priority_score', 0) for v in ranked_videos) / len(ranked_videos), 2
            ) if ranked_videos else 0
        }

    def process_channel(
        self,
        channel_file: Path,
        latest_n: int = 100,
        top_n: int = 50
    ) -> Dict:
        """
        Process a channel file and rank videos

        Args:
            channel_file: Path to channel JSON
            latest_n: Keep this many latest videos
            top_n: Add this many top by views

        Returns:
            Dict with ranked videos and summary
        """
        print(f"\n{'='*70}")
        print(f"Processing: {channel_file.name}")
        print(f"{'='*70}")

        videos = self.load_channel_videos(channel_file)
        channel_name = videos[0].get('channel', 'Unknown') if videos else 'Unknown'

        print(f"Channel: {channel_name}")
        print(f"Total videos found: {len(videos)}\n")

        # Get latest N videos (already sorted by date in extractor)
        latest_videos = videos[:latest_n]
        print(f"Latest {latest_n} videos selected")

        # Get top N by views
        top_viewed = self.get_top_by_views(videos, top_n)
        print(f"Top {top_n} by views selected")

        # Merge and remove duplicates
        merged = self.merge_video_lists(latest_videos, top_viewed)
        print(f"After merging: {len(merged)} unique videos\n")

        # Rank by priority score
        ranked = self.rank_videos(merged)

        # Generate summary
        summary = self.generate_channel_summary(channel_name, videos, ranked)

        print(f"Summary:")
        print(f"  Selected: {summary['selected_videos']} videos")
        print(f"  Total duration: {summary['total_duration_hours']}h")
        print(f"  Avg duration: {summary['avg_duration_minutes']}m")
        print(f"  Avg priority score: {summary['avg_priority_score']}")
        print(f"  Top video: {summary['top_video']['title'] if summary['top_video'] else 'N/A'}")

        return {
            "channel": channel_name,
            "videos": ranked,
            "summary": summary
        }

    def save_ranked_videos(self, channel_name: str, result: Dict):
        """Save ranked videos to output file"""
        output_file = self.channels_dir / f"{channel_name.lower().replace(' ', '_')}_ranked.json"

        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n💾 Saved to: {output_file}")
        return output_file


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Rank YouTube videos by priority')
    parser.add_argument('channel_files', nargs='+', help='Channel JSON files to process')
    parser.add_argument('--latest', type=int, default=100, help='Number of latest videos')
    parser.add_argument('--top', type=int, default=50, help='Number of top videos by views')
    parser.add_argument('--output-combined', help='Output file for combined ranking')

    args = parser.parse_args()

    ranker = YouTubeVideoRanker()

    all_results = []

    for channel_file in args.channel_files:
        file_path = Path(channel_file)

        if not file_path.exists():
            print(f"⚠️  File not found: {channel_file}")
            continue

        result = ranker.process_channel(file_path, args.latest, args.top)
        all_results.append(result)

        # Save individual channel ranking
        ranker.save_ranked_videos(result['channel'], result)

    # Generate combined summary
    if all_results:
        print(f"\n{'='*70}")
        print(f"📊 COMBINED SUMMARY")
        print(f"{'='*70}\n")

        total_channels = len(all_results)
        total_videos = sum(r['summary']['selected_videos'] for r in all_results)
        total_duration = sum(r['summary']['total_duration_hours'] for r in all_results)

        print(f"Channels processed: {total_channels}")
        print(f"Total videos selected: {total_videos}")
        print(f"Total content hours: {round(total_duration, 1)}h")
        print(f"Avg videos per channel: {total_videos // total_channels}")

        # Save combined if requested
        if args.output_combined:
            combined = {
                "generated_at": datetime.now().isoformat(),
                "total_channels": total_channels,
                "total_videos": total_videos,
                "total_duration_hours": round(total_duration, 1),
                "channels": all_results
            }

            output_path = Path(args.output_combined)
            with open(output_path, 'w') as f:
                json.dump(combined, f, indent=2)

            print(f"\n💾 Combined ranking saved to: {output_path}")


if __name__ == "__main__":
    main()
