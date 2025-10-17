#!/usr/bin/env python3
"""
Ingest JSON transcripts into Vector DB for semantic search
Works with the new parallel transcription output format
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv('/Users/yourox/AI-Workspace/.env')

# Import Mem0
try:
    from mem0 import Memory
    from mem0.configs.base import MemoryConfig, VectorStoreConfig, LlmConfig, EmbedderConfig
    MEM0_AVAILABLE = True
except ImportError:
    print("❌ Mem0 not installed. Install with: pip install mem0ai")
    sys.exit(1)


class TranscriptIngester:
    """Ingest transcripts from JSON format into vector database"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.transcripts_dir = self.workspace_dir / "data" / "transcripts"
        self.videos_json = self.workspace_dir / "data" / "greg_isenberg_videos.json"
        self.qdrant_dir = self.workspace_dir / "data" / "youtube_qdrant"

        # Create directories
        self.qdrant_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Mem0
        self.mem0 = self._init_mem0()
        print(f"✅ Vector DB initialized at: {self.qdrant_dir}")

    def _init_mem0(self):
        """Initialize Mem0 with Qdrant"""
        os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

        config = MemoryConfig(
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "collection_name": "youtube_transcripts",
                    "path": str(self.qdrant_dir),
                    "embedding_model_dims": 1536
                }
            ),
            llm=LlmConfig(
                provider="anthropic",
                config={
                    "model": "claude-sonnet-4-20250514",
                    "temperature": 0.1,
                    "max_tokens": 2000,
                    "api_key": os.getenv("ANTHROPIC_API_KEY")
                }
            ),
            embedder=EmbedderConfig(
                provider="openai",
                config={
                    "model": "text-embedding-3-small",
                    "api_key": os.getenv("OPENAI_API_KEY")
                }
            ),
            history_db_path=str(self.qdrant_dir / "history.db")
        )

        return Memory(config=config)

    def load_video_metadata(self) -> Dict[str, Dict]:
        """Load video metadata from JSON"""
        if not self.videos_json.exists():
            return {}

        with open(self.videos_json, 'r') as f:
            data = json.load(f)

        # Handle both formats
        if isinstance(data, dict) and 'videos' in data:
            videos = data['videos']
        else:
            videos = data

        return {v['id']: v for v in videos}

    def extract_transcript_text(self, transcript_data: Dict) -> str:
        """Extract full text from transcript segments"""
        if not transcript_data or 'transcript' not in transcript_data:
            return ""

        segments = transcript_data['transcript'].get('segments', [])
        return " ".join([seg.get('text', '') for seg in segments])

    def chunk_transcript(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split transcript into overlapping chunks for better search"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)

        return chunks

    def ingest_transcript(self, video_id: str, transcript_file: Path, video_metadata: Dict) -> bool:
        """Ingest a single transcript"""
        try:
            # Load transcript JSON
            with open(transcript_file, 'r') as f:
                data = json.load(f)

            # Extract text
            full_text = self.extract_transcript_text(data)

            if not full_text:
                print(f"  ⚠️  No transcript text for {video_id}")
                return False

            # Get metadata
            title = data.get('title', video_metadata.get('title', 'Unknown'))
            method = data.get('method', 'unknown')
            qc = data.get('qc_verification', {})

            # Chunk the transcript for better search
            chunks = self.chunk_transcript(full_text)

            print(f"  📝 Ingesting {video_id}: {title[:50]}... ({len(chunks)} chunks)")

            # Ingest each chunk
            for i, chunk in enumerate(chunks):
                self.mem0.add(
                    chunk,
                    user_id="greg_isenberg_knowledge",
                    metadata={
                        "video_id": video_id,
                        "title": title,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "method": method,
                        "quality_score": qc.get('quality_score', 0),
                        "key_topics": ", ".join(qc.get('key_topics', [])),
                        "duration": video_metadata.get('duration', 0),
                        "url": f"https://youtube.com/watch?v={video_id}",
                        "channel": video_metadata.get('channel', 'Greg Isenberg'),
                        "upload_date": video_metadata.get('upload_date', ''),
                        "ingested_at": datetime.now().isoformat()
                    }
                )

            return True

        except Exception as e:
            print(f"  ❌ Error ingesting {video_id}: {e}")
            return False

    def ingest_all(self, force: bool = False) -> Dict:
        """Ingest all transcripts"""
        print(f"\n{'='*70}")
        print(f"🚀 TRANSCRIPT INGESTION TO VECTOR DB")
        print(f"{'='*70}\n")

        # Load video metadata
        video_metadata = self.load_video_metadata()
        print(f"📹 Loaded metadata for {len(video_metadata)} videos")

        # Find all transcript JSON files
        transcript_files = list(self.transcripts_dir.glob("*_full.json"))
        print(f"📝 Found {len(transcript_files)} transcript files")
        print()

        results = {
            "total_transcripts": len(transcript_files),
            "ingested": 0,
            "failed": 0,
            "skipped": 0
        }

        for transcript_file in transcript_files:
            video_id = transcript_file.stem.replace("_full", "")
            video_meta = video_metadata.get(video_id, {})

            if self.ingest_transcript(video_id, transcript_file, video_meta):
                results["ingested"] += 1
            else:
                results["failed"] += 1

        print(f"\n{'='*70}")
        print(f"✅ INGESTION COMPLETE")
        print(f"{'='*70}")
        print(f"Total transcripts: {results['total_transcripts']}")
        print(f"✅ Successfully ingested: {results['ingested']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"⏭️  Skipped: {results['skipped']}")
        print(f"{'='*70}\n")

        return results

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search the vector database"""
        try:
            results = self.mem0.search(
                query,
                user_id="greg_isenberg_knowledge",
                limit=limit
            )

            return results.get('results', []) if results else []

        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            all_memories = self.mem0.get_all(user_id="greg_isenberg_knowledge")
            total_chunks = len(all_memories.get('results', [])) if all_memories else 0

            # Count unique videos
            unique_videos = set()
            if all_memories and 'results' in all_memories:
                for mem in all_memories['results']:
                    meta = mem.get('metadata', {})
                    if 'video_id' in meta:
                        unique_videos.add(meta['video_id'])

            return {
                "total_chunks": total_chunks,
                "unique_videos": len(unique_videos),
                "collection": "youtube_transcripts",
                "user_id": "greg_isenberg_knowledge"
            }
        except Exception as e:
            print(f"⚠️  Stats error: {e}")
            return {"error": str(e)}


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Ingest transcripts into vector DB')
    parser.add_argument('command', choices=['ingest', 'search', 'stats'], help='Command to run')
    parser.add_argument('--query', '-q', help='Search query (for search command)')
    parser.add_argument('--limit', '-l', type=int, default=5, help='Number of search results')
    parser.add_argument('--force', '-f', action='store_true', help='Force re-ingestion')

    args = parser.parse_args()

    ingester = TranscriptIngester()

    if args.command == 'ingest':
        results = ingester.ingest_all(force=args.force)

    elif args.command == 'search':
        if not args.query:
            print("❌ Search query required. Use --query 'your search'")
            sys.exit(1)

        print(f"\n🔍 Searching for: '{args.query}'")
        print(f"{'='*70}\n")

        results = ingester.search(args.query, limit=args.limit)

        if results:
            for i, result in enumerate(results, 1):
                memory = result.get('memory', '')
                metadata = result.get('metadata', {})

                print(f"{i}. {metadata.get('title', 'Unknown')}")
                print(f"   Video ID: {metadata.get('video_id', 'N/A')}")
                print(f"   URL: {metadata.get('url', 'N/A')}")
                print(f"   Chunk: {metadata.get('chunk_index', 0) + 1}/{metadata.get('total_chunks', 1)}")
                print(f"   Quality: {metadata.get('quality_score', 0):.2f}")
                print(f"   Topics: {metadata.get('key_topics', 'N/A')}")
                print(f"   Excerpt: {memory[:200]}...")
                print()
        else:
            print("No results found")

        print(f"{'='*70}\n")

    elif args.command == 'stats':
        stats = ingester.get_stats()

        print(f"\n📊 Vector Database Statistics")
        print(f"{'='*70}")
        print(f"Collection: {stats.get('collection', 'N/A')}")
        print(f"User ID: {stats.get('user_id', 'N/A')}")
        print(f"Total chunks: {stats.get('total_chunks', 0)}")
        print(f"Unique videos: {stats.get('unique_videos', 0)}")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
