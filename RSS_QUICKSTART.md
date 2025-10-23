# RSS News Collection - Quick Start Guide

## ✅ What's Complete

You now have a fully working RSS news collection pipeline that:
- Fetches from 7 high-quality sources (TechCrunch, HubSpot, Seth Godin, etc.)
- Filters and scores articles automatically
- Stores in Railway PostgreSQL database
- Creates JSON backups for safety
- Ready for daily automation

---

## 📊 Current Status

**Database**: 24 articles collected from 6/7 sources
- Seth Godin's Blog: 5 articles (avg score: 0.69)
- Neil Patel Blog: 5 articles (avg score: 0.60)
- Social Media Examiner: 5 articles (avg score: 0.56)
- TechCrunch AI: 3 articles (avg score: 0.65)
- HubSpot Blog: 3 articles (avg score: 0.69)
- Small Business Trends: 3 articles (avg score: 0.60)

---

## 🚀 Quick Commands

### Collect News

```bash
# Test mode (3 from each source)
python3 scripts/rss_news_collector.py --test

# Single source
python3 scripts/rss_news_collector.py --source techcrunch --limit 10

# All sources (recommended for daily run)
python3 scripts/rss_news_collector.py --source all --limit 20
```

### View Articles

```bash
# Recent articles
python3 scripts/query_rss_articles.py --recent 20

# By source (with stats)
python3 scripts/query_rss_articles.py --by-source

# Top scored
python3 scripts/query_rss_articles.py --top 10
```

---

## 📁 Key Files

**Scripts** (all in `/scripts/`):
- `rss_news_collector.py` - Main collector
- `query_rss_articles.py` - Query tool
- `setup_rss_database.py` - Schema setup (already run)

**Data**:
- `/data/rss_news/` - JSON backups
- Railway PostgreSQL - Live database

**Docs**:
- `docs/CONTENT_SOURCES_ARCHITECTURE.md` - Full architecture
- `docs/RSS_NEWS_COLLECTION_COMPLETE.md` - Implementation details
- `config/content_sources_catalog.json` - Source catalog (76 total sources)

---

## 🔄 Daily Automation (Recommended)

Add to cron for daily collection:

```bash
# Every day at 8am - collect 20 articles from each source
0 8 * * * cd /Users/yourox/AI-Workspace && python3 scripts/rss_news_collector.py --source all --limit 20
```

Or manually run when needed.

---

## 📈 What's Next (Optional)

1. **Add Hacker News API** - Higher quality tech news
2. **Extract Intelligence** - Auto-identify trends/tools/playbooks
3. **Full Text Scraping** - Get complete articles (not just summaries)
4. **Author Tracking** - Build authority scores
5. **Expand Sources** - 69 more sources ready in catalog

---

## 🎯 Integration Path

The RSS articles are stored separately from video transcripts:
- **Videos**: Primary source (weight 1.0)
- **RSS**: Supplementary (weight 0.5-0.7)

When querying for intelligence, use weighted distribution (70/30) as per architecture.

---

## 🐛 Troubleshooting

**No articles collected?**
- Check RSS feed URLs are still valid
- Adjust quality filters (min_word_count)
- Check date range (max 30 days old)

**Database errors?**
- Verify `RAILWAY_DATABASE_URL` in .env
- Run `python3 scripts/setup_rss_database.py` to reset schema

**SSL errors?**
- Already fixed with requests library
- Certificates updated automatically

---

## ✨ Success Metrics

From latest collection:
- ✅ 24 articles collected
- ✅ 6/7 sources active (Moz filtered out - too old)
- ✅ Avg score: 0.60-0.69
- ✅ Zero errors
- ✅ <10 sec collection time

**Status**: Production Ready 🎉
