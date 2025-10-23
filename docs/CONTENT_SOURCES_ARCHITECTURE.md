# Content Sources Integration Architecture

**Goal**: Expand database with external sources while maintaining content quality and preventing information overload

**Key Principles**:
1. Source attribution always tracked
2. Content weighted by importance and reliability
3. Video transcripts remain primary source (highest weight)
4. RSS/API news supplements, never dominates
5. Metadata-rich for intelligent filtering

---

## 1. Database Schema Design

### 1.1 New Tables

#### `external_sources` (Source Registry)
```sql
CREATE TABLE external_sources (
  source_id TEXT PRIMARY KEY,           -- e.g., "hackernews", "techcrunch"
  name TEXT NOT NULL,                   -- "Hacker News (YCombinator)"
  domain TEXT NOT NULL,                 -- "news.ycombinator.com"
  category TEXT NOT NULL,               -- "ai_tools_and_news", "business_trends"
  source_type TEXT NOT NULL,            -- "video_transcript", "rss_feed", "api", "scraping"
  priority TEXT NOT NULL,               -- "critical", "high", "medium", "low"
  base_weight REAL DEFAULT 0.5,         -- Base importance score (0.0 - 1.0)
  domain_authority INTEGER,             -- SEO metric (0-100, if available)
  update_frequency TEXT,                -- "realtime", "daily", "weekly"
  extraction_method TEXT,               -- "rss", "api", "scraping"
  api_endpoint TEXT,                    -- If applicable
  rss_url TEXT,                         -- If applicable
  rate_limit_per_day INTEGER,           -- Max articles to fetch per day
  is_active BOOLEAN DEFAULT 1,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_fetched_at TIMESTAMP,
  total_articles_fetched INTEGER DEFAULT 0,
  metadata JSON                         -- Additional config
);
```

**Key Design Choices**:
- `base_weight`: Pre-defined importance (video transcripts = 1.0, RSS = 0.3-0.7)
- `rate_limit_per_day`: Prevents flooding (e.g., max 10 articles/day from news sites)
- `source_type`: Critical for differentiating content types

#### `external_content` (Articles, Posts, News)
```sql
CREATE TABLE external_content (
  content_id TEXT PRIMARY KEY,          -- UUID or hash
  source_id TEXT NOT NULL,              -- FK to external_sources
  title TEXT NOT NULL,
  url TEXT UNIQUE NOT NULL,
  author TEXT,                          -- Article author
  author_id TEXT,                       -- Author identifier (for tracking)
  published_at TIMESTAMP,
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  content_type TEXT,                    -- "article", "video", "podcast", "documentation"
  content_text TEXT,                    -- Full text or summary
  content_length INTEGER,               -- Word count

  -- Metadata
  tags JSON,                            -- ["AI", "GPT-4", "startup"]
  categories JSON,                      -- From source classification

  -- Engagement metrics (if available)
  views INTEGER,
  upvotes INTEGER,                      -- HN points, reddit upvotes
  comments_count INTEGER,
  shares INTEGER,

  -- Quality signals
  has_code_examples BOOLEAN DEFAULT 0,
  has_actionable_advice BOOLEAN DEFAULT 0,
  is_tutorial BOOLEAN DEFAULT 0,
  is_news BOOLEAN DEFAULT 0,
  is_opinion BOOLEAN DEFAULT 0,

  -- Scoring (calculated)
  raw_score REAL,                       -- Initial quality score
  final_score REAL,                     -- After all factors applied
  relevance_score REAL,                 -- To user's interests (ML-based)
  freshness_score REAL,                 -- Decays over time

  -- Status
  is_processed BOOLEAN DEFAULT 0,
  is_indexed BOOLEAN DEFAULT 0,

  FOREIGN KEY (source_id) REFERENCES external_sources(source_id)
);

CREATE INDEX idx_ext_content_source ON external_content(source_id);
CREATE INDEX idx_ext_content_published ON external_content(published_at DESC);
CREATE INDEX idx_ext_content_score ON external_content(final_score DESC);
CREATE INDEX idx_ext_content_processed ON external_content(is_processed);
```

**Key Design Choices**:
- `final_score`: Weighted importance (0.0 - 1.0) for ranking
- Engagement metrics: Objective quality signals (HN points, etc.)
- Quality signals: Boolean flags for filtering
- Multiple indexes for fast queries

