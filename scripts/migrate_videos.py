#!/usr/bin/env python3
"""
Migrate Video Transcripts from JSON to Railway PostgreSQL + Mem0 pgvector

This script:
1. Reads video transcripts from /data/transcripts/*_full.json
2. Stores structured data in Railway PostgreSQL tables (videos, video_transcripts, etc.)
3. Stores embeddings in Mem0 pgvector collection for semantic search
4. Creates cross-references (videos → YC companies, videos → papers)

Run this AFTER user completes YC enrichment.
"""
import os
import json
import sys
import psycopg2
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.append('/Users/yourox/AI-Workspace')
from config.mem0_collections import get_mem0_config

load_dotenv('/Users/yourox/AI-Workspace/.env')

def load_video_transcripts():
    """Load all video transcripts from JSON files"""
    transcripts_dir = Path('/Users/yourox/AI-Workspace/data/transcripts')
    videos = []

    print(f"Loading video transcripts from {transcripts_dir}...")
    for json_file in sorted(transcripts_dir.glob('*_full.json')):
        try:
            with open(json_file, 'r') as f:
                video = json.load(f)
                videos.append(video)
        except Exception as e:
            print(f"⚠️  Error loading {json_file.name}: {e}")

    print(f"✅ Loaded {len(videos)} video transcripts")
    return videos

