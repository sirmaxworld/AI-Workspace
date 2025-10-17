#!/usr/bin/env python3
"""
YouTube Knowledge Base - Extended Memory System
Stores and searches YouTube video transcripts as an extended knowledge base
Separate from personal conversation memory
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/yourox/AI-Workspace/.env')

# Try to import Mem0
try:
    from mem0 import Memory
    from mem0.configs.base import MemoryConfig, VectorStoreConfig, LlmConfig, EmbedderConfig
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    print("⚠️  Mem0 not available")


class YouTubeKnowledgeBase:
    """
    YouTube Knowledge Base System
    Stores video transcripts in searchable vector database
    """
    
    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.transcripts_dir = self.workspace_dir / "data" / "transcripts"
        self.videos_json = self.workspace_dir / "data" / "greg_isenberg_videos.json"
        self.qdrant_dir = self.workspace_dir / "data" / "youtube_qdrant"
        
        # Create directories
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.qdrant_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Mem0 if available
        self.mem0 = None
        self.mem0_enabled = False
        
        if MEM0_AVAILABLE:
            try:
                self._init_mem0()
                self.mem0_enabled = True
                print("✓ YouTube Knowledge Base initialized with Mem0")
            except Exception as e:
                print(f"⚠️  Mem0 initialization failed: {e}")
                print("✓ Running in fallback mode (no semantic search)")
        else:
            print("✓ YouTube Knowledge Base initialized (no Mem0)")
        
        print(f"✓ Transcripts: {self.transcripts_dir}")
        print(f"✓ Database: {self.qdrant_dir}")
    
    def _init_mem0(self):
        """Initialize Mem0 for YouTube knowledge"""
        # Set environment variable to avoid threading issues
        os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
        
        history_path = str(self.qdrant_dir / "history.db")
        
        config = MemoryConfig(
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "collection_name": "youtube_knowledge",
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
            history_db_path=history_path
        )
        
        self.mem0 = Memory(config=config)
    
    def load_videos_metadata(self) -> List[Dict]:
        """Load videos metadata from JSON"""
        if not self.videos_json.exists():
            return []
        
        with open(self.videos_json, 'r') as f:
            return json.load(f)
    
    def ingest_transcript(self, video_id: str, title: str, force: bool = False) -> bool:
        """
        Ingest a single video transcript into the knowledge base
        
        Args:
            video_id: YouTube video ID
            title: Video title
            force: Re-ingest even if already exists
        
        Returns:
            Success status
        """
        transcript_file = self.transcripts_dir / f"{video_id}_full.txt"
        
        if not transcript_file.exists():
            print(f"✗ Transcript not found: {video_id}")
            return False
        
        # Read transcript
        with open(transcript_file, 'r') as f:
            transcript = f.read()
        
        if not self.mem0_enabled:
            print(f"⚠️  Mem0 not available, can't ingest")
            return False
        
        try:
            # Store in Mem0 with metadata
            self.mem0.add(
                transcript,
                user_id="youtube_knowledge",
                metadata={
                    "video_id": video_id,
                    "title": title,
                    "source": "youtube",
                    "ingested_at": datetime.now().isoformat()
                }
            )
            
            print(f"✓ Ingested: {title[:60]}...")
            return True
            
        except Exception as e:
            print(f"✗ Failed to ingest {video_id}: {e}")
            return False
    
    def ingest_all(self) -> Dict:
        """Ingest all available transcripts"""
        videos = self.load_videos_metadata()
        transcript_files = list(self.transcripts_dir.glob("*_full.txt"))
        
        results = {
            "total_videos": len(videos),
            "available_transcripts": len(transcript_files),
            "ingested": 0,
            "failed": 0,
            "skipped": 0
        }
        
        print(f"\n📹 Found {len(transcript_files)} transcripts")
        print(f"📊 Ingesting into YouTube Knowledge Base...")
        print()
        
        # Create a dict of video IDs to titles
        video_map = {v['id']: v['title'] for v in videos}
        
        for transcript_file in transcript_files:
            video_id = transcript_file.stem.replace("_full", "")
            title = video_map.get(video_id, "Unknown Title")
            
            if self.ingest_transcript(video_id, title):
                results["ingested"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search YouTube knowledge base
        
        Args:
            query: Search query
            limit: Max results
        
        Returns:
            List of matching results with video metadata
        """
        if not self.mem0_enabled:
            print("⚠️  Semantic search not available (Mem0 not initialized)")
            return []
        
        try:
            results = self.mem0.search(
                query,
                user_id="youtube_knowledge",
                limit=limit
            )
            
            if results and 'results' in results:
                return results['results']
            return []
            
        except Exception as e:
            print(f"✗ Search failed: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get knowledge base statistics"""
        videos = self.load_videos_metadata()
        transcript_files = list(self.transcripts_dir.glob("*_full.txt"))
        
        stats = {
            "total_videos_listed": len(videos),
            "transcripts_downloaded": len(transcript_files),
            "videos_without_transcript": len(videos) - len(transcript_files),
            "mem0_enabled": self.mem0_enabled,
            "collection": "youtube_knowledge",
            "location": str(self.qdrant_dir)
        }
        
        # Try to get Mem0 stats
        if self.mem0_enabled and self.mem0:
            try:
                all_memories = self.mem0.get_all(user_id="youtube_knowledge")
                if all_memories and 'results' in all_memories:
                    stats["videos_in_database"] = len(all_memories['results'])
                else:
                    stats["videos_in_database"] = 0
            except:
                stats["videos_in_database"] = 0
        
        return stats


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    kb = YouTubeKnowledgeBase()
    
    if command == "ingest":
        print("🚀 Starting ingestion of all transcripts...")
        results = kb.ingest_all()
        
        print("\n" + "="*60)
        print("📊 INGESTION RESULTS")
        print("="*60)
        print(f"Total Videos Listed: {results['total_videos']}")
        print(f"Available Transcripts: {results['available_transcripts']}")
        print(f"✓ Successfully Ingested: {results['ingested']}")
        print(f"✗ Failed: {results['failed']}")
        print(f"⊘ Skipped: {results['skipped']}")
        print("="*60)
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("✗ Error: Provide search query")
            print('Usage: python3 youtube_knowledge.py search "your query"')
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        results = kb.search(query, limit=3)
        
        print(f"\n🔍 Search Results for: '{query}'")
        print("="*60)
        
        if results:
            for i, result in enumerate(results, 1):
                memory = result.get('memory', '')
                metadata = result.get('metadata', {})
                title = metadata.get('title', 'Unknown')
                video_id = metadata.get('video_id', '')
                
                print(f"\n{i}. {title}")
                print(f"   Video ID: {video_id}")
                print(f"   URL: https://youtube.com/watch?v={video_id}")
                print(f"   Excerpt: {memory[:200]}...")
                print()
        else:
            print("No results found")
        
        print("="*60)
    
    elif command == "stats":
        stats = kb.get_statistics()
        
        print("\n📊 YouTube Knowledge Base Statistics")
        print("="*60)
        print(f"Collection: {stats['collection']}")
        print(f"Location: {stats['location']}")
        print(f"Mem0 Enabled: {stats['mem0_enabled']}")
        print(f"\nVideos Listed: {stats['total_videos_listed']}")
        print(f"Transcripts Downloaded: {stats['transcripts_downloaded']}")
        print(f"Videos in Database: {stats.get('videos_in_database', 'N/A')}")
        print(f"Missing Transcripts: {stats['videos_without_transcript']}")
        print("="*60)
    
    else:
        print(f"✗ Unknown command: {command}")
        print_usage()


def print_usage():
    print("""
╔══════════════════════════════════════════════════════════╗
║         YOUTUBE KNOWLEDGE BASE SYSTEM                    ║
╚══════════════════════════════════════════════════════════╝

COMMANDS:

  📥 Ingest all transcripts:
     python3 youtube_knowledge.py ingest
  
  🔍 Search knowledge base:
     python3 youtube_knowledge.py search "MCP servers"
  
  📊 View statistics:
     python3 youtube_knowledge.py stats

════════════════════════════════════════════════════════════

PURPOSE:
  Extended memory system for YouTube video knowledge
  Separate from personal conversation memory
  Searchable database of video content

WORKFLOW:
  1. Download transcripts (youtube_transcriber_pro.py)
  2. Ingest into database (youtube_knowledge.py ingest)
  3. Search during conversations (youtube_knowledge.py search "query")

════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    main()