#### `content_authors` (Author Popularity Tracking)
```sql
CREATE TABLE content_authors (
  author_id TEXT PRIMARY KEY,
  author_name TEXT NOT NULL,
  author_url TEXT,                      -- Profile link
  domain TEXT,                          -- Primary domain

  -- Popularity metrics
  total_articles INTEGER DEFAULT 0,
  avg_engagement REAL,                  -- Average upvotes/views
  follower_count INTEGER,               -- If available (Twitter, etc.)

  -- Quality signals
  verified BOOLEAN DEFAULT 0,           -- Verified account
  expert_in_topics JSON,                -- ["AI", "Marketing"]
  authority_score REAL,                 -- Calculated (0.0 - 1.0)

  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_active_at TIMESTAMP,

  metadata JSON
);

CREATE INDEX idx_author_authority ON content_authors(authority_score DESC);
```

#### `content_insights` (Extracted Intelligence)
```sql
CREATE TABLE content_insights (
  insight_id TEXT PRIMARY KEY,
  content_id TEXT NOT NULL,             -- FK to external_content OR video_id
  source_type TEXT NOT NULL,            -- "video_transcript" or "external_content"

  insight_type TEXT NOT NULL,           -- "tool", "trend", "playbook", "opportunity"
  title TEXT NOT NULL,
  description TEXT,
  actionability_score REAL,             -- How actionable (0.0 - 1.0)
  confidence REAL,                      -- Extraction confidence

  extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  tags JSON,
  metadata JSON,

  FOREIGN KEY (content_id) REFERENCES external_content(content_id)
);

CREATE INDEX idx_insights_type ON content_insights(insight_type);
CREATE INDEX idx_insights_actionability ON content_insights(actionability_score DESC);
```

---

## 2. Content Scoring & Weighting System

### 2.1 Base Weights by Source Type

```python
SOURCE_TYPE_WEIGHTS = {
    "video_transcript": 1.0,      # PRIMARY SOURCE - Full weight
    "api": 0.7,                   # High quality, structured
    "rss_feed": 0.5,              # Medium quality, news/blog
    "scraping": 0.3,              # Lower confidence, may be partial
}
```

### 2.2 Score Calculation Formula

```python
def calculate_final_score(content):
    """
    Final Score = Base Weight × Quality Score × Freshness × Engagement × Author Authority
    """

    # 1. Base weight from source type
    base_weight = SOURCE_TYPE_WEIGHTS[content.source.source_type]

    # 2. Quality score (0.0 - 1.0)
    quality_score = calculate_quality_score(content)

    # 3. Freshness score (decays over time)
    freshness_score = calculate_freshness(content.published_at)

    # 4. Engagement score (normalized)
    engagement_score = calculate_engagement(content)

    # 5. Author authority (0.0 - 1.0)
    author_score = content.author.authority_score if content.author else 0.5

    # Combine with weights
    final_score = (
        base_weight * 0.40 +          # Source type is most important
        quality_score * 0.25 +
        freshness_score * 0.15 +
        engagement_score * 0.10 +
        author_score * 0.10
    )

    return min(final_score, 1.0)


def calculate_quality_score(content):
    """Quality signals from content analysis"""
    score = 0.5  # Start neutral

    # Positive signals
    if content.has_code_examples: score += 0.15
    if content.has_actionable_advice: score += 0.15
    if content.is_tutorial: score += 0.10
    if content.content_length > 1000: score += 0.05  # Substantial content

    # Negative signals
    if content.is_opinion: score -= 0.10
    if content.content_length < 200: score -= 0.15  # Too short

    return max(0.0, min(score, 1.0))


def calculate_freshness(published_at):
    """Freshness decays over time"""
    days_old = (datetime.now() - published_at).days

    if days_old <= 1: return 1.0
    elif days_old <= 7: return 0.9
    elif days_old <= 30: return 0.7
    elif days_old <= 90: return 0.5
    elif days_old <= 180: return 0.3
    else: return 0.2


def calculate_engagement(content):
    """Normalize engagement metrics"""
    if not content.upvotes and not content.views:
        return 0.5  # Neutral if no data

    # Example for Hacker News (adjust per source)
    if content.source_id == "hackernews":
        if content.upvotes >= 500: return 1.0
        elif content.upvotes >= 100: return 0.8
        elif content.upvotes >= 50: return 0.6
        else: return 0.4

    return 0.5  # Default
```

