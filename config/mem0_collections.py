#!/usr/bin/env python3
"""
Multi-Collection Mem0 Configuration
Manages separate collections for different purposes:
- claude_memory: Claude's persistent memory across chats
- youtube_knowledge: YouTube transcripts and learning content
- research_papers: Academic papers and citations (future)
"""

import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')


def get_mem0_config(collection_name: str) -> Dict:
    """
    Get Mem0 configuration for a specific collection
    
    Args:
        collection_name: Name of the collection
            - "claude_memory": For Claude's cross-chat memory
            - "youtube_knowledge": For YouTube transcripts
            - "research_papers": For research papers/citations
    
    Returns:
        Mem0 configuration dictionary
    """
    
    # Base configuration (same for all collections)
    base_config = {
        "llm": {
            "provider": "openai",
            "config": {
                "model": "gpt-4-turbo",
                "temperature": 0.1,
                "max_tokens": 2000,
                "api_key": os.getenv("OPENAI_API_KEY")
            }
        },
        "embedder": {
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small",
                "api_key": os.getenv("OPENAI_API_KEY")
            }
        },
        "vector_store": {
            "provider": "pgvector",
            "config": {
                "collection_name": collection_name,  # Different per collection
                "embedding_model_dims": 1536,
                "host": os.getenv("RAILWAY_DB_HOST"),
                "port": int(os.getenv("RAILWAY_DB_PORT", 5432)),
                "user": os.getenv("RAILWAY_DB_USER"),
                "password": os.getenv("RAILWAY_DB_PASSWORD"),
                "dbname": os.getenv("RAILWAY_DB_NAME")
            }
        },
        "version": "v1.1"
    }
    
    return base_config


# Collection purposes and metadata
COLLECTIONS = {
    "claude_memory": {
        "purpose": "Claude's persistent memory across chat sessions",
        "description": "Stores conversation context, user preferences, project status",
        "user_id": "yourox_default",
        "use_cases": [
            "Remember user's goals and preferences",
            "Track ongoing projects",
            "Track covered topics"
        ]
    },
    "yc_companies": {
        "purpose": "Y Combinator companies database (5,490+ companies)",
        "description": "All YC companies with descriptions, batch, industry, hiring status",
        "user_id": "yc_batch_groups",
        "use_cases": [
            "Semantic search for YC companies",
            "Find companies by industry and batch",
            "Discover hiring opportunities",
            "Research startup ecosystems",
            "Market intelligence and trends"
        ]
    },
    "video_knowledge": {
        "purpose": "YouTube transcripts and video learning content (392+ videos, PERMANENT)",
        "description": "Full transcripts, summaries, concepts, learning paths from educational videos",
        "user_id": "yourox_default",
        "use_cases": [
            "Semantic search across video transcripts",
            "Find videos by concepts and topics",
            "Build learning paths (prerequisites → enables)",
            "Cross-reference videos with papers and companies",
            "Track educational content by expertise level"
        ]
    },
    "research_papers": {
        "purpose": "Academic papers, citations, and research content",
        "description": "Papers from arXiv, Semantic Scholar with citations and abstracts",
        "user_id": "yourox_default",
        "use_cases": [
            "Store research papers",
            "Track citations and references",
            "Build citation network",
            "Expert-level knowledge categorization",
            "Link papers to videos and companies"
        ]
    }
}


def list_collections():
    """Print all available collections"""
    print("\n📚 Available Mem0 Collections")
    print("="*60)
    for name, info in COLLECTIONS.items():
        print(f"\n🔹 {name}")
        print(f"   Purpose: {info['purpose']}")
        print(f"   Description: {info['description']}")
        print(f"   Use Cases:")
        for use_case in info['use_cases']:
            print(f"   - {use_case}")


if __name__ == "__main__":
    list_collections()
    print("\n" + "="*60)
    print("✅ All collections use OpenAI GPT-4 + OpenAI embeddings")
    print("✅ Stored in Railway PostgreSQL with pgvector")
    print(f"✅ Host: {os.getenv('RAILWAY_DB_HOST', 'Not configured')}")
    print("="*60)
