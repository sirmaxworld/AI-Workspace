# Content Collection Cost Analysis
## Historical Data Collection: API vs. Scraping

**Generated:** 2025-10-17
**Context:** Comparing costs for collecting 6 months of historical articles from 26 RSS sources

---

## Current RSS Collection Results

**What We Collected (Free):**
- 187 articles from 16/26 sources
- Date range: Last 1-2 months (not 6 months)
- Average: ~12 articles per active source
- Cost: $0 (using public RSS feeds)

**Why Limited Coverage:**
- RSS feeds only provide 10-50 recent items
- No historical archives available via RSS
- 10 sources had 0 articles (content too short, RSS errors, or all filtered)

**To Get True 6-Month Historical Data, We Need:**
- 26 sources × ~100 articles/source × 6 months lookback
- Estimated target: ~2,600 articles (assuming weekly publishing)

---

## Option 1: News Aggregation APIs

### NewsAPI.org
**Best for: Quick setup, broad coverage**

| Plan | Price | Historical Access | Requests/Month | Cost Per Article |
|------|-------|-------------------|----------------|------------------|
| Developer | Free | 1 month | 100/day (3,000/mo) | $0 |
| Business | $449/mo | 5 years | 250,000 | ~$0.002 |
| Advanced | $1,749/mo | 5 years | 2,000,000 | ~$0.0009 |

**Pros:**
- Simple REST API
- 150,000+ sources
- 14 languages, 55 countries
- 99.95% uptime SLA
- No infrastructure maintenance

**Cons:**
- Developer tier limited to 1 month (not enough)
- Business tier minimum $449/mo (even if we only need once)
- May not have all our specific niche sources (Seth Godin, Heinz Marketing, etc.)
- Aggregated content = may miss article metadata

**Cost Estimate for Our Use Case:**
- One-time historical collection: $449 (Business plan for 1 month)
- Ongoing monthly: $449/mo
- **Per article (2,600): $0.17/article**

---

### NewsAPI.ai
**Best for: Flexible historical search, token-based pricing**

| Plan | Price | Tokens | Historical Multiplier |
|------|-------|--------|----------------------|
| Free | $0 | 2,000 | 5x per year |
| 5K | $90/mo | 5,000 | 5x per year |
| 20K | $275/mo | 20,000 | 5x per year |

**Token Costs:**
- Recent articles (30 days): 1 token per search
- Historical articles: 5 tokens per year searched
- Example: Search 2025 H1 (6 months = 0.5 years): ~3 tokens per search

**Math for 2,600 Articles:**
- Assuming 100 articles per source = 26 searches
- 6 months back = 3 tokens per search
- Total: 26 × 3 = 78 tokens
- **BUT** each search returns max 100 articles, need pagination
- If we need 100 articles/source: ~26 searches × 3 tokens = 78 tokens
- Actually feasible with **Free plan** (2,000 tokens)!

**Pros:**
- Very cost-effective for historical data
- Token-based = pay only for what you use
- 150,000+ sources
- Can search specific date ranges

**Cons:**
- 100 articles per search limit (need multiple searches)
- Token math gets complex for large historical pulls
- Still may not have niche sources

**Cost Estimate:**
- One-time collection: $0 (Free plan covers it!)
- If need more: $90/mo for 5K tokens
- **Per article: $0/article (using free plan)**

---

## Option 2: Web Scraping Services

### Apify
**Best for: Pre-built scrapers, easy setup**

**Pricing:**
- Free: $5 credits
- Starter: $49/mo (compute units @ $0.40/GB-hour)
- Business: Custom pricing (compute @ $0.25/GB-hour)
- Additional: Proxy costs ($8/GB residential)

**Compute Estimate:**
- Scraping 26 websites: ~2-5 minutes per source = ~1-2 hours total
- Memory: 1-2 GB
- Total compute: 2-4 GB-hours = $0.80-$1.60
- Proxy bandwidth: ~500 MB = $4

**Pros:**
- 6,000+ pre-built scrapers (may have scrapers for popular sources)
- Can get ALL articles, not just RSS feed items
- Full HTML content, better metadata
- Can customize exactly what data to extract

**Cons:**
- Requires setup/coding for each source
- May hit rate limits or get blocked
- Need to maintain scrapers (sites change)
- Proxy costs add up

**Cost Estimate:**
- One-time collection: ~$5-10 (using free credits + small overage)
- Setup time: 2-4 hours (building/configuring scrapers)
- **Per article: $0.004/article**

---

### Bright Data
**Best for: Enterprise scale, reliability**

**Pricing:**
- Pay-as-you-go: $1.50 per 1,000 records
- Business: $999/mo (~1.2M records @ $0.84/1K)
- Premium: $1,999/mo (~2.5M records @ $0.79/1K)

**Pros:**
- 72M residential IPs (hard to block)
- Structured data extraction for 120+ domains
- Enterprise reliability
- Handles anti-scraping automatically

