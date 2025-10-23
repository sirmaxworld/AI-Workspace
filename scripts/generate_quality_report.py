#!/usr/bin/env python3
"""Generate comprehensive quality report for all tiers"""

import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def analyze_transcripts():
    """Analyze all transcript files"""
    transcripts_dir = Path("/Users/yourox/AI-Workspace/data/transcripts")
    transcript_files = list(transcripts_dir.glob("*_full.json"))

    stats = {
        'total_transcripts': len(transcript_files),
        'by_method': defaultdict(int),
        'total_segments': 0,
        'total_comments': 0,
        'avg_segments': 0,
        'avg_comments': 0,
        'enriched_with_api': 0,
        'with_metadata': 0,
        'videos_by_channel': defaultdict(int),
        'segment_distribution': {'<500': 0, '500-1000': 0, '1000-2000': 0, '>2000': 0}
    }

    for transcript_file in transcript_files:
        try:
            with open(transcript_file) as f:
                data = json.load(f)

            # Count segments
            segment_count = data.get('transcript', {}).get('segment_count', 0)
            stats['total_segments'] += segment_count

            # Segment distribution
            if segment_count < 500:
                stats['segment_distribution']['<500'] += 1
            elif segment_count < 1000:
                stats['segment_distribution']['500-1000'] += 1
            elif segment_count < 2000:
                stats['segment_distribution']['1000-2000'] += 1
            else:
                stats['segment_distribution']['>2000'] += 1

            # Count comments
            comments = data.get('comments', [])
            stats['total_comments'] += len(comments)

            # Method tracking
            method = data.get('method', 'unknown')
            stats['by_method'][method] += 1

            # API enrichment
            if data.get('extraction_method') == 'youtube_api_v3':
                stats['enriched_with_api'] += 1

            # Metadata
            if data.get('metadata'):
                stats['with_metadata'] += 1
                channel = data['metadata'].get('channel_title', 'unknown')
                stats['videos_by_channel'][channel] += 1

        except Exception as e:
            print(f"Error reading {transcript_file.name}: {e}")
            continue

    if stats['total_transcripts'] > 0:
        stats['avg_segments'] = stats['total_segments'] // stats['total_transcripts']
        stats['avg_comments'] = stats['total_comments'] // stats['total_transcripts']

    return stats

def analyze_insights():
    """Analyze business insights"""
    insights_dir = Path("/Users/yourox/AI-Workspace/data/business_insights")
    insight_files = list(insights_dir.glob("*_insights.json"))

    stats = {
        'total_insights': len(insight_files),
        'by_category': defaultdict(int),
        'total_items': 0,
        'avg_items_per_video': 0
    }

    for insight_file in insight_files:
        try:
            with open(insight_file) as f:
                data = json.load(f)

            # Count items in each category
            for category, items in data.items():
                if category not in ['video_id', 'extraction_date']:
                    if items:
                        stats['by_category'][category] += len(items)
                        stats['total_items'] += len(items)

        except Exception as e:
            print(f"Error reading {insight_file.name}: {e}")
            continue

    if stats['total_insights'] > 0:
        stats['avg_items_per_video'] = stats['total_items'] // stats['total_insights']

    return stats

def analyze_tier_performance():
    """Analyze performance by tier"""

    # Load tier video lists
    tier1_file = Path("/tmp/tier1_videos.txt")
    tier2_3_file = Path("/tmp/tier2_3_videos.txt")
    transcripts_dir = Path("/Users/yourox/AI-Workspace/data/transcripts")

    tier_stats = {}

    if tier1_file.exists():
        with open(tier1_file) as f:
            tier1_videos = set(line.strip() for line in f if line.strip())

        # Check which ones have transcripts
        tier1_extracted = sum(1 for vid in tier1_videos
                             if (transcripts_dir / f"{vid}_full.json").exists())

        tier_stats['tier1'] = {
            'target': len(tier1_videos),
            'extracted': tier1_extracted,
            'success_rate': f"{tier1_extracted/len(tier1_videos)*100:.1f}%"
        }

    if tier2_3_file.exists():
        with open(tier2_3_file) as f:
            tier2_3_videos = set(line.strip() for line in f if line.strip())

        tier2_3_extracted = sum(1 for vid in tier2_3_videos
                               if (transcripts_dir / f"{vid}_full.json").exists())

        tier_stats['tier2_3'] = {
            'target': len(tier2_3_videos),
            'extracted': tier2_3_extracted,
            'success_rate': f"{tier2_3_extracted/len(tier2_3_videos)*100:.1f}%",
            'failed': len(tier2_3_videos) - tier2_3_extracted
        }

    return tier_stats

