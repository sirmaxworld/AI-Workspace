#!/usr/bin/env python3
"""
Reddit Snapshot Quality Checker
Analyzes collected Reddit snapshots for data quality
"""

import os
import json
import glob
from collections import defaultdict

def check_subreddit_quality(subreddit_name):
    """Check quality of collected snapshots for a subreddit"""
    data_dir = f"/Users/yourox/AI-Workspace/data/reddit_snapshots/{subreddit_name.lower()}"

    if not os.path.exists(data_dir):
        print(f"❌ No data found for r/{subreddit_name}")
        return

    snapshot_files = sorted(glob.glob(f"{data_dir}/*.json"))

    if not snapshot_files:
        print(f"❌ No snapshots found for r/{subreddit_name}")
        return

    print(f"\n{'='*70}")
    print(f"📊 QUALITY CHECK: r/{subreddit_name}")
    print(f"{'='*70}")
    print(f"Total Snapshots: {len(snapshot_files)}")
    print()

    stats = {
        'total_posts': 0,
        'high_quality_weeks': 0,  # 50+ posts
        'medium_quality_weeks': 0,  # 10-49 posts
        'low_quality_weeks': 0,  # <10 posts
        'positive_weeks': 0,
        'negative_weeks': 0,
        'neutral_weeks': 0,
        'total_pain_points': 0,
        'total_questions': 0,
    }

    week_details = []

    for filepath in snapshot_files:
        with open(filepath, 'r') as f:
            snapshot = json.load(f)

        posts = snapshot['metadata']['posts_analyzed']
        quality = snapshot['metadata']['data_quality_score']
        sentiment = snapshot['sentiment']['overall_sentiment']['label']
        week = snapshot['week']

        stats['total_posts'] += posts

        if posts >= 50:
            stats['high_quality_weeks'] += 1
        elif posts >= 10:
            stats['medium_quality_weeks'] += 1
        else:
            stats['low_quality_weeks'] += 1

        if sentiment == 'positive':
            stats['positive_weeks'] += 1
        elif sentiment == 'negative':
            stats['negative_weeks'] += 1
        else:
            stats['neutral_weeks'] += 1

        stats['total_pain_points'] += len(snapshot['pain_points']['top_pain_points'])
        stats['total_questions'] += len(snapshot['questions']['top_questions'])

        week_details.append({
            'week': week,
            'posts': posts,
            'quality': quality,
            'sentiment': sentiment,
            'sentiment_score': snapshot['sentiment']['overall_sentiment']['score']
        })

    # Print summary
    print(f"📈 ENGAGEMENT SUMMARY:")
    print(f"   Total Posts Analyzed: {stats['total_posts']:,}")
    print(f"   Average Posts per Week: {stats['total_posts'] / len(snapshot_files):.1f}")
    print()

    print(f"✅ QUALITY BREAKDOWN:")
    print(f"   High Quality (50+ posts): {stats['high_quality_weeks']} weeks ({stats['high_quality_weeks']/len(snapshot_files)*100:.0f}%)")
    print(f"   Medium Quality (10-49): {stats['medium_quality_weeks']} weeks ({stats['medium_quality_weeks']/len(snapshot_files)*100:.0f}%)")
    print(f"   Low Quality (<10): {stats['low_quality_weeks']} weeks ({stats['low_quality_weeks']/len(snapshot_files)*100:.0f}%)")
    print()

    print(f"😊 SENTIMENT SUMMARY:")
    print(f"   Positive Weeks: {stats['positive_weeks']} ({stats['positive_weeks']/len(snapshot_files)*100:.0f}%)")
    print(f"   Neutral Weeks: {stats['neutral_weeks']} ({stats['neutral_weeks']/len(snapshot_files)*100:.0f}%)")
    print(f"   Negative Weeks: {stats['negative_weeks']} ({stats['negative_weeks']/len(snapshot_files)*100:.0f}%)")
    print()

    print(f"🔍 INSIGHTS EXTRACTED:")
    print(f"   Total Pain Points: {stats['total_pain_points']}")
    print(f"   Total Questions: {stats['total_questions']}")
    print()

    # Show recent weeks
    print(f"📅 RECENT WEEKS (last 5):")
    for week_data in week_details[-5:]:
        emoji = "✅" if week_data['posts'] >= 50 else "⚠️" if week_data['posts'] >= 10 else "❌"
        sentiment_emoji = "😊" if week_data['sentiment'] == 'positive' else "😐" if week_data['sentiment'] == 'neutral' else "😞"
        print(f"   {emoji} {week_data['week']}: {week_data['posts']:3d} posts | {sentiment_emoji} {week_data['sentiment']} ({week_data['sentiment_score']:.2f})")
    print()

    # Overall verdict
    high_pct = stats['high_quality_weeks'] / len(snapshot_files) * 100
    if high_pct >= 60:
        print("✅ VERDICT: Excellent data quality!")
    elif high_pct >= 40:
        print("⚠️  VERDICT: Good data quality, some sparse weeks")
    else:
        print("❌ VERDICT: Many sparse weeks, consider adjusting collection strategy")

    return stats

def check_all_subreddits():
    """Check all collected subreddits"""
    data_dir = "/Users/yourox/AI-Workspace/data/reddit_snapshots"

    if not os.path.exists(data_dir):
        print("❌ No Reddit snapshots directory found")
        return

    subreddits = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]

    if not subreddits:
        print("❌ No subreddit data found")
        return

    print(f"\n{'='*70}")
    print(f"📊 ALL SUBREDDITS QUALITY CHECK")
    print(f"{'='*70}")
    print(f"Found {len(subreddits)} subreddits with data\n")

    all_stats = {}
    for subreddit in sorted(subreddits):
        stats = check_subreddit_quality(subreddit)
        if stats:
            all_stats[subreddit] = stats

    # Overall summary
    if all_stats:
        print(f"\n{'='*70}")
        print(f"📊 OVERALL SUMMARY")
        print(f"{'='*70}")
        total_posts = sum(s['total_posts'] for s in all_stats.values())
        total_weeks = sum(s['high_quality_weeks'] + s['medium_quality_weeks'] + s['low_quality_weeks'] for s in all_stats.values())
        print(f"   Total Subreddits: {len(all_stats)}")
        print(f"   Total Snapshots: {total_weeks}")
        print(f"   Total Posts Analyzed: {total_posts:,}")
        print(f"   Average Posts per Snapshot: {total_posts / total_weeks:.1f}")
        print()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        subreddit = sys.argv[1]
        check_subreddit_quality(subreddit)
    else:
        check_all_subreddits()
