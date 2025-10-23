#!/usr/bin/env python3
"""
Knowledge Collection Configuration
Central config for all content sources
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path("/Users/yourox/AI-Workspace")
COLLECTION_DIR = BASE_DIR / "knowledge-base"
LOGS_DIR = Path("/tmp/intelligence_logs")

# Create directories
COLLECTION_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Content sources configuration
SOURCES = {
    "youtube": {
        "channels": [
            # Strategy & Business
            {
                "name": "a16z",
                "url": "@a16z",
                "channel_id": "UC9cn-yyajOWfH0cVmvSw7Hw",
                "category": "strategy",
                "priority": "high",
                "topics": ["AI strategy", "startup advice", "technology trends"]
            },
            {
                "name": "Y Combinator",
                "url": "@ycombinator",
                "channel_id": "UCcefcZRL2oaA_uBNeo5UOWg",
                "category": "strategy",
                "priority": "high",
                "topics": ["startup strategy", "AI implementation", "growth"]
            },
            # Technical Implementation
            {
                "name": "AWS Events",
                "url": "@AWSEventsChannel",
                "category": "technical",
                "priority": "high",
                "topics": ["AWS AI services", "cloud architecture", "MLOps"]
            },
            {
                "name": "Google Cloud Tech",
                "url": "@googlecloudtech",
                "category": "technical",
                "priority": "high",
                "topics": ["Google AI", "Vertex AI", "ML pipelines"]
            },
            {
                "name": "Microsoft Azure",
                "url": "@MicrosoftAzure",
                "category": "technical",
                "priority": "medium",
                "topics": ["Azure AI", "OpenAI Service", "enterprise AI"]
            },
            # AI Research & Education
            {
                "name": "Two Minute Papers",
                "url": "@TwoMinutePapers",
                "category": "research",
                "priority": "medium",
                "topics": ["AI research", "paper summaries", "cutting edge"]
            },
            {
                "name": "Lex Fridman",
                "url": "@lexfridman",
                "category": "strategy",
                "priority": "medium",
                "topics": ["AI thought leaders", "deep discussions", "future of AI"]
            }
        ],
        "search_queries": [
            "AI implementation for business",
            "machine learning ROI",
            "AI transformation strategy",
            "enterprise AI deployment",
            "AI use cases manufacturing",
            "AI use cases retail",
            "AI use cases healthcare",
            "MLOps best practices"
        ],
        "max_videos_per_channel": 50,
        "max_search_results": 20
    },

    "consulting_reports": {
        "sources": [
            {
                "name": "McKinsey AI Insights",
                "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights",
                "selector": "article",
                "priority": "high",
                "category": "consulting"
            },
            {
                "name": "BCG AI Reports",
                "url": "https://www.bcg.com/capabilities/artificial-intelligence/insights",
                "selector": "article",
                "priority": "high",
                "category": "consulting"
            },
            {
                "name": "Deloitte AI Institute",
                "url": "https://www2.deloitte.com/us/en/pages/consulting/topics/ai-and-analytics.html",
                "selector": "article",
                "priority": "high",
                "category": "consulting"
            },
            {
                "name": "Gartner AI Research",
                "url": "https://www.gartner.com/en/artificial-intelligence",
                "selector": "article",
                "priority": "medium",
                "category": "research"
            }
        ],
        "keywords": [
            "artificial intelligence",
            "machine learning",
            "AI strategy",
            "digital transformation",
            "AI implementation",
            "AI ROI"
        ]
    },

    "research_papers": {
        "sources": [
            {
                "name": "arXiv AI",
                "url": "https://arxiv.org/list/cs.AI/recent",
                "categories": ["cs.AI", "cs.LG", "cs.CL"],
                "priority": "medium"
            },
            {
                "name": "Papers with Code",
                "url": "https://paperswithcode.com/latest",
                "priority": "high",
                "category": "research"
            }
        ],
        "keywords": [
            "enterprise AI",
            "production ML",
            "AI deployment",
            "business impact"
        ],
        "max_papers": 100
    },

    "podcasts": {
        "shows": [
            {
                "name": "AI in Business",
                "url": "https://emerj.com/artificial-intelligence-podcast/",
                "rss": "https://feeds.soundcloud.com/users/soundcloud:users:267196586/sounds.rss",
                "priority": "high",
                "category": "business"
            },
            {
                "name": "Practical AI",
                "url": "https://changelog.com/practicalai",
                "rss": "https://changelog.com/practicalai/feed",
                "priority": "high",
                "category": "technical"
            },
            {
                "name": "The AI in Business Podcast",
                "url": "https://techemergence.libsyn.com/",
                "rss": "https://techemergence.libsyn.com/rss",
                "priority": "medium",
                "category": "business"
            }
        ],
        "max_episodes_per_show": 20
    },

    "github": {
        "topics": [
            "ai-implementation",
            "mlops",
            "ai-agents",
            "llm-applications",
            "ai-frameworks"
        ],
        "languages": ["Python", "TypeScript", "JavaScript"],
        "min_stars": 100,
        "with_readme": True,
        "max_repos": 500
    }
}

# Collection priorities
PRIORITY_ORDER = ["high", "medium", "low"]

# File paths
STORAGE_PATHS = {
    "youtube": COLLECTION_DIR / "youtube",
    "consulting": COLLECTION_DIR / "consulting-reports",
    "research": COLLECTION_DIR / "research-papers",
    "podcasts": COLLECTION_DIR / "podcasts",
    "github": COLLECTION_DIR / "github-repos",
    "web_articles": COLLECTION_DIR / "web-articles"
}

# Create all storage directories
for path in STORAGE_PATHS.values():
    path.mkdir(parents=True, exist_ok=True)

# Collection metadata
METADATA_FILE = COLLECTION_DIR / "collection_metadata.json"
PROGRESS_FILE = COLLECTION_DIR / "collection_progress.json"

# Rate limiting
RATE_LIMITS = {
    "youtube": {
        "requests_per_hour": 100,
        "delay_between_requests": 2  # seconds
    },
    "web_scraping": {
        "requests_per_minute": 10,
        "delay_between_requests": 6  # seconds
    },
    "github": {
        "requests_per_hour": 60,  # GitHub API limit
        "delay_between_requests": 2
    }
}

# Quality filters
QUALITY_FILTERS = {
    "min_video_duration": 180,  # 3 minutes
    "min_transcript_length": 500,  # characters
    "min_article_length": 1000,  # characters
    "min_document_pages": 2,
    "exclude_patterns": [
        "advertisement",
        "sponsored",
        "click here",
        "subscribe now"
    ]
}

# First batch targets (initial collection)
FIRST_BATCH_TARGETS = {
    "youtube_videos": 100,
    "consulting_reports": 50,
    "research_papers": 30,
    "podcast_episodes": 20,
    "web_articles": 50,
    "github_repos": 50
}

def get_source_config(source_type: str):
    """Get configuration for a specific source type"""
    return SOURCES.get(source_type, {})

def get_storage_path(source_type: str):
    """Get storage path for a source type"""
    return STORAGE_PATHS.get(source_type, COLLECTION_DIR / source_type)

def get_rate_limit(source_type: str):
    """Get rate limit for a source type"""
    return RATE_LIMITS.get(source_type, {"delay_between_requests": 5})