def main():
    print("📊 Generating Comprehensive Quality Report...\n")

    # Analyze transcripts
    print("1️⃣  Analyzing transcripts...")
    transcript_stats = analyze_transcripts()

    # Analyze insights
    print("2️⃣  Analyzing business insights...")
    insight_stats = analyze_insights()

    # Analyze tier performance
    print("3️⃣  Analyzing tier performance...")
    tier_stats = analyze_tier_performance()

    # Build comprehensive report
    report = {
        'report_generated': datetime.now().isoformat(),
        'overall_summary': {
            'total_videos_extracted': transcript_stats['total_transcripts'],
            'total_segments': transcript_stats['total_segments'],
            'avg_segments_per_video': transcript_stats['avg_segments'],
            'total_comments': transcript_stats['total_comments'],
            'avg_comments_per_video': transcript_stats['avg_comments'],
            'videos_enriched_with_api': transcript_stats['enriched_with_api'],
            'videos_with_metadata': transcript_stats['with_metadata'],
            'business_insights_generated': insight_stats['total_insights'],
            'total_business_items': insight_stats['total_items'],
            'avg_business_items_per_video': insight_stats['avg_items_per_video']
        },
        'extraction_methods': dict(transcript_stats['by_method']),
        'segment_distribution': transcript_stats['segment_distribution'],
        'business_insights_by_category': dict(insight_stats['by_category']),
        'tier_performance': tier_stats,
        'top_channels': dict(sorted(
            transcript_stats['videos_by_channel'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
    }

    # Save report
    output_file = Path("/Users/yourox/AI-Workspace/data/comprehensive_quality_report.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Report saved to: {output_file}")

    # Print summary
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE QUALITY REPORT")
    print("="*70)
    print(f"\n📹 OVERALL SUMMARY:")
    print(f"   Total videos extracted: {report['overall_summary']['total_videos_extracted']}")
    print(f"   Total segments: {report['overall_summary']['total_segments']:,}")
    print(f"   Avg segments/video: {report['overall_summary']['avg_segments_per_video']}")
    print(f"   Total comments: {report['overall_summary']['total_comments']:,}")
    print(f"   Avg comments/video: {report['overall_summary']['avg_comments_per_video']}")
    print(f"   Videos enriched with API: {report['overall_summary']['videos_enriched_with_api']}")
    print(f"   Business insights generated: {report['overall_summary']['business_insights_generated']}")

    print(f"\n🎯 TIER PERFORMANCE:")
    for tier, stats in tier_stats.items():
        print(f"   {tier.upper()}: {stats['extracted']}/{stats['target']} ({stats['success_rate']})")
        if 'failed' in stats:
            print(f"      Failed: {stats['failed']}")

    print(f"\n🔧 EXTRACTION METHODS:")
    for method, count in report['extraction_methods'].items():
        print(f"   {method}: {count}")

    print(f"\n📊 SEGMENT DISTRIBUTION:")
    for range_label, count in report['segment_distribution'].items():
        print(f"   {range_label} segments: {count} videos")

    print(f"\n💡 BUSINESS INSIGHTS (Top 5):")
    top_insights = sorted(report['business_insights_by_category'].items(),
                         key=lambda x: x[1], reverse=True)[:5]
    for category, count in top_insights:
        print(f"   {category}: {count} items")

    print("\n" + "="*70)

if __name__ == "__main__":
    main()
