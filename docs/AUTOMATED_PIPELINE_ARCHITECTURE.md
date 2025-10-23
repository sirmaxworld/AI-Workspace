# Automated Content Pipeline Architecture

**Created**: 2025-10-17
**Status**: Phase 1 Complete (RSS), Phase 2 In Design

---

## Overview

Automated system for daily/weekly collection and enrichment of content from multiple sources. Designed for scheduled execution (cron) with comprehensive logging and error handling.

---

## Architecture

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  AUTOMATED CONTENT PIPELINE                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │   Daily/Weekly Scheduler        │
            │   (Cron or Task Scheduler)      │
            └─────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ RSS Feeds    │  │ YouTube      │  │ GitHub       │
    │ Collection   │  │ Channels     │  │ Repos        │
    └──────────────┘  └──────────────┘  └──────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                   ┌─────────────────────┐
                   │  Railway PostgreSQL  │
                   │  (Raw Content)       │
                   └─────────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Enrichment Layer   │
                   │  (AI Intelligence)  │
                   └─────────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Aggregation Layer  │
                   │  (Meta-Intelligence)│
                   └─────────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  TubeDB UI / API    │
                   │  (User Access)      │
                   └─────────────────────┘
```

---

## Content Sources

### 1. RSS News Feeds (✅ Complete)

**Sources**: 7 Tier 1 sources
- TechCrunch AI
- HubSpot Blog
- Seth Godin's Blog
- Neil Patel Blog
- Social Media Examiner
- Small Business Trends
- Moz Blog

**Schedule**: Daily
**Script**: `scripts/rss_news_collector.py`
**Storage**: `external_content` table

**Collection Stats** (Historical):
- Total articles: 95
- Date range: Last 6 months
- Storage: Railway PostgreSQL + JSON backup

### 2. YouTube Channels (🚧 In Progress)

**Sources**: Business intelligence channels
- Lenny's Podcast
- Y Combinator
- SaaStr
- *76 channels total in catalog*

**Schedule**: Weekly
**Script**: `scripts/youtube_bi_enricher_hybrid.py`
**Storage**: `videos` table

**Status**: Manual collection working, automation pending

### 3. GitHub Repositories (🚧 Planned)

**Sources**:
- YC companies
- MCP servers
- Open source projects

**Schedule**: Weekly
**Script**: `scripts/github_repo_collector.py`
**Storage**: Custom tables

**Status**: Collector exists, needs integration

### 4. MCP Servers (🚧 Planned)

**Sources**: NPM registry
**Schedule**: Weekly
**Script**: `scripts/import_npm_mcp_servers.py`
**Storage**: Custom tables

**Status**: Collector exists, needs integration

---

## Scheduling Strategy

### Daily Schedule (High Priority)

```bash
# 8:00 AM - RSS News Collection
0 8 * * * cd /Users/yourox/AI-Workspace && python3 scripts/automated_content_pipeline.py --mode daily

# Components:
# - Collect RSS feeds (20 articles/source)
# - Quick enrichment pass
# - Status check
```

**Duration**: ~5 minutes
**Articles**: ~100-150

### Weekly Schedule (Full Pipeline)

```bash
# Sunday 2:00 AM - Full Collection
0 2 * * 0 cd /Users/yourox/AI-Workspace && python3 scripts/automated_content_pipeline.py --mode weekly

# Components:
# - RSS feeds (50 articles/source)
# - YouTube channels (new videos)
# - GitHub repositories (updates)
# - MCP servers (new releases)
# - Full enrichment
# - Aggregation and analysis
```

**Duration**: ~30 minutes
**Content**: ~500+ items

### Monthly Maintenance

```bash
# First of month - Cleanup
0 3 1 * * cd /Users/yourox/AI-Workspace && python3 scripts/cleanup_old_content.py
```

**Tasks**:
- Delete expired content (TTL)
- Archive old data
- Database optimization
- Generate monthly report

---

## Error Handling

### Retry Strategy

```python
# Automatic retries for transient failures
MAX_RETRIES = 3
RETRY_DELAY = 60  # seconds