### 2.3 Query Weighting (Preventing Flooding)

When querying for intelligence or recommendations:

```python
def get_weighted_content(limit=50):
    """
    Get content with proportional representation
    Ensures video transcripts dominate, external sources supplement
    """

    # Target distribution
    DISTRIBUTION = {
        "video_transcript": 0.70,  # 70% from videos
        "api": 0.15,               # 15% from APIs
        "rss_feed": 0.10,          # 10% from RSS
        "scraping": 0.05,          # 5% from scraping
    }

    results = []
    for source_type, proportion in DISTRIBUTION.items():
        count = int(limit * proportion)

        # Get top-scored content from this source type
        content = db.query("""
            SELECT c.* FROM external_content c
            JOIN external_sources s ON c.source_id = s.source_id
            WHERE s.source_type = ?
            ORDER BY c.final_score DESC, c.published_at DESC
            LIMIT ?
        """, [source_type, count])

        results.extend(content)

    # Sort combined results by final score
    return sorted(results, key=lambda x: x.final_score, reverse=True)[:limit]
```

---

## 3. Preventing Database Flooding

### 3.1 Rate Limiting

```python
RATE_LIMITS = {
    "critical": 50,    # Max 50 articles/day from critical sources
    "high": 20,        # Max 20 articles/day from high priority
    "medium": 10,      # Max 10 articles/day from medium
    "low": 5,          # Max 5 articles/day from low
}

def should_fetch_from_source(source):
    """Check if we can fetch more from this source today"""
    today_count = db.count_fetched_today(source.source_id)
    limit = RATE_LIMITS[source.priority]
    return today_count < limit
```

### 3.2 Quality Filters

Only fetch content that meets minimum thresholds:

```python
MINIMUM_THRESHOLDS = {
    "hackernews": {
        "min_upvotes": 50,         # Only HN posts with 50+ points
        "min_comments": 5,
    },
    "techcrunch": {
        "min_word_count": 500,     # No short news briefs
    },
    "default": {
        "min_word_count": 300,
        "min_quality_score": 0.4,
    }
}
```

### 3.3 Deduplication

```python
def is_duplicate(new_content):
    """Check if content already exists (by URL or title similarity)"""

    # Exact URL match
    if db.exists(url=new_content.url):
        return True

    # Title similarity (fuzzy match > 90%)
    similar = db.find_similar_titles(new_content.title, threshold=0.9)
    if similar:
        return True

    return False
```

---

## 4. Source Attribution Schema

### 4.1 Always Track Source in Insights

When extracting intelligence from ANY content:

```python
@dataclass
class Intelligence:
    insight_id: str
    source_content_id: str           # Links to external_content OR video_id
    source_type: str                 # "video_transcript" or "external_content"
    source_name: str                 # Human-readable: "Hacker News" or "Lenny's Podcast"
    author: Optional[str]
    published_at: datetime

    # The actual insight
    insight_type: str                # "tool", "trend", "playbook"
    title: str
    description: str
    actionability_score: float

    # Weighting
    base_weight: float               # From source type
    final_score: float               # After all factors
```

### 4.2 Display Source in UI

When showing intelligence to user:

```typescript
interface Intelligence {
  title: string;
  description: string;
  sourceType: 'video' | 'article' | 'api';
  sourceName: string;              // "Lenny's Podcast" or "Hacker News"
  sourceUrl: string;
  author?: string;
  publishedAt: string;
  trustScore: number;              // final_score (0-100 for display)
}

// In UI:
<div className="source-badge">
  {sourceType === 'video' ? '🎥' : '📰'} {sourceName}
  <span className="trust-score">{trustScore}/100</span>
</div>
```

---

## 5. Integration Strategy for Tier 1 (8 Easy Wins)

### 5.1 Source Configuration

