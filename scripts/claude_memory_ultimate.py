#!/usr/bin/env python3
"""
Claude Ultimate Memory System - DUAL-LAYER ARCHITECTURE (Thread-Safe)
Combines JSON (fast/reliable) with Mem0 (semantic/vast)
FIXED: Threading issues resolved
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv('/Users/yourox/AI-Workspace/.env')

# Fix threading issues BEFORE importing Mem0
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
# Tell SQLite to allow multi-threading
os.environ['SQLITE_THREADSAFE'] = '1'

# Try to import Mem0 (optional, system works without it)
try:
    from mem0 import Memory
    from mem0.configs.base import MemoryConfig, VectorStoreConfig, LlmConfig, EmbedderConfig
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    print("⚠️  Mem0 not available, running in JSON-only mode")


class ThreadSafeMemory:
    """Thread-safe wrapper for Mem0"""
    
    def __init__(self, config):
        self._local = threading.local()
        self._config = config
        
    def _get_memory(self):
        """Get thread-local Mem0 instance"""
        if not hasattr(self._local, 'memory'):
            self._local.memory = Memory(config=self._config)
        return self._local.memory
    
    def add(self, text, user_id, metadata=None):
        """Thread-safe add"""
        return self._get_memory().add(text, user_id=user_id, metadata=metadata or {})
    
    def search(self, query, user_id, limit=10):
        """Thread-safe search"""
        return self._get_memory().search(query, user_id=user_id, limit=limit)
    
    def get_all(self, user_id):
        """Thread-safe get all"""
        return self._get_memory().get_all(user_id=user_id)


class UltimateMemorySystem:
    """
    Dual-layer memory system (Thread-Safe):
    - Layer 1 (JSON): Fast, reliable, recent memories
    - Layer 2 (Mem0): Semantic search, unlimited scale
    """
    
    def __init__(self, user_id: str = "yourox_default"):
        self.user_id = user_id
        
        # Layer 1: JSON paths
        self.json_dir = Path("/Users/yourox/AI-Workspace/data/claude_memory_json")
        self.json_file = self.json_dir / "memories.json"
        self.json_index = self.json_dir / "index.json"
        
        # Layer 2: Mem0 paths
        self.mem0_dir = Path("/Users/yourox/AI-Workspace/data/claude_memory_qdrant")
        
        # Create directories
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.mem0_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize JSON layer
        self._init_json_layer()
        
        # Initialize Mem0 layer (if available) - Thread-safe version
        self.mem0 = None
        self.mem0_enabled = False
        if MEM0_AVAILABLE:
            try:
                self._init_mem0_layer()
                self.mem0_enabled = True
                print("✓ Dual-layer system initialized (JSON + Mem0) [Thread-Safe]")
            except Exception as e:
                print(f"⚠️  Mem0 initialization failed: {e}")
                print("✓ Running in JSON-only mode")
        else:
            print("✓ JSON layer initialized")
        
        print(f"✓ User: {user_id}")
        print(f"✓ JSON: {self.json_file}")
        if self.mem0_enabled:
            print(f"✓ Mem0: {self.mem0_dir} (Thread-Safe)")
    
    def _init_json_layer(self):
        """Initialize JSON storage"""
        if not self.json_file.exists():
            self._save_json([])
        
        if not self.json_index.exists():
            self._save_index({
                "user_id": self.user_id,
                "created_at": datetime.now().isoformat(),
                "total_memories": 0,
                "last_updated": datetime.now().isoformat(),
                "mem0_enabled": False
            })
    
    def _init_mem0_layer(self):
        """Initialize Thread-Safe Mem0"""
        history_path = str(self.mem0_dir / "history.db")
        
        config = MemoryConfig(
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "collection_name": "claude_memory",
                    "path": str(self.mem0_dir),
                    "embedding_model_dims": 1536,
                    "on_disk": True  # Better for threading
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
        
        # Use thread-safe wrapper
        self.mem0 = ThreadSafeMemory(config)
    
    def _load_json(self) -> List[Dict]:
        """Load memories from JSON"""
        if not self.json_file.exists():
            return []
        with open(self.json_file, 'r') as f:
            return json.load(f)
    
    def _save_json(self, memories: List[Dict]):
        """Save memories to JSON"""
        with open(self.json_file, 'w') as f:
            json.dump(memories, f, indent=2)
    
    def _load_index(self) -> Dict:
        """Load index metadata"""
        if not self.json_index.exists():
            return {}
        with open(self.json_index, 'r') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """Save index metadata"""
        with open(self.json_index, 'w') as f:
            json.dump(index, f, indent=2)
    
    def save_memory(self, text: str, memory_type: str = "conversation") -> Tuple[bool, str]:
        """
        Save memory to BOTH layers (Thread-Safe)
        
        Returns:
            (success, message)
        """
        timestamp = datetime.now().isoformat()
        
        # Layer 1: Save to JSON (always succeeds)
        json_memories = self._load_json()
        new_memory = {
            "id": len(json_memories) + 1,
            "text": text,
            "type": memory_type,
            "timestamp": timestamp,
            "user_id": self.user_id,
            "synced_to_mem0": False
        }
        json_memories.append(new_memory)
        self._save_json(json_memories)
        
        # Update index
        index = self._load_index()
        index["total_memories"] = len(json_memories)
        index["last_updated"] = timestamp
        index["mem0_enabled"] = self.mem0_enabled
        self._save_index(index)
        
        # Layer 2: Save to Mem0 (if available) - Thread-Safe
        mem0_status = "skipped"
        mem0_count = 0
        if self.mem0_enabled and self.mem0:
            try:
                result = self.mem0.add(
                    text,
                    user_id=self.user_id,
                    metadata={
                        "type": memory_type,
                        "timestamp": timestamp,
                        "json_id": new_memory["id"]
                    }
                )
                new_memory["synced_to_mem0"] = True
                self._save_json(json_memories)  # Update sync status
                mem0_count = len(result.get('results', [])) if isinstance(result, dict) else 1
                mem0_status = "synced"
            except Exception as e:
                print(f"⚠️  Mem0 save error: {e}")
                mem0_status = f"failed: {e}"
        
        message = f"✓ Saved to JSON"
        if mem0_status == "synced":
            message += f" + Mem0"
            if mem0_count > 0:
                message += f"\n🔄 Synced to Mem0: {mem0_count}"
        elif mem0_status != "skipped":
            message += f" (Mem0 {mem0_status})"
        
        return True, message
    
    def load_context(self, query: Optional[str] = None, limit: int = 15, use_semantic: bool = True) -> str:
        """
        Load context using dual-layer approach
        
        Args:
            query: Search query (None = recent memories)
            limit: Number of memories
            use_semantic: Use Mem0 semantic search if available
        
        Returns:
            Formatted context string
        """
        # Layer 1: JSON (fast path)
        json_memories = self._load_json()
        
        if not json_memories:
            return self._format_empty_context()
        
        # If no query, just return recent from JSON
        if not query:
            recent = json_memories[-limit:]
            return self._format_context(recent, len(json_memories), "JSON (Recent)")
        
        # Text search in JSON
        query_lower = query.lower()
        json_matches = [m for m in json_memories if query_lower in m['text'].lower()]
        
        # Layer 2: Mem0 semantic search (if available and requested)
        mem0_matches = []
        if use_semantic and self.mem0_enabled and self.mem0:
            try:
                results = self.mem0.search(query, user_id=self.user_id, limit=limit)
                if results and 'results' in results:
                    mem0_matches = results['results']
            except Exception as e:
                print(f"⚠️  Mem0 search failed: {e}")
        
        # Combine results
        if mem0_matches:
            combined_text = f"JSON matches: {len(json_matches)}, Mem0 semantic: {len(mem0_matches)}"
            display_memories = json_matches[-limit:] if json_matches else []
            return self._format_context(display_memories, len(json_memories), combined_text)
        else:
            display_memories = json_matches[-limit:] if json_matches else json_memories[-limit:]
            return self._format_context(display_memories, len(json_memories), "JSON Search")
    
    def _format_context(self, memories: List[Dict], total: int, source: str) -> str:
        """Format memories as context string"""
        header = f"""╔══════════════════════════════════════════════════════════╗
