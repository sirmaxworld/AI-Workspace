#!/usr/bin/env python3
"""
YouTube Database Statistics Analyzer
Provides comprehensive statistics on all transcripts
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
TRANSCRIPTS_DIR = Path('/Users/yourox/AI-Workspace/data/transcripts')
INSIGHTS_DIR = Path('/Users/yourox/AI-Workspace/data/insights')
QC_REPORTS_DIR = Path('/Users/yourox/AI-Workspace/data/qc_reports')

def analyze_youtube_database():
    """Comprehensive YouTube database analysis"""

    stats = {
        'total_videos': 0,
        'unique_videos': set(),
        'batch_files': 0,
        'batch_videos': 0,
        'individual_files': 0,
        'total_segments': 0,
        'total_duration': 0,
        'methods': defaultdict(int),
        'languages': defaultdict(int),
        'channels': defaultdict(int),
        'file_sizes_mb': [],
        'segments_per_video': [],
        'titles': [],
        'agent_ids': defaultdict(int)
    }

    # Analyze individual transcript files
    full_json_files = list(TRANSCRIPTS_DIR.glob('*_full.json'))
    stats['individual_files'] = len(full_json_files)

    for file_path in full_json_files:
        try:
            # Get file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            stats['file_sizes_mb'].append(file_size_mb)

            # Read and parse file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract video ID
            video_id = data.get('video_id', file_path.stem.replace('_full', ''))
            stats['unique_videos'].add(video_id)

            # Extract metadata
            title = data.get('title', 'Unknown')
            stats['titles'].append(title)

            # Method used
            method = data.get('method', 'unknown')
            stats['methods'][method] += 1

            # Agent ID
            agent_id = data.get('agent_id', 0)
            stats['agent_ids'][agent_id] += 1

            # Transcript data
            transcript = data.get('transcript', {})
            if isinstance(transcript, dict):
                segments = transcript.get('segments', [])
                language = transcript.get('language', 'en')
                stats['languages'][language] += 1
            else:
                segments = transcript if isinstance(transcript, list) else []

            num_segments = len(segments)
            stats['segments_per_video'].append(num_segments)
            stats['total_segments'] += num_segments

            # Calculate duration from segments
            if segments and len(segments) > 0:
                last_segment = segments[-1]
                total_duration = last_segment.get('start', 0) + last_segment.get('duration', 0)
                stats['total_duration'] += total_duration

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

    # Analyze batch files
    batch_files = list(TRANSCRIPTS_DIR.glob('batch_*.json'))
    stats['batch_files'] = len(batch_files)

    for file_path in batch_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                stats['batch_videos'] += len(data)
                for video in data:
                    video_id = video.get('video_id')
                    if video_id and video_id not in stats['unique_videos']:
                        stats['unique_videos'].add(video_id)
                        stats['total_videos'] += 1

        except Exception as e:
            print(f"Error processing batch {file_path.name}: {e}")

    # Convert set to count
    stats['total_videos'] = len(stats['unique_videos'])

    # Calculate averages
    if stats['file_sizes_mb']:
        stats['avg_file_size_mb'] = sum(stats['file_sizes_mb']) / len(stats['file_sizes_mb'])
        stats['total_storage_mb'] = sum(stats['file_sizes_mb'])

    if stats['segments_per_video']:
        stats['avg_segments_per_video'] = sum(stats['segments_per_video']) / len(stats['segments_per_video'])

    # Format duration
    if stats['total_duration'] > 0:
        hours = int(stats['total_duration'] // 3600)
        minutes = int((stats['total_duration'] % 3600) // 60)
        stats['total_duration_formatted'] = f"{hours}h {minutes}m"

    return stats


def print_statistics_report(stats):
    """Print formatted statistics report"""

    print("\n" + "="*80)
    print("📊 YOUTUBE DATABASE STATISTICS REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Overall Statistics
    print("📺 VIDEO STATISTICS:")
    print(f"  Total Unique Videos: {stats['total_videos']}")
    print(f"  Individual Files: {stats['individual_files']}")
    print(f"  Batch Files: {stats['batch_files']} (containing {stats['batch_videos']} videos)")
    print(f"  Total Segments: {stats['total_segments']:,}")
    print(f"  Avg Segments/Video: {stats.get('avg_segments_per_video', 0):.0f}")

    if 'total_duration_formatted' in stats:
        print(f"  Total Duration: {stats['total_duration_formatted']}")

    # Storage Statistics
    print(f"\n💾 STORAGE STATISTICS:")
    if 'total_storage_mb' in stats:
        print(f"  Total Storage: {stats['total_storage_mb']:.2f} MB")
        print(f"  Average File Size: {stats['avg_file_size_mb']:.2f} MB")
        print(f"  Storage Efficiency: {(stats['total_storage_mb'] / stats['total_videos']):.2f} MB/video")

    # Processing Methods
    print(f"\n⚙️ PROCESSING METHODS:")
    for method, count in stats['methods'].items():
        percentage = (count / stats['total_videos']) * 100
        print(f"  • {method}: {count} videos ({percentage:.1f}%)")

    # Language Distribution
    print(f"\n🌍 LANGUAGE DISTRIBUTION:")
    for lang, count in stats['languages'].items():
        percentage = (count / stats['total_videos']) * 100
        print(f"  • {lang}: {count} videos ({percentage:.1f}%)")

    # Agent Distribution
    print(f"\n🤖 AGENT DISTRIBUTION:")
    for agent_id, count in sorted(stats['agent_ids'].items()):
        percentage = (count / stats['total_videos']) * 100
        print(f"  • Agent {agent_id}: {count} videos ({percentage:.1f}%)")

    # Sample Titles
    print(f"\n📝 SAMPLE VIDEO TITLES (Latest 5):")
    for title in stats['titles'][-5:]:
        print(f"  • {title[:70]}...")

    # Summary
    print(f"\n" + "="*80)
    print("📈 SUMMARY:")
    print(f"  • {stats['total_videos']} unique videos processed")
    print(f"  • {stats['total_segments']:,} total transcript segments")
    if 'total_storage_mb' in stats:
        print(f"  • {stats['total_storage_mb']:.1f} MB total storage used")
    print(f"  • Primary method: {max(stats['methods'].items(), key=lambda x: x[1])[0] if stats['methods'] else 'N/A'}")
    print("="*80 + "\n")

    return stats


def main():
    """Main execution"""
    print("\n🔄 Analyzing YouTube Database...")

    # Perform analysis
    stats = analyze_youtube_database()

    # Print report
    print_statistics_report(stats)

    # Save report to JSON
    report_path = Path('/Users/yourox/AI-Workspace/youtube_stats.json')
    with open(report_path, 'w') as f:
        # Convert defaultdicts and sets to regular dicts/lists for JSON serialization
        json_stats = {
            k: dict(v) if isinstance(v, defaultdict) else
               list(v) if isinstance(v, set) else v
            for k, v in stats.items()
        }
        json.dump(json_stats, f, indent=2)

    print(f"📊 Detailed stats saved to: {report_path}")

    return stats


if __name__ == "__main__":
    stats = main()