# Exponential backoff for API rate limits
BACKOFF_MULTIPLIER = 2
```

### Failure Modes

1. **Source Unavailable**
   - Action: Skip, log warning
   - Continue with other sources
   - Retry in next run

2. **Database Error**
   - Action: Rollback transaction
   - Save to JSON backup
   - Alert admin

3. **Enrichment Failure**
   - Action: Mark content as not processed
   - Queue for manual review
   - Continue collection

4. **Timeout**
   - Action: Cancel operation
   - Log partial results
   - Resume from checkpoint

---

## Logging System

### Log Levels

- **INFO**: Normal operations
- **WARN**: Non-critical issues
- **ERROR**: Failures requiring attention
- **CRITICAL**: System-wide failures

### Log Files

```
logs/pipeline/
├── pipeline_20251017.log      # Daily log
├── errors_20251017.log         # Error-only log
└── summary_20251017.json       # Structured summary
```

### Log Format

```
[2025-10-17 08:00:15] [INFO] 🚀 Starting daily pipeline
[2025-10-17 08:00:16] [INFO] 📰 Collecting RSS feeds
[2025-10-17 08:02:45] [INFO] ✅ RSS collection: 95 articles
[2025-10-17 08:02:46] [WARN] ⚠️  YouTube API rate limit
[2025-10-17 08:02:47] [INFO] ⏭️  Skipping YouTube, will retry
[2025-10-17 08:05:30] [INFO] ✅ Daily pipeline complete
```

---

## Monitoring & Alerts

### Health Checks

**Daily Checks**:
- Collection success rate > 90%
- Database connection healthy
- Disk space available
- API quotas remaining

**Weekly Reports**:
- Total content collected
- Source-by-source breakdown
- Error rate trends
- Storage growth

### Alert Conditions

**Critical**:
- Pipeline fails 3 times in row
- Database connection lost
- Disk space < 10%

**Warning**:
- Single source fails
- Collection < 50% of expected
- Enrichment backlog > 1000 items

---

## Data Quality

### Quality Scoring

All content scored 0.0-1.0 based on:
- **Source weight** (0.5-1.0)
- **Content quality** (length, structure)
- **Freshness** (time decay)
- **Engagement** (upvotes, views if available)

### Filtering Rules

**Minimum Thresholds**:
- Word count: 20-50 words (source dependent)
- Age: < 180 days
- Score: > 0.3

**Deduplication**:
- URL uniqueness
- Title similarity (>90% = duplicate)
- Content hash matching

---

## Storage Strategy

### Hot Storage (Railway PostgreSQL)

**Retention**: 6 months
**Content**:
- Recent articles (last 180 days)
- High-scored content (> 0.7)
- All enriched/processed items

### Warm Storage (JSON Archives)

**Retention**: Indefinite
**Content**:
- Full article backups
- Collection metadata
- Processing history

**Location**: `/data/rss_news/`, `/data/youtube_channels/`

### Cold Storage (Future)

**Retention**: Indefinite
**Content**:
- Aged-out content
- Low-scored items
- Historical snapshots

**Technology**: S3 or similar

---

## Enrichment Pipeline

### Stage 1: Content Collection

- Fetch raw content
- Apply quality filters
- Store in database
- Create JSON backup

### Stage 2: Intelligence Extraction

**For Articles**:
- Extract key insights
- Identify tools/trends/playbooks
- Score actionability
- Tag with categories

**For Videos**:
- Transcript processing
- Segment identification
- Quote extraction
- Timestamp mapping

### Stage 3: Aggregation

**Cross-Source Analysis**:
- Trend detection
- Topic clustering
- Sentiment analysis
- Timeline building

**Meta-Intelligence**:
- Pattern recognition
- Opportunity identification
- Market analysis
- Competitive insights

---

## API Integration

### Future: RESTful API

```
GET /api/content/recent
GET /api/content/by-source/{source_id}
GET /api/content/search?q={query}
GET /api/insights/trending
GET /api/pipeline/status
POST /api/pipeline/trigger
```

### Webhooks

**Trigger on**:
- New high-scored content (> 0.8)
- Critical errors
- Weekly report ready

---

## Performance Targets

### Collection Speed

- RSS: < 2 sec per source
- YouTube: < 5 sec per channel
- GitHub: < 3 sec per repo

**Total**: Daily pipeline < 5 min

### Resource Usage

- CPU: < 20% sustained
- Memory: < 500 MB
- Disk I/O: Minimal (batch writes)
- Network: Respectful rate limiting

### Reliability

- Uptime: 99.5%
- Success rate: 95%
- Data accuracy: 99%

---

## Phase Roadmap

### Phase 1: RSS Foundation (✅ Complete)

- [x] RSS collector
- [x] Database schema
- [x] Historical collection (6 months)
- [x] Query tools

### Phase 2: Automation (In Progress)

- [x] Pipeline orchestrator
- [ ] Cron setup
- [ ] Logging system
- [ ] Error handling

### Phase 3: Multi-Source (Planned)

- [ ] YouTube integration
- [ ] GitHub integration
- [ ] MCP integration
- [ ] Unified enrichment

### Phase 4: Intelligence (Planned)

- [ ] Auto-enrichment
- [ ] Trend detection
- [ ] Meta-aggregation
- [ ] API access

### Phase 5: Scale (Future)

- [ ] Distributed processing
- [ ] Queue system (Redis)
- [ ] Cold storage
- [ ] Advanced analytics

---

## Configuration Files

### Pipeline Config

**Location**: `config/pipeline_config.json`

```json
{
  "sources": {
    "rss": {
      "enabled": true,
      "schedule": "daily",
      "limit": 20
    },
    "youtube": {
      "enabled": false,
      "schedule": "weekly",
      "channels": []
    }
  },
  "enrichment": {
    "enabled": true,
    "batch_size": 50
  },
  "storage": {
    "ttl_days": 180,
    "backup": true
  }
}
```

### Cron Setup

**File**: `crontab` or `launchd` plist

```bash
# RSS Daily Collection
0 8 * * * cd /Users/yourox/AI-Workspace && python3 scripts/automated_content_pipeline.py --mode daily >> logs/cron.log 2>&1

# Weekly Full Pipeline
0 2 * * 0 cd /Users/yourox/AI-Workspace && python3 scripts/automated_content_pipeline.py --mode weekly >> logs/cron.log 2>&1
```

---

## Testing Strategy

### Unit Tests

- Individual collectors
- Database operations
- Scoring algorithms
- Quality filters

### Integration Tests

- End-to-end pipeline
- Multi-source collection
- Error recovery
- Data validation

### Load Tests

- 1000+ articles
- Concurrent operations
- Database performance
- Memory usage

---

## Summary

**Current Status**: Phase 1 complete, Phase 2 in progress

**What Works**:
- ✅ RSS collection (7 sources)
- ✅ Database storage
- ✅ Historical data (95 articles)
- ✅ Quality filtering
- ✅ Query tools

**Next Steps**:
1. Set up cron for daily RSS collection
2. Implement comprehensive logging
3. Add YouTube integration
4. Build enrichment layer
5. Create aggregation pipeline

**Goal**: Fully automated, multi-source intelligence pipeline running daily with minimal manual intervention.