```json
{
  "tier1_sources": [
    {
      "source_id": "hackernews",
      "name": "Hacker News (YCombinator)",
      "domain": "news.ycombinator.com",
      "source_type": "api",
      "priority": "critical",
      "base_weight": 0.8,
      "rate_limit_per_day": 50,
      "extraction_method": "api",
      "api_endpoint": "https://hacker-news.firebaseio.com/v0",
      "quality_filter": {
        "min_upvotes": 50,
        "min_comments": 5
      }
    },
    {
      "source_id": "techcrunch",
      "name": "TechCrunch",
      "domain": "techcrunch.com",
      "source_type": "rss_feed",
      "priority": "high",
      "base_weight": 0.6,
      "rate_limit_per_day": 20,
      "extraction_method": "rss",
      "rss_url": "https://techcrunch.com/feed/",
      "quality_filter": {
        "min_word_count": 500
      }
    },
    {
      "source_id": "hubspot_blog",
      "name": "HubSpot Blog",
      "domain": "blog.hubspot.com",
      "source_type": "rss_feed",
      "priority": "high",
      "base_weight": 0.7,
      "rate_limit_per_day": 15,
      "extraction_method": "rss",
      "rss_url": "https://blog.hubspot.com/marketing/rss.xml",
      "category": "marketing"
    },
    {
      "source_id": "small_biz_trends",
      "name": "Small Business Trends",
      "domain": "smallbiztrends.com",
      "source_type": "rss_feed",
      "priority": "medium",
      "base_weight": 0.5,
      "rate_limit_per_day": 10,
      "extraction_method": "rss",
      "rss_url": "https://smallbiztrends.com/feed"
    },
    {
      "source_id": "social_media_examiner",
      "name": "Social Media Examiner",
      "domain": "socialmediaexaminer.com",
      "source_type": "rss_feed",
      "priority": "medium",
      "base_weight": 0.5,
      "rate_limit_per_day": 10,
      "extraction_method": "rss",
      "rss_url": "https://www.socialmediaexaminer.com/feed/"
    },
    {
      "source_id": "neil_patel",
      "name": "Neil Patel Blog",
      "domain": "neilpatel.com",
      "source_type": "rss_feed",
      "priority": "medium",
      "base_weight": 0.6,
      "rate_limit_per_day": 10,
      "extraction_method": "rss",
      "rss_url": "https://neilpatel.com/feed/"
    },
    {
      "source_id": "seth_godin",
      "name": "Seth Godin's Blog",
      "domain": "seths.blog",
      "source_type": "rss_feed",
      "priority": "high",
      "base_weight": 0.7,
      "rate_limit_per_day": 5,
      "extraction_method": "rss",
      "rss_url": "https://seths.blog/feed/"
    },
    {
      "source_id": "moz_blog",
      "name": "Moz Blog",
      "domain": "moz.com",
      "source_type": "rss_feed",
      "priority": "medium",
      "base_weight": 0.6,
      "rate_limit_per_day": 10,
      "extraction_method": "rss",
      "rss_url": "https://moz.com/blog/feed"
    }
  ]
}
```

### 5.2 Fetching Schedule

```python
FETCH_SCHEDULE = {
    "critical": "every 2 hours",   # Hacker News
    "high": "every 6 hours",       # TechCrunch, HubSpot, Seth Godin
    "medium": "daily at 8am",      # Others
}
```

### 5.3 Initial Data Volume Estimates

| Source | Frequency | Articles/Day | Words/Article | Total Words/Day |
|--------|-----------|--------------|---------------|-----------------|
| Hacker News | 2h | 50 | 2000 | 100,000 |
| TechCrunch | 6h | 20 | 800 | 16,000 |
| HubSpot | 6h | 15 | 1500 | 22,500 |
| Small Biz | Daily | 10 | 1000 | 10,000 |
| SME | Daily | 10 | 1200 | 12,000 |
| Neil Patel | Daily | 10 | 1500 | 15,000 |
| Seth Godin | Daily | 5 | 500 | 2,500 |
| Moz | Daily | 10 | 1200 | 12,000 |
| **TOTAL** | | **130** | | **190,000** |

**Comparison to Video Transcripts**:
- Assume 10 video transcripts/week = ~50,000 words/week = ~7,000 words/day
- External sources = 190,000 words/day
- **Ratio**: 27:1 (external:video) in volume

**But with weighting**:
- Video transcripts: base_weight = 1.0
- External: base_weight = 0.5-0.8
- Effective ratio after scoring: ~10:1

**Query distribution** (70/30 rule):
- 70% of results from video transcripts
- 30% from external sources
- Final perceived ratio: ~2:1 (videos feel dominant)

---

## 6. Implementation Plan

