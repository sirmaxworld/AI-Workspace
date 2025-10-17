#!/usr/bin/env python3
"""
Video Ingestion Pipeline

Processes new YouTube videos and stores them in:
1. Railway PostgreSQL (permanent structured storage)
2. Mem0 pgvector (semantic search)

Usage:
    python3 video_ingestion.py --video-id "dQw4w9WgXcQ"
    python3 video_ingestion.py --video-url "https://youtube.com/watch?v=dQw4w9WgXcQ"
    python3 video_ingestion.py --batch-file "new_videos.txt"
"""
import os
import sys
import json
import argparse
import psycopg2
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
from config.mem0_collections import get_mem0_config

load_dotenv('/Users/yourox/AI-Workspace/.env')

class VideoIngestionPipeline:
    def __init__(self):
        """Initialize Railway PostgreSQL and Mem0 connections"""
        self.conn_string = os.getenv('RAILWAY_DATABASE_URL')
        self.mem0_config = get_mem0_config("video_knowledge")

        # Initialize Mem0
        try:
            from mem0 import Memory
            self.mem0 = Memory.from_config(self.mem0_config)
            print("✅ Mem0 initialized")
        except ImportError:
            print("❌ mem0 library not installed")
            self.mem0 = None

    def fetch_video_data(self, video_id):
        """
        Fetch video metadata and transcript

        Args:
            video_id: YouTube video ID

        Returns:
            dict: Video data with transcript
        """
        print(f"📥 Fetching video data for {video_id}...")

        # TODO: Implement actual fetching using yt-dlp or YouTube API
        # For now, check if transcript exists in data/transcripts/
        transcript_file = Path(f'/Users/yourox/AI-Workspace/data/transcripts/{video_id}_full.json')

        if transcript_file.exists():
            with open(transcript_file, 'r') as f:
                return json.load(f)
        else:
            print(f"⚠️  Transcript not found: {transcript_file}")
            # In production, this would call yt-dlp to fetch transcript
            return None

    def store_in_railway(self, video_data):
        """
        Store video in Railway PostgreSQL tables

        Args:
            video_data: Video metadata and transcript

        Returns:
            bool: Success status
        """
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()

            # Extract metadata
            video_id = video_data.get('video_id')
            title = video_data.get('title', 'Untitled')
            url = video_data.get('url', f"https://youtube.com/watch?v={video_id}")

            channel = video_data.get('channel', {})
            channel_name = channel.get('name') if isinstance(channel, dict) else channel
            channel_id = channel.get('id') if isinstance(channel, dict) else None

            duration_seconds = video_data.get('duration_seconds') or video_data.get('duration')
            published_date = video_data.get('published_date')
            transcript = video_data.get('transcript', '')

            # Insert into videos table
            cursor.execute("""
                INSERT INTO videos (
                    video_id, title, url, channel_name, channel_id,
                    duration_seconds, published_date, created_at, metadata
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (video_id) DO UPDATE SET
                    updated_at = NOW(),
                    metadata = EXCLUDED.metadata;
            """, (
                video_id, title, url, channel_name, channel_id,
                duration_seconds, published_date, datetime.now(),
                json.dumps(video_data)
            ))

            # Insert transcript
            if transcript:
                cursor.execute("""
                    INSERT INTO video_transcripts (
                        video_id, transcript_full, created_at
                    ) VALUES (
                        %s, %s, %s
                    )
                    ON CONFLICT (video_id) DO UPDATE SET
                        transcript_full = EXCLUDED.transcript_full;
                """, (
                    video_id, transcript, datetime.now()
                ))

            conn.commit()
            cursor.close()
            conn.close()

            print(f"✅ Stored in Railway PostgreSQL: {video_id}")
            return True

        except Exception as e:
            print(f"❌ Railway storage error: {e}")
            return False

    def store_in_mem0(self, video_data):
        """
        Store video in Mem0 pgvector for semantic search

        Args:
            video_data: Video metadata and transcript

        Returns:
            bool: Success status
        """
        if not self.mem0:
            print("⚠️  Mem0 not available, skipping vector storage")
            return False

        try:
            video_id = video_data.get('video_id')
            title = video_data.get('title', 'Untitled')
            transcript = video_data.get('transcript', '')

            # Create searchable text (first 5000 chars)
            video_text = f"{title}\n\n{transcript[:5000]}"

            # Store with metadata
            channel = video_data.get('channel', {})
            channel_name = channel.get('name') if isinstance(channel, dict) else channel

            result = self.mem0.add(
                video_text,
                user_id="yourox_default",
                metadata={
                    "video_id": video_id,
                    "title": title,
                    "channel_name": channel_name,
                    "published_date": video_data.get('published_date'),
                    "duration_seconds": video_data.get('duration_seconds') or video_data.get('duration'),
                    "url": video_data.get('url', f"https://youtube.com/watch?v={video_id}"),
                    "source": "youtube_transcript",
                    "ingested_at": datetime.now().isoformat()
                }
            )

            print(f"✅ Stored in Mem0 pgvector: {video_id}")
            return True

        except Exception as e:
            print(f"❌ Mem0 storage error: {e}")
            return False

    def ingest_video(self, video_id):
        """
        Complete ingestion pipeline for a single video

        Args:
            video_id: YouTube video ID

        Returns:
            bool: Success status
        """
        print(f"\n{'='*60}")
        print(f"INGESTING VIDEO: {video_id}")
        print(f"{'='*60}\n")

        # Fetch data
        video_data = self.fetch_video_data(video_id)
        if not video_data:
            print(f"❌ Failed to fetch video data: {video_id}")
            return False

        # Store in Railway (permanent)
        railway_success = self.store_in_railway(video_data)

        # Store in Mem0 (semantic search)
        mem0_success = self.store_in_mem0(video_data)

        if railway_success:
            print(f"\n✅ Video ingested successfully: {video_id}")
            return True
        else:
            print(f"\n❌ Video ingestion failed: {video_id}")
            return False

    def ingest_batch(self, video_ids):
        """
        Ingest multiple videos

        Args:
            video_ids: List of YouTube video IDs

        Returns:
            tuple: (success_count, failed_count)
        """
        print(f"\n{'='*60}")
        print(f"BATCH INGESTION: {len(video_ids)} videos")
        print(f"{'='*60}\n")

        success = 0
        failed = 0

        for video_id in video_ids:
            if self.ingest_video(video_id):
                success += 1
            else:
                failed += 1

        print(f"\n{'='*60}")
        print(f"BATCH COMPLETE: {success} succeeded, {failed} failed")
        print(f"{'='*60}\n")

        return success, failed

def main():
    parser = argparse.ArgumentParser(description='Ingest YouTube videos into Railway pgvector')
    parser.add_argument('--video-id', help='Single YouTube video ID')
    parser.add_argument('--video-url', help='Single YouTube video URL')
    parser.add_argument('--batch-file', help='File with video IDs (one per line)')

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = VideoIngestionPipeline()

    # Process based on arguments
    if args.video_id:
        pipeline.ingest_video(args.video_id)
    elif args.video_url:
        # Extract video ID from URL
        if 'v=' in args.video_url:
            video_id = args.video_url.split('v=')[1].split('&')[0]
            pipeline.ingest_video(video_id)
        else:
            print("❌ Could not extract video ID from URL")
    elif args.batch_file:
        with open(args.batch_file, 'r') as f:
            video_ids = [line.strip() for line in f if line.strip()]
        pipeline.ingest_batch(video_ids)
    else:
        print("❌ Please provide --video-id, --video-url, or --batch-file")
        parser.print_help()

if __name__ == "__main__":
    main()
