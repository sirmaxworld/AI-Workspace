#!/usr/bin/env python3
"""
Secure Memory System with Classification Levels
Protects sensitive data from unauthorized access
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal
from enum import Enum

# Memory classification levels
class SecurityLevel(str, Enum):
    PUBLIC = "public"        # Safe to share, auto-load
    PRIVATE = "private"      # Personal info, load on request
    CONFIDENTIAL = "confidential"  # Sensitive business data, explicit access only
    SECRET = "secret"        # API keys, passwords, NEVER auto-load

# Memory file paths
BASE_DIR = Path("/Users/yourox/AI-Workspace/data/claude_memory_json")
PUBLIC_MEMORY = BASE_DIR / "memories_public.json"
PRIVATE_MEMORY = BASE_DIR / "memories_private.json"
CONFIDENTIAL_MEMORY = BASE_DIR / "memories_confidential.json"
SECRET_MEMORY = BASE_DIR / "memories_secret.json"

# Ensure directories exist
BASE_DIR.mkdir(parents=True, exist_ok=True)


class SecureMemorySystem:
    """Memory system with security classification"""
    
    def __init__(self):
        self.files = {
            SecurityLevel.PUBLIC: PUBLIC_MEMORY,
            SecurityLevel.PRIVATE: PRIVATE_MEMORY,
            SecurityLevel.CONFIDENTIAL: CONFIDENTIAL_MEMORY,
            SecurityLevel.SECRET: SECRET_MEMORY
        }
    
    def load_memories(self, level: SecurityLevel) -> list[dict[str, Any]]:
        """Load memories at specific security level"""
        file = self.files[level]
        if not file.exists():
            return []
        with open(file, 'r') as f:
            return json.load(f)
    
    def save_memory(
        self, 
        text: str, 
        level: SecurityLevel = SecurityLevel.PUBLIC,
        memory_type: str = "conversation"
    ) -> dict[str, Any]:
        """Save memory at specific security level"""
        memories = self.load_memories(level)
        
        new_memory = {
            "id": len(memories) + 1,
            "text": text,
            "type": memory_type,
            "level": level.value,
            "timestamp": datetime.now().isoformat(),
            "user_id": "yourox_default"
        }
        
        memories.append(new_memory)
        
        file = self.files[level]
        with open(file, 'w') as f:
            json.dump(memories, f, indent=2)
        
        return new_memory
    
    def load_safe_context(self, include_private: bool = False) -> str:
        """Load only safe memories for auto-context"""
        lines = [
            "🧠 CLAUDE'S PERSISTENT MEMORY",
            "=" * 60,
            ""
        ]
        
        # Always include public memories
        public = self.load_memories(SecurityLevel.PUBLIC)
        if public:
            lines.append("📢 PUBLIC MEMORIES:")
            for mem in public[-10:]:
                date = mem['timestamp'].split('T')[0]
                lines.append(f"[{date}] {mem['text']}")
            lines.append("")
        
        # Optionally include private (but not confidential/secret)
        if include_private:
            private = self.load_memories(SecurityLevel.PRIVATE)
            if private:
                lines.append("🔒 PRIVATE MEMORIES:")
                for mem in private[-5:]:
                    date = mem['timestamp'].split('T')[0]
                    lines.append(f"[{date}] {mem['text']}")
                lines.append("")
        
        # NEVER auto-load confidential or secret
        lines.append("⚠️  Confidential and secret memories available on request only")
        
        return "\n".join(lines)
    
    def search_memories(
        self, 
        query: str, 
        level: SecurityLevel | None = None
    ) -> list[dict[str, Any]]:
        """Search memories (respecting security levels)"""
        results = []
        query_lower = query.lower()
        
        # Search only specified level or public by default
        levels_to_search = [level] if level else [SecurityLevel.PUBLIC, SecurityLevel.PRIVATE]
        
        for search_level in levels_to_search:
            memories = self.load_memories(search_level)
            matches = [m for m in memories if query_lower in m['text'].lower()]
            results.extend(matches)
        
        return results
    
    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics"""
        return {
            "public": len(self.load_memories(SecurityLevel.PUBLIC)),
            "private": len(self.load_memories(SecurityLevel.PRIVATE)),
            "confidential": len(self.load_memories(SecurityLevel.CONFIDENTIAL)),
            "secret": len(self.load_memories(SecurityLevel.SECRET)),
            "total": sum([
                len(self.load_memories(level)) 
                for level in SecurityLevel
            ])
        }
    
    def migrate_existing_memories(self, source_file: Path) -> dict[str, int]:
        """Migrate existing memories to classified system"""
        if not source_file.exists():
            return {"migrated": 0, "skipped": 0}
        
        with open(source_file, 'r') as f:
            old_memories = json.load(f)
        
        # Classify existing memories
        migrated = 0
        for mem in old_memories:
            text_lower = mem['text'].lower()
            
            # Check for sensitive keywords
            if any(keyword in text_lower for keyword in ['api_key', 'password', 'secret', 'token', 'credential']):
                level = SecurityLevel.SECRET
            elif any(keyword in text_lower for keyword in ['confidential', 'private key', 'internal']):
                level = SecurityLevel.CONFIDENTIAL
            elif any(keyword in text_lower for keyword in ['personal', 'private']):
                level = SecurityLevel.PRIVATE
            else:
                level = SecurityLevel.PUBLIC
            
            # Save to appropriate level
            self.save_memory(mem['text'], level, mem.get('type', 'conversation'))
            migrated += 1
        
        return {"migrated": migrated, "skipped": 0}


def main():
    """CLI for secure memory system"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
Usage:
  python secure_memory.py migrate      # Migrate existing memories
  python secure_memory.py stats        # View statistics
  python secure_memory.py save "text" [level]  # Save memory
  python secure_memory.py search "query" [level]  # Search memories
  python secure_memory.py context      # Get safe context
        """)
        sys.exit(1)
    
    system = SecureMemorySystem()
    command = sys.argv[1]
    
    if command == "migrate":
        old_file = Path("/Users/yourox/AI-Workspace/data/claude_memory_json/memories.json")
        result = system.migrate_existing_memories(old_file)
        print(f"✓ Migrated {result['migrated']} memories")
        print(f"\nNew structure:")
        stats = system.get_stats()
        for level, count in stats.items():
            print(f"  {level}: {count}")
    
    elif command == "stats":
        stats = system.get_stats()
        print("\n📊 Secure Memory Statistics:")
        for level, count in stats.items():
            print(f"  {level}: {count}")
    
    elif command == "save":
        text = sys.argv[2]
        level = SecurityLevel(sys.argv[3]) if len(sys.argv) > 3 else SecurityLevel.PUBLIC
        mem = system.save_memory(text, level)
        print(f"✓ Saved to {level.value} (ID: {mem['id']})")
    
    elif command == "search":
        query = sys.argv[2]
        level = SecurityLevel(sys.argv[3]) if len(sys.argv) > 3 else None
        results = system.search_memories(query, level)
        print(f"\nFound {len(results)} results:")
        for r in results:
            print(f"  [{r['level']}] {r['text']}")
    
    elif command == "context":
        context = system.load_safe_context(include_private=False)
        print(context)


if __name__ == "__main__":
    main()
