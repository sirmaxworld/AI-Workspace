# Pinkbike / Cycling Intelligence Integration

Complete integration of Pinkbike.com into your knowledge base and trend analysis system.

## 🎯 Overview

This integration adds **cycling industry intelligence** from Pinkbike to your existing business intelligence platform. It captures:

- 🚵 **Product Reviews**: Mountain bikes, components, apparel
- 📊 **Field Tests**: Comparative bike testing and rankings
- 📈 **Industry Trends**: Technology adoption, geometry evolution, market shifts
- 💬 **Community Insights**: Comments with engagement metrics (likes/votes)
- ⭐ **Recommendations**: Editor picks, value winners, field test rankings
- ⚠️ **Known Issues**: Reliability, compatibility, availability problems
- 🏢 **Brand Perception**: Community sentiment on manufacturers

## 📁 Directory Structure

```
/Users/yourox/AI-Workspace/
├── domains/cycling_trends/
│   ├── config.json                       # Collection configuration
│   ├── pinkbike_collector.py            # Browserbase web scraper
│   └── pinkbike_articles.json           # Collected article metadata
├── data/
│   ├── pinkbike_articles/               # Raw article data + comments
│   │   └── {article_id}_full.json
│   └── pinkbike_insights/               # AI-extracted insights
│       └── {article_id}_insights.json
├── config/
│   └── cycling_intelligence_schema.json # Data extraction schema
├── pinkbike_intelligence_extractor.py   # AI processing pipeline
└── mcp-servers/
    └── cycling-intelligence/
        └── server.py                     # MCP query interface
```

## 🚀 Quick Start

### 1. Collect Articles from Pinkbike

```bash
# Collect 5 articles per section (reviews, field tests, news)
python3 domains/cycling_trends/pinkbike_collector.py \
  /Users/yourox/AI-Workspace/domains/cycling_trends 5

# This will:
# - Use Browserbase to bypass bot protection
# - Scrape articles + metadata + comments with likes
# - Save to data/pinkbike_articles/
```

### 2. Extract Intelligence with AI

```bash
# Process all collected articles
python3 pinkbike_intelligence_extractor.py all

# Or process specific article
python3 pinkbike_intelligence_extractor.py article-name-here

# This will:
# - Use Claude Sonnet 4 to extract structured insights
# - Analyze articles + community comments
# - Save to data/pinkbike_insights/
```

### 3. Query via MCP Server

The **Cycling Intelligence** MCP server is now available in your MCP config.

Restart your IDE/CLI to load the new server, then use these tools:

- `search_mountain_bikes()` - Search bike reviews and tests
- `search_components()` - Search component reviews
- `search_cycling_trends()` - Find industry trends
- `search_field_tests()` - Query field test results
- `search_gear_recommendations()` - Get editor picks and value winners
- `search_brand_perception()` - Community sentiment on brands
- `search_reliability_issues()` - Known product problems
- `get_database_stats()` - View data coverage

## 🔧 Configuration

### Collection Settings (`domains/cycling_trends/config.json`)

```json
{
  "pinkbike": {
    "sections": [
      "https://www.pinkbike.com/news/tags/reviews/",
      "https://www.pinkbike.com/news/tags/field-test/",
      "https://www.pinkbike.com/news/tags/reviews-and-tech/",
      "https://www.pinkbike.com/news/"
    ],
    "max_articles_per_section": 10,
    "comments_per_article": 50,
    "schedule": "daily"
  }
}
```

### Extracted Data Categories

**Products:**
- `mountain_bikes` - Full bike reviews with specs, pros/cons, sentiment
- `components` - Forks, shocks, drivetrains, brakes, wheels, tires
- `apparel_gear` - Helmets, pads, shoes, clothing

**Trends:**
- `technology_trends` - Suspension tech, geometry, drivetrain innovations
- `market_trends` - Pricing, consumer preferences, market shifts
- `geometry_trends` - Reach, stack, travel evolution

**Recommendations:**
- `editor_picks` - Staff recommendations with reasoning
- `field_test_results` - Comparative test rankings and winners
- `value_picks` - Best bang-for-buck products

**Community Intelligence:**
- `comment_sentiment` - Aggregated community opinions
- `user_validation` - Confirmation/disputes of claims
- `feature_requests` - What riders want
- `brand_perception` - Manufacturer reputation

**Industry News:**
- `product_launches` - New product announcements
- `brand_news` - Acquisitions, recalls, company updates