**Cons:**
- Expensive for small projects
- $500+ monthly minimums
- Overkill for 26 sources
- Weeks of configuration time

**Cost Estimate:**
- One-time collection: $3.90 (2,600 records × $1.50/1K)
- But PAYG may have minimums
- **Per article: $0.0015/article**

---

### Custom Scraping (DIY)
**Best for: Full control, cheapest long-term**

**Infrastructure Costs:**
- Hosting: $5-20/mo (Digital Ocean, AWS)
- Proxy service: $10-30/mo (optional, for rate limit avoidance)
- Development time: 8-16 hours initial setup

**Technology Stack:**
- Python + BeautifulSoup/Scrapy
- Proxy rotation (Scrapy-Proxy or Crawlera Lite)
- Database storage (already have Railway PostgreSQL)
- Schedule with cron

**Pros:**
- Full control over data extraction
- Can get exact fields we need
- One-time setup, runs forever
- Already have infrastructure (Railway)

**Cons:**
- Development time (8-16 hours)
- Maintenance required (sites change)
- Risk of getting blocked
- Need to handle edge cases

**Cost Estimate:**
- One-time setup: $0 (DIY development)
- Hosting: $0 (use existing Railway)
- Optional proxy: $10-30/mo
- **Per article: $0/article**

---

## Recommendation Matrix

| Use Case | Best Option | Cost | Time to Deploy |
|----------|-------------|------|----------------|
| **One-time 6-month backfill** | NewsAPI.ai (Free) | $0 | 2 hours |
| **Want full article content** | DIY Scraping | $0 | 16 hours |
| **Need enterprise reliability** | NewsAPI.org Business | $449/mo | 1 hour |
| **Ongoing daily collection** | Current RSS + DIY scraping gaps | $0 | 20 hours |

---

## Cost Comparison Summary

**For 2,600 Articles (6 months historical):**

| Method | One-Time Cost | Monthly Cost | Setup Time | Per Article |
|--------|--------------|--------------|------------|-------------|
| **Current RSS (free)** | $0 | $0 | Done ✅ | $0 |
| **NewsAPI.ai (free plan)** | $0 | $0 | 2 hours | $0 |
| **NewsAPI.org** | $449 | $449 | 1 hour | $0.17 |
| **Apify** | $5-10 | $49 | 4 hours | $0.004 |
| **Bright Data** | $4 | $999 | 2 weeks | $0.0015 |
| **DIY Scraping** | $0 | $0-30 | 16 hours | $0 |

---

## Recommended Approach

### Phase 1: Quick Win (2 hours)
✅ **Use NewsAPI.ai Free Plan**
- Get 2,000 tokens for free
- Search for historical articles from top 26 sources
- 6 months lookback = 3 tokens per search
- Should cover our 2,600 article target

### Phase 2: Fill Gaps with DIY (16 hours)
✅ **Build Custom Scrapers for Missing Sources**
- Target the 10 sources that RSS couldn't handle:
  - Entrepreneur, Inc.com, Moz, Copyblogger, Buffer
  - Knowledge @ Wharton, HuggingFace Blog
- Build Python scrapers for each site
- Extract full article content (not just RSS summaries)
- Run one-time backfill for 6 months

### Phase 3: Maintain with Hybrid (ongoing)
✅ **RSS + Selective Scraping**
- Keep RSS collection for daily updates (free)
- Run weekly scrapers for sources with poor RSS feeds
- Total cost: $0/month

---

## Technical Implementation Plan

### NewsAPI.ai Integration
```python
import requests

API_KEY = "your-key-here"
url = "https://newsapi.ai/api/v1/article/getArticles"

# Search HubSpot blog articles from last 6 months
params = {
    "apiKey": API_KEY,
    "sourceUri": "blog.hubspot.com",
    "dateStart": "2025-04-17",
    "dateEnd": "2025-10-17",
    "articlesCount": 100,
    "resultType": "articles"
}

response = requests.get(url, params=params)
articles = response.json()
```

**Token Usage:** 3 tokens per search (0.5 years × 5 tokens + 1 base)

### DIY Scraper Template
```python
import scrapy
from scrapy_proxy_pool import RandomProxy

class BlogSpider(scrapy.Spider):
    name = 'hubspot_blog'
    start_urls = ['https://blog.hubspot.com/marketing/archive']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_proxy_pool.RandomProxy': 100,
        }
    }

    def parse(self, response):
        for article in response.css('article.post'):
            yield {
                'title': article.css('h2::text').get(),
                'url': article.css('a::attr(href)').get(),
                'date': article.css('time::attr(datetime)').get(),
                'excerpt': article.css('p.excerpt::text').get()
            }
```

---

## Conclusion

**Best Value:** NewsAPI.ai free plan for immediate historical collection, followed by DIY scraping for long-term maintenance and full content extraction.

**Total Estimated Cost:** $0 for 2,600 articles
**Setup Time:** 18 hours total (2 for API + 16 for DIY scrapers)
**Monthly Ongoing:** $0