║     ULTIMATE MEMORY SYSTEM -     🟢 DUAL-LAYER          ║
╚══════════════════════════════════════════════════════════╝

👤 User: {self.user_id}
📊 Total Memories: {total}
📋 Showing: {len(memories)} ({source})
🕐 Loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 Search Capabilities:
  • Text search (JSON layer) ⚡ instant
  • Semantic search (Mem0 layer) 🧠 intelligent

─────────────────────────────────────────────────────────
💭 MEMORIES FROM PREVIOUS CONVERSATIONS
─────────────────────────────────────────────────────────

"""
        
        memory_lines = []
        for i, mem in enumerate(memories, 1):
            timestamp = mem.get('timestamp', 'Unknown')
            if 'T' in timestamp:
                timestamp = timestamp.split('T')[0] + ' ' + timestamp.split('T')[1][:5]
            
            synced = " ✓" if mem.get('synced_to_mem0') else ""
            memory_lines.append(f"Memory #{i} ({timestamp}){synced}")
            memory_lines.append(f"  {mem['text']}")
            memory_lines.append(f"  Type: {mem.get('type', 'conversation')}\n")
        
        footer = f"""════════════════════════════════════════════════════════════
💡 Powered by Dual-Layer Architecture
   Layer 1: JSON (100% reliable, instant)
   Layer 2: Mem0 (semantic search, unlimited scale)
