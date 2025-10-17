# YouTube Knowledge Base - Expert-Level Categorization System

## 📋 Overview

This system provides **expert-level categorization** for YouTube videos, research papers, and citations with:
- **Multi-dimensional topic taxonomy**
- **Concept prerequisite tracking**
- **Learning path generation**
- **Citation network analysis**
- **Temporal relevance tracking**

## 🏗️ Architecture

```
TWO SEPARATE MEM0 COLLECTIONS:

1. youtube_knowledge (ai_workspace_memory)
   └─ Video transcripts with rich metadata
   └─ Embeddings for semantic search
   └─ Topic hierarchies and concepts

2. claude_memory (claude_memory)
   └─ Persistent chat memory across sessions
   └─ User preferences and context
   └─ Conversation history
```

## 📁 File Structure

```
AI-Workspace/
├── config/
│   ├── topic_taxonomy.json       # Master topic hierarchy
│   └── video_metadata_schema.json # Metadata structure
├── scripts/
│   ├── youtube_transcriber_pro.py # Get transcripts
│   ├── video_categorizer.py       # Categorize with Claude
│   ├── claude_memory.py           # Chat persistence
│   └── configure_mem0_anthropic.py # Setup Mem0
├── data/
│   ├── greg_isenberg_videos.json  # Video list
│   ├── transcripts/               # Raw transcripts
│   ├── categorized/               # Rich metadata
│   └── qdrant/                    # Vector database
│       ├── ai_workspace_memory/   # YouTube knowledge
│       └── claude_memory/         # Chat memory
```

## 🎯 How to Know All Topics

### Method 1: Query the Taxonomy File
```bash
# See all available topics
cat /Users/yourox/AI-Workspace/config/topic_taxonomy.json | jq '.disciplines'
```

### Method 2: Query Categorized Videos
```python
import json
from pathlib import Path

# Load all categorized metadata
categorized_dir = Path("/Users/yourox/AI-Workspace/data/categorized")

all_topics = set()
all_concepts = set()

for metadata_file in categorized_dir.glob("*_metadata.json"):
    with open(metadata_file) as f:
        data = json.load(f)
        
        # Extract topics
        classification = data.get("content_classification", {})
        all_topics.add(classification.get("primary_domain"))
        all_topics.update(classification.get("sub_domains", []))
        
        # Extract concepts
        for concept in data.get("concepts", []):
            all_concepts.add(concept["name"])

print(f"Total topics: {len(all_topics)}")
print(f"Total concepts: {len(all_concepts)}")
print("\\nTopics:", sorted(all_topics))
print("\\nConcepts:", sorted(all_concepts))
```


### Method 3: Query Mem0 Database Directly
```python
from mem0 import Memory
import os

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "ai_workspace_memory",
            "path": "/Users/yourox/AI-Workspace/data/qdrant"
        }
    }
}

memory = Memory(config=config)
all_memories = memory.get_all(user_id="yourox_default")
# Extract topics from metadata
```

## 🚀 Complete Workflow

### Step 1: Collect Videos ✅
```bash
# Already done - you have greg_isenberg_videos.json
```

### Step 2: Get Transcripts
```bash
cd /Users/yourox/AI-Workspace/scripts
python3 youtube_transcriber_pro.py
```

### Step 3: Categorize Videos
```bash
python3 video_categorizer.py
```

This will:
- Read each transcript
- Analyze with Claude
- Extract topics, concepts, prerequisites
- Save rich metadata to `/data/categorized/`
