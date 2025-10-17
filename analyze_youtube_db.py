#!/usr/bin/env python3
"""Analyze YouTube database status and processing efficiency"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Define paths
BASE_PATH = Path('/Users/yourox/AI-Workspace')
TRANSCRIPTS_PATH = BASE_PATH / 'data' / 'transcripts'
INSIGHTS_PATH = BASE_PATH / 'data' / 'insights'
REPORTS_PATH = BASE_PATH / 'data' / 'qc_reports'

def analyze_transcripts():
    """Analyze transcript files"""
    stats = {
        'total_videos': 0,
        'by_channel': defaultdict(int),
        'by_date': defaultdict(int),
        'recent_additions': [],
        'file_sizes': [],
        'processing_methods': defaultdict(int)
    }

    if not TRANSCRIPTS_PATH.exists():
        return stats

    # Get all transcript files
    transcript_files = list(TRANSCRIPTS_PATH.glob('*.json'))
    stats['total_videos'] = len(transcript_files)

    # Analyze each transcript
    for file_path in transcript_files:
        try:
            # Get file stats
            file_stat = file_path.stat()
            file_size_mb = file_stat.st_size / (1024 * 1024)
            stats['file_sizes'].append(file_size_mb)

            # Get creation time
            creation_time = datetime.fromtimestamp(file_stat.st_mtime)
            date_key = creation_time.strftime('%Y-%m-%d')
            stats['by_date'][date_key] += 1

            # Check if recent (last 7 days)
            if creation_time > datetime.now() - timedelta(days=7):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    stats['recent_additions'].append({
                        'video_id': metadata.get('video_id', file_path.stem),
                        'title': metadata.get('title', 'Unknown'),
                        'channel': metadata.get('channel', 'Unknown'),
                        'added': creation_time.strftime('%Y-%m-%d %H:%M'),
                        'duration': metadata.get('duration_formatted', 'N/A')
                    })

                    # Track channel
                    channel = metadata.get('channel', 'Unknown')
                    stats['by_channel'][channel] += 1

                    # Track processing method
                    method = data.get('method', 'unknown')
                    stats['processing_methods'][method] += 1

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue

    return stats

def analyze_insights():
    """Analyze insight files"""
    stats = {
        'total_insights': 0,
        'by_type': defaultdict(int),
        'recent_insights': []
    }

    if not INSIGHTS_PATH.exists():
        return stats

    insight_files = list(INSIGHTS_PATH.glob('*_insights.json'))
    stats['total_insights'] = len(insight_files)

    for file_path in insight_files:
        try:
            file_stat = file_path.stat()
            creation_time = datetime.fromtimestamp(file_stat.st_mtime)

            if creation_time > datetime.now() - timedelta(days=7):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stats['recent_insights'].append({
                        'video_id': file_path.stem.replace('_insights', ''),
                        'added': creation_time.strftime('%Y-%m-%d %H:%M'),
                        'key_topics': len(data.get('key_topics', [])),
                        'summary_length': len(data.get('summary', ''))
                    })
        except:
            continue

    return stats

def analyze_qc_reports():
    """Analyze quality control reports"""
    stats = {
        'total_reports': 0,
        'recent_runs': [],
        'quality_distribution': defaultdict(int),
        'pass_rates': []
    }

    if not REPORTS_PATH.exists():
        return stats

    report_files = list(REPORTS_PATH.glob('*.json'))
    stats['total_reports'] = len(report_files)

    for file_path in sorted(report_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                report = json.load(f)

                pipeline_run = report.get('pipeline_run', {})
                extraction = report.get('extraction_summary', {})
                qc = report.get('quality_control', {})

                stats['recent_runs'].append({
                    'channel': pipeline_run.get('channel', 'Unknown'),
                    'date': pipeline_run.get('started_at', '')[:10],
                    'duration': pipeline_run.get('duration_formatted', 'N/A'),
                    'videos_processed': extraction.get('transcribed_successfully', 0),
                    'success_rate': extraction.get('success_rate', 'N/A'),
                    'qc_pass_rate': qc.get('qc_pass_rate', 'N/A')
                })

                # Track quality distribution
                dist = qc.get('quality_distribution', {})
                for quality, count in dist.items():
                    stats['quality_distribution'][quality] += count

                # Track pass rates
                if qc.get('qc_pass_rate', 'N/A') != 'N/A':
                    rate = float(qc['qc_pass_rate'].rstrip('%'))
                    stats['pass_rates'].append(rate)

        except Exception as e:
            print(f"Error processing report {file_path.name}: {e}")
            continue

    return stats

def calculate_efficiency_metrics(transcript_stats, insight_stats, qc_stats):
    """Calculate processing efficiency metrics"""
    metrics = {}

    # Video processing rate (last 7 days)
    recent_dates = sorted(transcript_stats['by_date'].keys())[-7:]
    recent_count = sum(transcript_stats['by_date'][d] for d in recent_dates if d in transcript_stats['by_date'])
    metrics['daily_average'] = recent_count / 7 if recent_count > 0 else 0

    # File size efficiency
    if transcript_stats['file_sizes']:
        metrics['avg_file_size_mb'] = sum(transcript_stats['file_sizes']) / len(transcript_stats['file_sizes'])
        metrics['total_storage_mb'] = sum(transcript_stats['file_sizes'])

    # Processing method distribution
    metrics['processing_methods'] = dict(transcript_stats['processing_methods'])

    # Quality metrics
    if qc_stats['pass_rates']:
        metrics['avg_qc_pass_rate'] = sum(qc_stats['pass_rates']) / len(qc_stats['pass_rates'])

    # Insight generation rate
    if transcript_stats['total_videos'] > 0:
        metrics['insight_coverage'] = (insight_stats['total_insights'] / transcript_stats['total_videos']) * 100

    return metrics

def print_report(transcript_stats, insight_stats, qc_stats, metrics):
    """Print formatted report"""
    print("\n" + "="*80)
    print("📊 YOUTUBE DATABASE STATUS REPORT")
    print("="*80)

    # Overall statistics
    print(f"\n📺 VIDEO STATISTICS:")
    print(f"  Total Videos in Database: {transcript_stats['total_videos']}")
    print(f"  Total Insights Generated: {insight_stats['total_insights']}")
    print(f"  Insight Coverage: {metrics.get('insight_coverage', 0):.1f}%")

    # Channel distribution
    print(f"\n📻 TOP CHANNELS:")
    for channel, count in sorted(transcript_stats['by_channel'].items(),
                                 key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {channel}: {count} videos")

    # Recent additions
    print(f"\n🆕 RECENT ADDITIONS (Last 7 Days):")
    if transcript_stats['recent_additions']:
        for video in transcript_stats['recent_additions'][:5]:
            print(f"  [{video['added']}] {video['title'][:50]}...")
            print(f"    Channel: {video['channel']} | Duration: {video['duration']}")
    else:
        print("  No videos added in the last 7 days")

    # Processing efficiency
    print(f"\n⚡ PROCESSING EFFICIENCY:")
    print(f"  Daily Average (7 days): {metrics.get('daily_average', 0):.1f} videos/day")
    print(f"  Average File Size: {metrics.get('avg_file_size_mb', 0):.2f} MB")
    print(f"  Total Storage Used: {metrics.get('total_storage_mb', 0):.1f} MB")

    if metrics.get('processing_methods'):
        print(f"\n  Processing Methods Used:")
        for method, count in metrics['processing_methods'].items():
            percentage = (count / transcript_stats['total_videos']) * 100
            print(f"    • {method}: {count} ({percentage:.1f}%)")

    # Quality control
    if qc_stats['recent_runs']:
        print(f"\n🔍 QUALITY CONTROL:")
        print(f"  Average QC Pass Rate: {metrics.get('avg_qc_pass_rate', 0):.1f}%")
        print(f"\n  Recent Pipeline Runs:")
        for run in qc_stats['recent_runs'][:3]:
            print(f"    [{run['date']}] {run['channel']}")
            print(f"      Videos: {run['videos_processed']} | Success: {run['success_rate']} | QC Pass: {run['qc_pass_rate']}")

        if qc_stats['quality_distribution']:
            print(f"\n  Overall Quality Distribution:")
            total_qc = sum(qc_stats['quality_distribution'].values())
            for quality in ['excellent', 'good', 'fair', 'poor']:
                count = qc_stats['quality_distribution'].get(quality, 0)
                percentage = (count / total_qc * 100) if total_qc > 0 else 0
                print(f"    • {quality.capitalize()}: {count} ({percentage:.1f}%)")

    # Processing trends
    print(f"\n📈 PROCESSING TRENDS (Last 7 Days):")
    recent_dates = sorted(transcript_stats['by_date'].keys())[-7:]
    for date in recent_dates:
        count = transcript_stats['by_date'].get(date, 0)
        bar = "█" * min(count, 50)
        print(f"  {date}: {bar} {count}")

    print("\n" + "="*80)
    print("✅ Report generated successfully!")
    print("="*80 + "\n")

def main():
    """Main analysis function"""
    print("\n🔄 Analyzing YouTube database...")

    # Gather statistics
    transcript_stats = analyze_transcripts()
    insight_stats = analyze_insights()
    qc_stats = analyze_qc_reports()

    # Calculate efficiency metrics
    metrics = calculate_efficiency_metrics(transcript_stats, insight_stats, qc_stats)

    # Print report
    print_report(transcript_stats, insight_stats, qc_stats, metrics)

    return {
        'transcripts': transcript_stats,
        'insights': insight_stats,
        'qc': qc_stats,
        'metrics': metrics
    }

if __name__ == "__main__":
    results = main()