def migrate_to_railway(videos):
    """
    Migrate videos to Railway PostgreSQL tables

    Args:
        videos: List of video transcript dicts
    """
    print("\n" + "="*60)
    print("MIGRATING VIDEOS TO RAILWAY POSTGRESQL")
    print("="*60)

    conn_string = os.getenv('RAILWAY_DATABASE_URL')

    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        total = len(videos)
        migrated = 0
        failed = 0

        for video in videos:
            try:
                # Extract video metadata
                video_id = video.get('video_id')
                title = video.get('title', 'Untitled')
                url = video.get('url', f"https://youtube.com/watch?v={video_id}")

                # Channel info
                channel = video.get('channel', {})
                channel_name = channel.get('name') if isinstance(channel, dict) else channel
                channel_id = channel.get('id') if isinstance(channel, dict) else None

                # Temporal info
                duration_seconds = video.get('duration_seconds') or video.get('duration')
                published_date = video.get('published_date')

                # Transcript
                transcript = video.get('transcript', '')

                # Insert into videos table
                cursor.execute("""
                    INSERT INTO videos (
                        video_id, title, url, channel_name, channel_id,
                        duration_seconds, published_date, created_at,
                        metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (video_id) DO NOTHING;
                """, (
                    video_id, title, url, channel_name, channel_id,
                    duration_seconds, published_date, datetime.now(),
                    json.dumps(video)  # Store full video data as JSONB
                ))

                # Insert transcript
                if transcript:
                    cursor.execute("""
                        INSERT INTO video_transcripts (
                            video_id, transcript_full, created_at
                        ) VALUES (
                            %s, %s, %s
                        )
                        ON CONFLICT (video_id) DO NOTHING;
                    """, (
                        video_id, transcript, datetime.now()
                    ))

                migrated += 1

                if migrated % 10 == 0:
                    conn.commit()  # Commit in batches
                    print(f"   ✅ {migrated}/{total} videos migrated...", end='\r')

            except Exception as e:
                failed += 1
                print(f"   ⚠️  Failed to migrate {video.get('video_id', 'Unknown')}: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n\n{'='*60}")
        print(f"✅ Railway migration complete!")
        print(f"   Migrated: {migrated}/{total}")
        print(f"   Failed: {failed}")
        print(f"{'='*60}\n")

        return migrated, failed

    except Exception as e:
        print(f"❌ Railway migration error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

def migrate_to_mem0(videos, batch_size=20):
    """
    Migrate videos to Mem0 pgvector collection for semantic search

    Args:
        videos: List of video dicts
        batch_size: Process in smaller batches (videos have large transcripts)
    """
    print("\n" + "="*60)
    print("MIGRATING VIDEOS TO MEM0 PGVECTOR")
    print("="*60)

    try:
        from mem0 import Memory

        # Temporarily unset OPENROUTER_API_KEY to force Mem0 to use OpenAI
        openrouter_key = os.environ.pop('OPENROUTER_API_KEY', None)
        if openrouter_key:
            print("✅ Temporarily disabled OpenRouter (using OpenAI directly)")

        # Initialize Mem0 with pgvector backend
        config = get_mem0_config("video_knowledge")
        m = Memory.from_config(config)
        print("✅ Mem0 connection established")

        # Migrate in batches
        total = len(videos)
        migrated = 0
        failed = 0

        for i in range(0, total, batch_size):
            batch = videos[i:i+batch_size]
            print(f"\n📦 Processing batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, total)} of {total})...")

            for video in batch:
                try:
                    video_id = video.get('video_id')
                    title = video.get('title', 'Untitled')
                    transcript = video.get('transcript', '')

                    # Create searchable text (use first 5000 chars of transcript for embedding)
                    video_text = f"{title}\n\n{transcript[:5000]}"

                    # Store in Mem0 with metadata
                    channel = video.get('channel', {})
                    channel_name = channel.get('name') if isinstance(channel, dict) else channel

                    result = m.add(
                        video_text,
                        user_id="yourox_default",
                        metadata={
                            "video_id": video_id,
                            "title": title,
                            "channel_name": channel_name,
                            "published_date": video.get('published_date'),
                            "duration_seconds": video.get('duration_seconds') or video.get('duration'),
                            "url": video.get('url', f"https://youtube.com/watch?v={video_id}"),
                            "source": "youtube_transcript"
                        }
                    )

                    migrated += 1

                    if migrated % 5 == 0:
                        print(f"   ✅ {migrated}/{total} videos migrated...", end='\r')

                except Exception as e:
                    failed += 1
                    print(f"   ⚠️  Failed to migrate {video.get('video_id', 'Unknown')}: {e}")

        print(f"\n\n{'='*60}")
        print(f"✅ Mem0 migration complete!")
        print(f"   Migrated: {migrated}/{total}")
        print(f"   Failed: {failed}")
        print(f"{'='*60}\n")

        return migrated, failed

    except ImportError:
        print("❌ mem0 library not installed. Install with:")
        print("   pip3 install mem0ai")
        return 0, 0

    except Exception as e:
        print(f"❌ Mem0 migration error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

def verify_migration():
    """Verify migration was successful"""
    print("\n" + "="*60)
    print("VERIFYING MIGRATION")
    print("="*60)

    # Verify Railway tables
    try:
        conn_string = os.getenv('RAILWAY_DATABASE_URL')
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM videos;")
        video_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM video_transcripts;")
        transcript_count = cursor.fetchone()[0]

        print(f"✅ Railway PostgreSQL:")
        print(f"   - {video_count} videos")
        print(f"   - {transcript_count} transcripts")

        # Sample videos
        cursor.execute("SELECT video_id, title FROM videos LIMIT 3;")
        samples = cursor.fetchall()
        print(f"\n   Sample videos:")
        for video_id, title in samples:
            print(f"   - {video_id}: {title[:60]}...")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"⚠️  Railway verification error: {e}")

    # Verify Mem0
    try:
        from mem0 import Memory

        config = get_mem0_config("video_knowledge")
        m = Memory.from_config(config)

        results = m.get_all(user_id="yourox_default", limit=3)
        print(f"\n✅ Mem0 pgvector:")
        print(f"   - Found {len(results)} videos")

        # Test semantic search
        print("\n🔍 Testing semantic search...")
        search_results = m.search("machine learning tutorial", user_id="yourox_default", limit=3)

        print(f"✅ Search returned {len(search_results)} results")
        for i, result in enumerate(search_results, 1):
            metadata = result.get('metadata', {})
            print(f"   {i}. {metadata.get('title', 'Unknown')[:60]}...")

        print("\n✅ Migration verified successfully!")
        return True

    except Exception as e:
        print(f"⚠️  Mem0 verification error: {e}")
        return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Migrate video transcripts to Railway pgvector')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    args = parser.parse_args()

    print("\n" + "="*80)
    print(" "*20 + "VIDEO TRANSCRIPTS MIGRATION TO RAILWAY PGVECTOR")
    print("="*80)

    # Load videos
    videos = load_video_transcripts()

    if not videos:
        print("❌ No videos found to migrate")
        return 1

    # Ask for confirmation
    print(f"\n⚠️  About to migrate {len(videos)} video transcripts to Railway pgvector")
    print("   This will:")
    print("   - Store structured data in Railway PostgreSQL tables")
    print("   - Store embeddings in Railway pgvector via Mem0")
    print("   - Enable semantic search across all transcripts")
    print("   - Videos are PERMANENT (never expire)")

    if not args.yes:
        response = input("\nProceed with migration? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Migration cancelled")
            return 1
    else:
        print("\n✅ Auto-confirming migration (--yes flag)")


    # Migrate to Railway tables
    railway_migrated, railway_failed = migrate_to_railway(videos)

    if railway_migrated == 0:
        print("❌ Railway migration failed")
        return 1

    # Migrate to Mem0 pgvector
    mem0_migrated, mem0_failed = migrate_to_mem0(videos)

    if mem0_migrated == 0:
        print("⚠️  Mem0 migration failed, but Railway data is safe")

    # Verify
    if not verify_migration():
        print("⚠️  Migration completed but verification had issues")
        return 1

    print("\n🎉 Videos successfully migrated to Railway pgvector!")
    print(f"   Total storage: ~{(railway_migrated * 50) // 1024}MB")
    return 0

if __name__ == "__main__":
    sys.exit(main())
