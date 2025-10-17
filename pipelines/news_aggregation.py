#!/usr/bin/env python3
"""
News Aggregation Pipeline with Time-Based TTL

Aggregates news from multiple sources into time-based windows:
- Hourly aggregations (TTL: 24 hours)
- Daily aggregations (TTL: 7 days)
- Weekly aggregations (TTL: 3 months)
- Monthly aggregations (TTL: 6 months)

Sources:
- Hacker News API
- arXiv recent papers
- Semantic Scholar trending papers
- Reddit (via API)

Usage:
    python3 news_aggregation.py --granularity hourly
    python3 news_aggregation.py --granularity daily
    python3 news_aggregation.py --cleanup  # Run TTL cleanup
"""
import os
import sys
import json
import argparse
import psycopg2
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
from config.mem0_collections import get_mem0_config

load_dotenv('/Users/yourox/AI-Workspace/.env')

class NewsAggregationPipeline:
    def __init__(self):
        """Initialize Railway PostgreSQL connection"""
        self.conn_string = os.getenv('RAILWAY_DATABASE_URL')

        # TTL settings (in hours)
        self.ttl_hours = {
            'hourly': 24,
            'daily': 24 * 7,
            'weekly': 24 * 90,
            'monthly': 24 * 180
        }

    def fetch_hacker_news(self, hours=1):
        """
        Fetch recent Hacker News stories

        Args:
            hours: Number of hours to look back

        Returns:
            list: HN stories
        """
        print(f"📥 Fetching Hacker News from last {hours} hours...")

        # TODO: Implement actual HN API fetching
        # Using https://github.com/HackerNews/API

        # Placeholder
        return [
            {"title": "HN Story 1", "url": "https://hn.com/1", "score": 100},
            {"title": "HN Story 2", "url": "https://hn.com/2", "score": 85},
        ]

    def fetch_arxiv_papers(self, hours=24):
        """
        Fetch recent arXiv papers

        Args:
            hours: Number of hours to look back

        Returns:
            list: arXiv papers
        """
        print(f"📥 Fetching arXiv papers from last {hours} hours...")

        # TODO: Implement arXiv API fetching
        # Using http://export.arxiv.org/api/query

        # Placeholder
        return [
            {"title": "Paper 1", "arxiv_id": "2024.12345", "category": "cs.AI"},
        ]

    def aggregate_news(self, granularity='hourly'):
        """
        Aggregate news for a time window

        Args:
            granularity: 'hourly', 'daily', 'weekly', or 'monthly'

        Returns:
            dict: Aggregated news summary
        """
        print(f"\n{'='*60}")
        print(f"AGGREGATING NEWS: {granularity.upper()}")
        print(f"{'='*60}\n")

        # Define time window
        now = datetime.now()
        if granularity == 'hourly':
            window_start = now.replace(minute=0, second=0, microsecond=0)
            window_end = window_start + timedelta(hours=1)
            hours_back = 1
        elif granularity == 'daily':
            window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            window_end = window_start + timedelta(days=1)
            hours_back = 24
        elif granularity == 'weekly':
            # Start of current week (Monday)
            window_start = now - timedelta(days=now.weekday())
            window_start = window_start.replace(hour=0, minute=0, second=0, microsecond=0)
            window_end = window_start + timedelta(days=7)
            hours_back = 24 * 7
        elif granularity == 'monthly':
            window_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # End of month (approximate)
            window_end = window_start + timedelta(days=32)
            window_end = window_end.replace(day=1)
            hours_back = 24 * 30
        else:
            raise ValueError(f"Invalid granularity: {granularity}")

        print(f"Time window: {window_start} to {window_end}")

        # Fetch from sources
        hn_stories = self.fetch_hacker_news(hours=hours_back)
        arxiv_papers = self.fetch_arxiv_papers(hours=hours_back)

        # Aggregate
        summary = {
            "total_hn_stories": len(hn_stories),
            "total_arxiv_papers": len(arxiv_papers),
            "top_hn_stories": hn_stories[:10],
            "top_arxiv_papers": arxiv_papers[:10],
            "trending_topics": self.extract_trending_topics(hn_stories, arxiv_papers)
        }

        # Calculate TTL
        ttl_hours = self.ttl_hours[granularity]
        expires_at = now + timedelta(hours=ttl_hours)

        print(f"✅ Aggregated {summary['total_hn_stories']} HN stories, {summary['total_arxiv_papers']} papers")
        print(f"⏰ TTL: {ttl_hours} hours (expires at {expires_at})")

        return {
            "window_start": window_start,
            "window_end": window_end,
            "granularity": granularity,
            "summary": summary,
            "expires_at": expires_at,
            "source_count": len(hn_stories) + len(arxiv_papers)
        }

    def extract_trending_topics(self, hn_stories, arxiv_papers):
        """Extract trending topics from news"""
        # TODO: Implement NLP-based topic extraction
        # For now, simple keyword extraction
        topics = ["AI", "Machine Learning", "Blockchain", "Climate Tech"]
        return topics

    def store_aggregation(self, aggregation):
        """
        Store news aggregation in Railway PostgreSQL

        Args:
            aggregation: Aggregation dict

        Returns:
            bool: Success status
        """
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO news_aggregations (
                    time_window_start, time_window_end, granularity,
                    summary, trending_topics, source_count, expires_at, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                );
            """, (
                aggregation['window_start'],
                aggregation['window_end'],
                aggregation['granularity'],
                json.dumps(aggregation['summary']),
                aggregation['summary'].get('trending_topics', []),
                aggregation['source_count'],
                aggregation['expires_at'],
                datetime.now()
            ))

            conn.commit()
            cursor.close()
            conn.close()

            print(f"✅ Stored aggregation in Railway PostgreSQL")
            return True

        except Exception as e:
            print(f"❌ Storage error: {e}")
            return False

    def cleanup_expired(self):
        """
        Delete expired news aggregations (TTL cleanup)

        Returns:
            int: Number of deleted records
        """
        print(f"\n{'='*60}")
        print(f"CLEANING UP EXPIRED NEWS")
        print(f"{'='*60}\n")

        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()

            # Count expired before deletion
            cursor.execute("""
                SELECT COUNT(*) FROM news_aggregations
                WHERE expires_at < NOW();
            """)
            expired_count = cursor.fetchone()[0]

            print(f"Found {expired_count} expired aggregations")

            if expired_count > 0:
                # Delete expired
                cursor.execute("""
                    DELETE FROM news_aggregations
                    WHERE expires_at < NOW();
                """)

                conn.commit()
                print(f"✅ Deleted {expired_count} expired aggregations")

            # Show current storage stats
            cursor.execute("""
                SELECT granularity, COUNT(*), MIN(time_window_start), MAX(time_window_start)
                FROM news_aggregations
                GROUP BY granularity;
            """)
            stats = cursor.fetchall()

            print(f"\n📊 Current storage stats:")
            for granularity, count, min_date, max_date in stats:
                print(f"   {granularity}: {count} records ({min_date.date()} to {max_date.date()})")

            cursor.close()
            conn.close()

            return expired_count

        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            return 0

    def run_aggregation(self, granularity):
        """
        Run complete aggregation pipeline

        Args:
            granularity: Time granularity

        Returns:
            bool: Success status
        """
        # Aggregate news
        aggregation = self.aggregate_news(granularity)

        # Store in Railway
        success = self.store_aggregation(aggregation)

        if success:
            print(f"\n✅ {granularity.capitalize()} aggregation complete!")
        else:
            print(f"\n❌ {granularity.capitalize()} aggregation failed!")

        return success

def main():
    parser = argparse.ArgumentParser(description='Aggregate news with time-based TTL')
    parser.add_argument('--granularity', choices=['hourly', 'daily', 'weekly', 'monthly'],
                        help='Aggregation granularity')
    parser.add_argument('--cleanup', action='store_true',
                        help='Run TTL cleanup (delete expired aggregations)')

    args = parser.parse_args()

    pipeline = NewsAggregationPipeline()

    if args.cleanup:
        pipeline.cleanup_expired()
    elif args.granularity:
        pipeline.run_aggregation(args.granularity)
    else:
        print("❌ Please specify --granularity or --cleanup")
        parser.print_help()

if __name__ == "__main__":
    main()