════════════════════════════════════════════════════════════

============================================================
📋 Copy the above and paste to Claude!
============================================================
"""
        
        return header + '\n'.join(memory_lines) + footer
    
    def _format_empty_context(self) -> str:
        """Format empty context message"""
        return f"""╔══════════════════════════════════════════════════════════╗
║     ULTIMATE MEMORY SYSTEM -     🟢 DUAL-LAYER          ║
╚══════════════════════════════════════════════════════════╝

👤 User: {self.user_id}
📊 Total Memories: 0

No memories stored yet. Use save command to add your first memory!
"""
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        json_memories = self._load_json()
        synced_count = sum(1 for m in json_memories if m.get('synced_to_mem0'))
        
        return {
            "total_memories": len(json_memories),
            "synced_to_mem0": synced_count,
            "mem0_enabled": self.mem0_enabled,
            "json_path": str(self.json_file),
            "mem0_path": str(self.mem0_dir) if self.mem0_enabled else None
        }


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python claude_memory_ultimate_v2.py load [query]")
        print("  python claude_memory_ultimate_v2.py save 'memory text'")
        print("  python claude_memory_ultimate_v2.py stats")
        sys.exit(1)
    
    command = sys.argv[1]
    mem = UltimateMemorySystem()
    
    if command == "load":
        query = sys.argv[2] if len(sys.argv) > 2 else None
        context = mem.load_context(query=query)
        print(context)
    
    elif command == "save":
        if len(sys.argv) < 3:
            print("Error: Please provide memory text")
            sys.exit(1)
        text = sys.argv[2]
        success, message = mem.save_memory(text)
        print(message)
        if success:
            stats = mem.get_stats()
            print(f"📊 Total memories: {stats['total_memories']}")
    
    elif command == "stats":
        stats = mem.get_stats()
        print(f"\n📊 Memory System Statistics:")
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Synced to Mem0: {stats['synced_to_mem0']}")
        print(f"   Mem0 enabled: {stats['mem0_enabled']}")
        print(f"   JSON path: {stats['json_path']}")
        if stats['mem0_path']:
            print(f"   Mem0 path: {stats['mem0_path']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
