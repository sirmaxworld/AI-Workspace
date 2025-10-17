#!/usr/bin/env python3
"""
Simple vector ingestion - bypass Mem0's AI processing
Direct chunk storage for faster, more reliable ingestion
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
import hashlib

load_dotenv('/Users/yourox/AI-Workspace/.env')


class SimpleVectorStore:
    """Direct Qdrant storage without Mem0 overhead"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.transcripts_dir = self.workspace_dir / "data" / "transcripts"
        self.videos_json = self.workspace_dir / "data" / "greg_isenberg_videos.json"
        self.qdrant_dir = self.workspace_dir / "data" / "youtube_qdrant_direct"

        # Create directory
        self.qdrant_dir.mkdir(parents=True, exist_ok=True)

        # Initialize clients
        self.qdrant = QdrantClient(path=str(self.qdrant_dir))
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Collection name
        self.collection_name = "greg_isenberg_videos"

        # Initialize collection
        self._init_collection()

        print(f"✅ Vector store initialized: {self.qdrant_dir}")

    def _init_collection(self):
        """Create collection if it doesn't exist"""
        try:
            self.qdrant.get_collection(self.collection_name)
            print(f"✅ Collection '{self.collection_name}' already exists")
        except:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"✅ Created collection '{self.collection_name}'")

    def get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)

        return chunks

    def generate_id(self, video_id: str, chunk_index: int) -> str:
        """Generate unique ID for chunk"""
        return hashlib.md5(f"{video_id}_{chunk_index}".encode()).hexdigest()

    def ingest_transcript(self, video_id: str, video_metadata: Dict) -> Dict:
        """Ingest a single transcript"""
        transcript_file = self.transcripts_dir / f"{video_id}_full.json"

        if not transcript_file.exists():
            return {"status": "skipped", "reason": "file not found"}

        try:
            # Load transcript
            with open(transcript_file, 'r') as f:
                data = json.load(f)

            # Extract text
            if not data.get('transcript'):
                return {"status": "skipped", "reason": "no transcript"}

            segments = data['transcript'].get('segments', [])
            full_text = " ".join([seg.get('text', '') for seg in segments])

            if not full_text:
                return {"status": "skipped", "reason": "empty text"}

            # Chunk the text
            chunks = self.chunk_text(full_text)

            # Prepare points
            points = []
            title = data.get('title', video_metadata.get('title', 'Unknown'))

            print(f"  📝 {video_id}: {title[:50]}... ({len(chunks)} chunks)", end="", flush=True)

            for i, chunk in enumerate(chunks):
                # Get embedding
                embedding = self.get_embedding(chunk)

                # Create point
                point_id = self.generate_id(video_id, i)
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "video_id": video_id,
                        "title": title,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "text": chunk,
                        "method": data.get('method', 'unknown'),
                        "url": f"https://youtube.com/watch?v={video_id}",
                        "channel": video_metadata.get('channel', 'Greg Isenberg'),
                        "duration": video_metadata.get('duration', 0),
                        "upload_date": video_metadata.get('upload_date', ''),
                        "view_count": video_metadata.get('view_count', 0)
                    }
                )
                points.append(point)

            # Upsert points
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points
            )

            print(f" ✅")
            return {"status": "success", "chunks": len(chunks)}

        except Exception as e:
            print(f" ❌ Error: {e}")
            return {"status": "error", "reason": str(e)}

    def ingest_all(self):
        """Ingest all transcripts"""
        print(f"\n{'='*70}")
        print(f"🚀 DIRECT VECTOR INGESTION")
        print(f"{'='*70}\n")

        # Load video metadata
        with open(self.videos_json, 'r') as f:
            data = json.load(f)

        if isinstance(data, dict) and 'videos' in data:
            videos = {v['id']: v for v in data['videos']}
        else:
            videos = {v['id']: v for v in data}

        print(f"📹 Loaded metadata for {len(videos)} videos")

        # Find transcripts
        transcript_files = list(self.transcripts_dir.glob("*_full.json"))
        print(f"📝 Found {len(transcript_files)} transcript files\n")

        stats = {"success": 0, "skipped": 0, "error": 0, "total_chunks": 0}

        for transcript_file in transcript_files:
            video_id = transcript_file.stem.replace("_full", "")
            video_meta = videos.get(video_id, {})

            result = self.ingest_transcript(video_id, video_meta)

            if result["status"] == "success":
                stats["success"] += 1
                stats["total_chunks"] += result["chunks"]
            elif result["status"] == "skipped":
                stats["skipped"] += 1
            else:
                stats["error"] += 1

        print(f"\n{'='*70}")
        print(f"✅ INGESTION COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Success: {stats['success']} videos")
        print(f"⏭️  Skipped: {stats['skipped']} videos")
        print(f"❌ Errors: {stats['error']} videos")
        print(f"📦 Total chunks: {stats['total_chunks']}")
        print(f"{'='*70}\n")

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search the vector store"""
        # Get query embedding
        query_embedding = self.get_embedding(query)

        # Search
        results = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )

        return results

    def get_stats(self) -> Dict:
        """Get collection stats"""
        info = self.qdrant.get_collection(self.collection_name)
        return {
            "total_points": info.points_count,
            "collection": self.collection_name,
            "path": str(self.qdrant_dir)
        }


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 simple_vector_ingest.py [ingest|search|stats]")
        sys.exit(1)

    command = sys.argv[1]
    store = SimpleVectorStore()

    if command == "ingest":
        store.ingest_all()

    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python3 simple_vector_ingest.py search 'your query'")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        print(f"\n🔍 Searching for: '{query}'")
        print(f"{'='*70}\n")

        results = store.search(query, limit=5)

        for i, result in enumerate(results, 1):
            payload = result.payload
            print(f"{i}. {payload['title']}")
            print(f"   Score: {result.score:.3f}")
            print(f"   URL: {payload['url']}")
            print(f"   Chunk: {payload['chunk_index'] + 1}/{payload['total_chunks']}")
            print(f"   Text: {payload['text'][:200]}...")
            print()

        print(f"{'='*70}\n")

    elif command == "stats":
        stats = store.get_stats()
        print(f"\n📊 Vector Store Statistics")
        print(f"{'='*70}")
        print(f"Collection: {stats['collection']}")
        print(f"Total chunks: {stats['total_points']}")
        print(f"Path: {stats['path']}")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