## 🔍 Example Queries

### Find trail bikes under $5000
```python
search_mountain_bikes(
  query="trail under 5000",
  category="trail",
  sentiment="positive"
)
```

### Check reliability of a component
```python
search_reliability_issues(
  query="SRAM XX1 Eagle",
  severity="all"
)
```

### See 2024 field test winners
```python
search_field_tests(
  query="enduro",
  year="2024"
)
```

### Brand reputation check
```python
search_brand_perception(
  brand="Santa Cruz"
)
```

## 🔄 Data Pipeline

```
Pinkbike.com
     ↓
[Browserbase Collector]
  - Articles, metadata, tags
  - Full content
  - Comments with likes/votes
     ↓
{article_id}_full.json
     ↓
[AI Intelligence Extractor]
  - Claude Sonnet 4 analysis
  - Structured data extraction
  - Sentiment analysis
     ↓
{article_id}_insights.json
     ↓
[MCP Server / API]
  - Semantic search
  - Filtering & aggregation
  - Real-time queries
     ↓
Claude Code / Frontend Access
```

## 📊 Data Quality

- **Articles**: Full text extraction with metadata
- **Comments**: Top 50 per article, sorted by engagement
- **Products**: Model names, prices, specs, pros/cons
- **Sentiment**: Positive/negative/neutral classification
- **Trends**: Stage (emerging/growing/mainstream)
- **Community**: High-engagement comments (50+ likes)

## 🔐 Rate Limiting & Ethics

The collector implements:
- 5-second delay between articles
- 10-second delay between sections
- Respectful of Pinkbike's server load
- Browserbase for legitimate access (not IP spoofing)

## 🆕 MCP Server Connection

**Added to:** `~/.cursor/mcp.json`

```json
{
  "Cycling Intelligence": {
    "type": "stdio",
    "command": "python3",
    "args": [
      "/Users/yourox/AI-Workspace/mcp-servers/cycling-intelligence/server.py"
    ],
    "env": {}
  }
}
```

**Restart your IDE** to activate the server.

## 🔗 Integration with Existing System

This cycling intelligence integrates seamlessly with your existing:

- **YouTube Business Intelligence**: Cross-reference product mentions
- **Supabase Database**: Unified storage with existing BI data
- **Vector Search (Qdrant)**: Semantic similarity across domains
- **API Server**: Unified REST API for all intelligence
- **Frontend (bi-hub)**: Display cycling data alongside YouTube insights

## 📝 Next Steps

1. ✅ **Collect Initial Data**: Run collector with 10-20 articles
2. ⏳ **Extract Insights**: Process with AI extractor
3. 🔄 **Test MCP Server**: Query via Claude Code
4. 📊 **Supabase Integration**: Create tables for cycling data
5. 🌐 **API Endpoints**: Add Pinkbike routes to REST API
6. 🎨 **Frontend**: Add cycling dashboard to bi-hub
7. ⏰ **Automation**: Schedule daily collection

## 🐛 Troubleshooting

**Browserbase Timeout:**
- Increase timeout in `pinkbike_collector.py` (default: 60s)
- Check Browserbase API key in `.env`

**No Articles Found:**
- Verify Pinkbike URL patterns haven't changed
- Check selector logic in collector
- Test single article URL manually

**AI Extraction Errors:**
- Verify ANTHROPIC_API_KEY in `.env`
- Check article content length (min 200 chars)
- Review prompt in extractor for schema match

**MCP Server Not Loading:**
- Restart IDE after config change
- Check server.py syntax: `python3 server.py`
- Verify path in mcp.json is absolute

## 📚 Related Files

- **Schema**: `/config/cycling_intelligence_schema.json`
- **Business Schema**: `/config/business_intelligence_schema.json`
- **Domain Config**: `/domains/cycling_trends/config.json`
- **MCP Config**: `~/.cursor/mcp.json`

## 🎯 Use Cases

1. **Product Research**: Compare mountain bikes across field tests
2. **Trend Analysis**: Track geometry evolution over years
3. **Community Validation**: Verify marketing claims against user feedback
4. **Reliability Tracking**: Monitor known issues with components
5. **Value Discovery**: Find best bang-for-buck products
6. **Market Intelligence**: Understand brand positioning
7. **Feature Prioritization**: See what riders are requesting

---

**Status**: ✅ Core infrastructure complete | ⏳ Testing in progress | 📈 Ready for data collection
