#!/usr/bin/env python3
"""
Check enrichment coverage for all videos
Identifies which videos have complete enrichment data
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Directories
INSIGHTS_DIR = Path("/Users/yourox/AI-Workspace/data/business_insights")
ENRICHED_DIR = Path("/Users/yourox/AI-Workspace/data/enriched_insights")
SUMMARIES_DIR = Path("/Users/yourox/AI-Workspace/data/video_summaries")
META_FILE = Path("/Users/yourox/AI-Workspace/data/meta_intelligence/meta_intelligence_report.json")

def get_video_ids_from_insights():
    """Get all video IDs that have insight files"""
    video_ids = set()
    for file_path in INSIGHTS_DIR.glob("*_insights.json"):
        video_id = file_path.stem.replace('_insights', '')
        video_ids.add(video_id)
    return video_ids

def get_video_ids_from_enriched():
    """Get all video IDs that have enriched files"""
    video_ids = set()
    for file_path in ENRICHED_DIR.glob("*_enriched.json"):
        video_id = file_path.stem.replace('_enriched', '')
        video_ids.add(video_id)
    return video_ids

def get_video_ids_from_summaries():
    """Get all video IDs that have summary files"""
    video_ids = set()
    for file_path in SUMMARIES_DIR.glob("*_summary.json"):
        video_id = file_path.stem.replace('_summary', '')
        video_ids.add(video_id)
    return video_ids

def get_video_metadata(video_id):
    """Get metadata for a video"""
    insight_file = INSIGHTS_DIR / f"{video_id}_insights.json"

    if not insight_file.exists():
        return None

    try:
        with open(insight_file, 'r') as f:
            data = json.load(f)
            meta = data.get('meta', {})
            return {
                'title': meta.get('title', 'Unknown'),
                'channel': meta.get('channel_title', 'Unknown'),
                'created': meta.get('created_at', 'Unknown')
            }
    except:
        return None

def check_enrichment_quality(video_id):
    """Check the quality of enrichment for a video"""
    enriched_file = ENRICHED_DIR / f"{video_id}_enriched.json"
    summary_file = SUMMARIES_DIR / f"{video_id}_summary.json"

    quality = {
        'has_enriched': enriched_file.exists(),
        'has_summary': summary_file.exists(),
        'enriched_version': None,
        'enriched_at': None,
        'high_value_insights': 0,
        'avg_actionability': 0,
        'total_insights': 0,
        'opportunity_count': 0
    }

    # Check enriched file
    if enriched_file.exists():
        try:
            with open(enriched_file, 'r') as f:
                data = json.load(f)
                quality['enriched_version'] = data.get('_version')
                quality['enriched_at'] = data.get('_computed_at')

                metrics = data.get('video_level_metrics', {})
                quality['high_value_insights'] = metrics.get('high_value_insights', 0)
                quality['avg_actionability'] = metrics.get('avg_actionability_score', 0)
                quality['total_insights'] = metrics.get('total_insights', 0)
        except:
            pass

    # Check summary file
    if summary_file.exists():
        try:
            with open(summary_file, 'r') as f:
                data = json.load(f)
                opp_map = data.get('opportunity_map', {})
                quality['opportunity_count'] = opp_map.get('total_opportunities', 0)
        except:
            pass

    return quality

def main():
    print("=" * 80)
    print("🔍 ENRICHMENT COVERAGE ANALYSIS")
    print("=" * 80)

    # Get all video IDs
    insight_ids = get_video_ids_from_insights()
    enriched_ids = get_video_ids_from_enriched()
    summary_ids = get_video_ids_from_summaries()

    print(f"\n📊 File Counts:")
    print(f"   Insight files: {len(insight_ids)}")
    print(f"   Enriched files: {len(enriched_ids)}")
    print(f"   Summary files: {len(summary_ids)}")

    # Find gaps
    missing_enriched = insight_ids - enriched_ids
    missing_summaries = insight_ids - summary_ids

    print(f"\n📊 Coverage:")
    print(f"   ✅ Complete enrichment: {len(enriched_ids)} / {len(insight_ids)} videos")
    print(f"   ✅ Complete summaries: {len(summary_ids)} / {len(insight_ids)} videos")

    if missing_enriched:
        print(f"\n⚠️  Videos Missing Enrichment ({len(missing_enriched)}):")
        for video_id in sorted(missing_enriched):
            meta = get_video_metadata(video_id)
            if meta:
                print(f"   - {video_id}: {meta['title'][:60]}")
    else:
        print(f"\n✅ All videos have enrichment!")

    if missing_summaries:
        print(f"\n⚠️  Videos Missing Summaries ({len(missing_summaries)}):")
        for video_id in sorted(missing_summaries):
            meta = get_video_metadata(video_id)
            if meta:
                print(f"   - {video_id}: {meta['title'][:60]}")
    else:
        print(f"\n✅ All videos have summaries!")

    # Check meta-intelligence coverage
    print(f"\n📊 Meta-Intelligence Coverage:")
    if META_FILE.exists():
        try:
            with open(META_FILE, 'r') as f:
                meta_data = json.load(f)
                print(f"   ✅ Meta-intelligence report exists")
                print(f"   Videos analyzed: {meta_data.get('data_scope', {}).get('total_videos', 0)}")
                print(f"   Total insights: {meta_data.get('data_scope', {}).get('total_insights', 0)}")

                # Check trends
                trends = meta_data.get('cross_video_trends', {})
                print(f"   Unique trends: {trends.get('total_unique_trends', 0)}")

                # Check products
                products = meta_data.get('product_ecosystem', {})
                print(f"   Unique products: {products.get('total_unique_products', 0)}")

                # Check opportunities
                opportunities = meta_data.get('opportunity_matrix', {})
                print(f"   Total opportunities: {opportunities.get('total_opportunities', 0)}")
        except Exception as e:
            print(f"   ❌ Error reading meta-intelligence: {e}")
    else:
        print(f"   ❌ Meta-intelligence report not found!")

    # Quality analysis
    print(f"\n📊 Enrichment Quality Analysis:")
    print(f"\n{'Video ID':<15} {'Title':<40} {'Insights':<10} {'HV':<5} {'Action':<7} {'Opps':<6}")
    print("-" * 80)

    quality_stats = []

    for video_id in sorted(enriched_ids):
        meta = get_video_metadata(video_id)
        quality = check_enrichment_quality(video_id)

        if meta and quality['has_enriched']:
            title = meta['title'][:38]
            insights = quality['total_insights']
            hv = quality['high_value_insights']
            action = f"{quality['avg_actionability']:.1f}"
            opps = quality['opportunity_count']

            print(f"{video_id:<15} {title:<40} {insights:<10} {hv:<5} {action:<7} {opps:<6}")

            quality_stats.append({
                'video_id': video_id,
                'insights': insights,
                'high_value': hv,
                'actionability': quality['avg_actionability'],
                'opportunities': opps
            })

    # Summary statistics
    if quality_stats:
        print(f"\n📊 Quality Statistics:")
        total_insights = sum(s['insights'] for s in quality_stats)
        total_hv = sum(s['high_value'] for s in quality_stats)
        avg_action = sum(s['actionability'] for s in quality_stats) / len(quality_stats)
        total_opps = sum(s['opportunities'] for s in quality_stats)

        print(f"   Total insights: {total_insights}")
        print(f"   High-value insights: {total_hv} ({total_hv/total_insights*100:.1f}%)")
        print(f"   Average actionability: {avg_action:.1f}")
        print(f"   Total opportunities: {total_opps}")

        # Top videos by high-value insights
        top_hv = sorted(quality_stats, key=lambda x: x['high_value'], reverse=True)[:5]
        print(f"\n🏆 Top 5 Videos by High-Value Insights:")
        for i, video in enumerate(top_hv, 1):
            meta = get_video_metadata(video['video_id'])
            if meta:
                print(f"   {i}. {meta['title'][:60]}")
                print(f"      HV Insights: {video['high_value']}, Actionability: {video['actionability']:.1f}")

        # Top videos by opportunities
        top_opps = sorted(quality_stats, key=lambda x: x['opportunities'], reverse=True)[:5]
        print(f"\n🎯 Top 5 Videos by Opportunities:")
        for i, video in enumerate(top_opps, 1):
            meta = get_video_metadata(video['video_id'])
            if meta:
                print(f"   {i}. {meta['title'][:60]}")
                print(f"      Opportunities: {video['opportunities']}")

    # Check for recent files
    print(f"\n📅 Recent Enrichment Activity:")
    recent_files = []
    for file_path in ENRICHED_DIR.glob("*_enriched.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                computed_at = data.get('_computed_at')
                if computed_at:
                    recent_files.append((file_path.stem.replace('_enriched', ''), computed_at))
        except:
            pass

    recent_files.sort(key=lambda x: x[1], reverse=True)

    print(f"\n   Last 10 enriched videos:")
    for video_id, computed_at in recent_files[:10]:
        meta = get_video_metadata(video_id)
        if meta:
            print(f"   {computed_at[:19]} - {meta['title'][:50]}")

    # Final status
    print(f"\n{'=' * 80}")
    if not missing_enriched and not missing_summaries and META_FILE.exists():
        print(f"✅ COMPLETE: All videos have full enrichment coverage!")
    else:
        print(f"⚠️  INCOMPLETE: Some videos are missing enrichment data")
        if missing_enriched:
            print(f"   - {len(missing_enriched)} videos need enrichment")
        if missing_summaries:
            print(f"   - {len(missing_summaries)} videos need summaries")
        if not META_FILE.exists():
            print(f"   - Meta-intelligence report missing")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    main()