### Phase 1: Infrastructure (Week 1)
- [ ] Create database tables (external_sources, external_content, content_authors, content_insights)
- [ ] Implement scoring algorithms
- [ ] Build fetching framework (RSS parser, API client)
- [ ] Add rate limiting and deduplication

### Phase 2: Tier 1 Integration (Week 2)
- [ ] Configure 8 Tier 1 sources
- [ ] Build Hacker News API fetcher
- [ ] Build RSS feed fetcher (7 sources)
- [ ] Test quality filters and rate limits

### Phase 3: Intelligence Extraction (Week 3)
- [ ] Extend insight extraction to external content
- [ ] Implement source attribution in all insights
- [ ] Update meta-intelligence aggregator
- [ ] Test weighted queries (70/30 distribution)

### Phase 4: UI Integration (Week 4)
- [ ] Update dashboard to show source badges
- [ ] Add filtering by source type
- [ ] Display trust scores
- [ ] Create source management page

### Phase 5: Monitoring & Tuning (Ongoing)
- [ ] Monitor database growth
- [ ] Adjust weights based on user feedback
- [ ] Tune rate limits
- [ ] Add/remove sources

---

## 7. Monitoring & Quality Control

### 7.1 Daily Metrics

```sql
-- Daily fetch report
SELECT
  s.name,
  s.source_type,
  COUNT(c.content_id) as articles_today,
  AVG(c.final_score) as avg_score,
  SUM(CASE WHEN c.is_processed = 1 THEN 1 ELSE 0 END) as processed
FROM external_sources s
LEFT JOIN external_content c ON s.source_id = c.source_id
WHERE DATE(c.fetched_at) = DATE('now')
GROUP BY s.source_id
ORDER BY articles_today DESC;
```

### 7.2 Quality Dashboard

Track:
- Articles fetched per source
- Average scores per source
- Ratio of video:external in intelligence
- Top authors by authority score
- Duplicate detection rate

### 7.3 Alerts

```python
QUALITY_ALERTS = {
    "external_ratio_too_high": 0.4,    # Alert if external > 40% in results
    "source_score_too_low": 0.3,       # Alert if source avg score < 0.3
    "duplicate_rate_high": 0.2,        # Alert if >20% duplicates detected
}
```

---

## 8. Example Queries

### Get Weighted Intelligence

```sql
-- Get top 50 insights with proper source distribution
WITH video_insights AS (
  SELECT i.*, 'video' as source_type, 1.0 as weight
  FROM insights i
  JOIN videos v ON i.video_id = v.video_id
  ORDER BY i.actionability_score DESC
  LIMIT 35  -- 70% of 50
),
external_insights AS (
  SELECT i.*, 'external' as source_type, c.final_score as weight
  FROM content_insights i
  JOIN external_content c ON i.content_id = c.content_id
  ORDER BY c.final_score DESC, c.published_at DESC
  LIMIT 15  -- 30% of 50
)
SELECT * FROM video_insights
UNION ALL
SELECT * FROM external_insights
ORDER BY weight DESC, published_at DESC;
```

### Find Content by Source

```sql
-- Get all Hacker News posts with high engagement
SELECT
  c.title,
  c.url,
  c.upvotes,
  c.published_at,
  c.final_score
FROM external_content c
WHERE c.source_id = 'hackernews'
  AND c.final_score >= 0.7
ORDER BY c.upvotes DESC
LIMIT 20;
```

### Author Leaderboard

```sql
-- Top authors by authority
SELECT
  a.author_name,
  a.authority_score,
  a.total_articles,
  a.avg_engagement,
  a.expert_in_topics
FROM content_authors a
ORDER BY a.authority_score DESC
LIMIT 20;
```

---

## Summary

**Key Guarantees**:
1. ✅ Video transcripts always dominate (70% of results, weight = 1.0)
2. ✅ Every piece of content tracks source and author
3. ✅ Scoring system prevents low-quality flooding
4. ✅ Rate limits control daily volume
5. ✅ Metadata-rich for filtering and ranking
6. ✅ Quality over quantity (filters ensure only valuable content)

**Starting Point**: 8 Tier 1 sources, ~130 articles/day, heavily filtered and weighted

**Expansion Path**: Add Tier 2 sources gradually, monitor quality metrics

**Safety**: Can disable any source instantly if quality drops
