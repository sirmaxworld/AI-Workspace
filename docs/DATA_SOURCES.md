# 🌐 Affordable Data Sources & APIs for Knowledge Base

## 📊 Overview
This document lists all affordable data sources and APIs for building your multi-domain knowledge bases.

---

## 🔍 Search & Web Scraping APIs

### **1. Tavily AI** ⭐ RECOMMENDED
- **Purpose**: AI-powered research API
- **Cost**: **1,000 searches/month FREE**, then $1 per 1,000 searches
- **Best for**: Academic research, comprehensive web searches
- **Features**:
  - Returns cleaned, structured data
  - Filters for high-quality sources
  - Citation extraction
- **Setup**: `pip install tavily-python`
- **API Key**: Get from https://tavily.com

### **2. Brave Search API** ⭐ RECOMMENDED
- **Purpose**: Privacy-focused search engine API
- **Cost**: **2,000 queries/month FREE**
- **Best for**: General web searches, news, images
- **Features**:
  - No tracking
  - Clean results
  - News, web, images, videos
- **Setup**: Already available via CrewAI tools
- **API Key**: Get from https://brave.com/search/api/

### **3. Firecrawl** 🔥
- **Purpose**: Web scraping & crawling
- **Cost**: **500 credits/month FREE**, $49/month for 10k pages
- **Best for**: Crawling entire websites, blog archives
- **Features**:
  - Converts any webpage to markdown
  - Crawls entire sites
  - Extracts structured data
- **Setup**: `pip install firecrawl-py`
- **API Key**: Get from https://firecrawl.dev

### **4. Jina AI Reader** 💎
- **Purpose**: Convert any URL to clean markdown/LLM-ready format
- **Cost**: **FREE** (1M requests/month free tier)
- **Best for**: Reading blog posts, documentation, articles
- **Usage**: Simply prepend `https://r.jina.ai/` to any URL
- **Example**: `https://r.jina.ai/https://example.com`
- **No API key needed!**

### **5. Exa (formerly Metaphor)** 🎯
- **Purpose**: Semantic search engine for the web
- **Cost**: **1,000 searches/month FREE**, $20/month for 10k searches
- **Best for**: Finding similar content, research papers, blog posts
- **Features**:
  - Neural search (understands meaning, not just keywords)
  - Find similar to URL
  - Filter by domain, date
- **Setup**: `pip install exa-py`
- **API Key**: Get from https://exa.ai

---

## 📚 Academic & Research APIs

### **6. arXiv API** 📖 FREE
- **Purpose**: Access to 2+ million research papers
- **Cost**: **100% FREE**
- **Best for**: ML, AI, robotics, physics research papers
- **Features**:
  - Full paper access
  - Metadata extraction
  - Daily updates
- **Setup**: `pip install arxiv`
- **No API key needed**

### **7. Semantic Scholar API** 🎓 FREE
- **Purpose**: AI-powered academic search
- **Cost**: **100% FREE** (rate limited)
- **Best for**: Paper recommendations, citations, research graphs
- **Features**:
  - 200M+ papers
  - Citation analysis
  - Research influence metrics
- **Setup**: `pip install semanticscholar`
- **Optional API key for higher limits**: https://semanticscholar.org/product/api

### **8. PubMed API** 🏥 FREE
- **Purpose**: Biomedical and life sciences research
- **Cost**: **100% FREE**
- **Best for**: Mental health research, psychology, neuroscience
- **Setup**: `pip install biopython`
- **No API key needed**

### **9. OpenAlex** 🌍 FREE
- **Purpose**: Open catalog of scholarly papers
- **Cost**: **100% FREE**
- **Best for**: Cross-disciplinary research, citation graphs
- **Features**:
  - 250M+ works
  - Open access
  - No rate limits
- **Setup**: REST API or Python client
- **No API key needed**: https://openalex.org

---

## 📱 Social Media APIs

### **10. Reddit API (PRAW)** 🤖
- **Purpose**: Reddit data collection
- **Cost**: **FREE** (with rate limits)
- **Best for**: Community discussions, sentiment analysis, trends
- **Setup**: `pip install praw`
- **API Key**: Create app at https://reddit.com/prefs/apps

### **11. Twitter/X API v2** 🐦
- **Purpose**: Twitter data collection
- **Cost**: **Basic tier FREE** (1,500 posts/month)
- **Best for**: Trend monitoring, sentiment analysis
- **Limits**: Restricted on free tier
- **Setup**: `pip install tweepy`
- **API Key**: https://developer.twitter.com

### **12. Hacker News API** 💬 FREE
- **Purpose**: Tech community discussions
- **Cost**: **100% FREE**
- **Best for**: Tech trends, startup discussions, AI news
- **No API key needed**
- **Endpoint**: https://hacker-news.firebaseio.com/v0/

---

## 🎥 YouTube & Video APIs

### **13. YouTube Data API** 📺
- **Purpose**: YouTube metadata, search, channel info
- **Cost**: **FREE** (10,000 quota units/day)
- **Best for**: Finding videos, channel stats, metadata
- **Setup**: `pip install google-api-python-client`
- **API Key**: Google Cloud Console

### **14. youtube-transcript-api** 📝 FREE
- **Purpose**: Extract video transcripts
- **Cost**: **100% FREE** (no API key needed)
- **Best for**: Getting video captions/transcripts
- **Setup**: Already installed in your workspace
- **No limits!**

### **15. Whisper API (OpenAI)** 🎙️
- **Purpose**: Audio transcription for videos without captions
- **Cost**: **$0.006/minute** (~$0.36/hour of video)
- **Best for**: Videos without captions
- **Setup**: Via OpenAI API
- **API Key**: Your existing OpenAI key

---

## 📰 News & RSS APIs

### **16. NewsAPI** 📰
- **Purpose**: News articles from 150k+ sources
- **Cost**: **100 requests/day FREE**, $449/month for unlimited
- **Best for**: Industry news, trend monitoring
- **Setup**: `pip install newsapi-python`
- **API Key**: https://newsapi.org

### **17. RSS Feeds** 📡 FREE
- **Purpose**: Blog posts, news updates
- **Cost**: **100% FREE**
- **Best for**: Following specific blogs/sites
- **Setup**: `pip install feedparser`
- **No API key needed**

---

## 💾 Data Storage & Vector DBs

### **18. Qdrant** 🎯
- **Purpose**: Vector database for embeddings
- **Cost**: **FREE for local** or $25/month cloud
- **Best for**: Storing and searching your knowledge base
- **Already installed in your workspace**

### **19. ChromaDB** 🎨
- **Purpose**: Alternative vector database
- **Cost**: **FREE** (local)
- **Best for**: Simpler setup than Qdrant
- **Setup**: `pip install chromadb`

---

## 🤖 LLM & Embedding APIs

### **20. OpenAI API** (Already have)
- **Embeddings**: text-embedding-3-small ($0.02/1M tokens)
- **Best value for embeddings**

### **21. Anthropic API** (Already have)
- **Claude**: For summarization, analysis
- **Your current LLM**

### **22. Cohere** 💚
- **Purpose**: Alternative embeddings
- **Cost**: **FREE tier available**
- **Best for**: Multilingual embeddings
- **Setup**: `pip install cohere`

---

## 🎁 Recommended Stack for Your Use Case

### **Tier 1: Must-Have (All Free or Very Cheap)**
1. ✅ **Jina AI Reader** - FREE web scraping
2. ✅ **Brave Search API** - 2,000 free searches/month
3. ✅ **Tavily AI** - 1,000 free AI searches/month
4. ✅ **arXiv API** - FREE research papers
5. ✅ **YouTube Transcript API** - FREE video transcripts
6. ✅ **Reddit API (PRAW)** - FREE social sentiment
7. ✅ **Semantic Scholar** - FREE academic search

### **Tier 2: Worth Paying For**
1. 💰 **Firecrawl** - $49/month (for crawling entire sites)
2. 💰 **Exa** - $20/month (for semantic search)

### **Total Monthly Cost: $0-69/month**
- **Free tier only**: $0/month
- **With premium tools**: ~$69/month

---

## 🚀 Next Steps

1. **Get API Keys**:
   ```bash
   # Add to .env file
   TAVILY_API_KEY=your_key_here
   BRAVE_SEARCH_API_KEY=your_key_here
   FIRECRAWL_API_KEY=your_key_here  # if using
   EXA_API_KEY=your_key_here  # if using
   REDDIT_CLIENT_ID=your_id_here
   REDDIT_CLIENT_SECRET=your_secret_here
   ```

2. **Install Libraries**:
   ```bash
   pip install tavily-python firecrawl-py exa-py praw arxiv semanticscholar feedparser
   ```

3. **Test Each Service**:
   ```bash
   python3 test_data_sources.py
   ```

---

## 📊 Comparison Table

| Service | Free Tier | Monthly Cost | Best For |
|---------|-----------|-------------|----------|
| Jina AI | 1M requests | $0 | Web scraping |
| Brave | 2k searches | $0 | General search |
| Tavily | 1k searches | $0-99 | AI research |
| arXiv | Unlimited | $0 | Research papers |
| YouTube Transcript | Unlimited | $0 | Video transcripts |
| Firecrawl | 500 pages | $0-49 | Site crawling |
| Exa | 1k searches | $0-20 | Semantic search |
| Reddit API | Rate limited | $0 | Social media |

---

**Total Cost for All Premium Tiers: ~$170/month**
**Recommended Starter Cost: $0-20/month** (Brave + Tavily + Exa free tiers)


---

## 🔗 Knowledge Base & Collaboration Tool Connectors

### **23. Notion MCP Server** 📝
- **Purpose**: Connect to Notion databases and pages
- **Cost**: Notion API is **FREE** with Notion account
- **Best for**: Client knowledge bases, project documentation, meeting notes
- **Features**:
  - Read/write to Notion databases
  - Search across workspaces
  - Access page content and metadata
- **Setup**: MCP server available via `@modelcontextprotocol/server-notion`
- **API Key**: Get from https://developers.notion.com

### **24. Confluence MCP Server** 🏢
- **Purpose**: Enterprise wiki and documentation
- **Cost**: Based on Confluence plan (starts at $5.75/user/month)
- **Best for**: Corporate knowledge bases, technical documentation
- **Features**:
  - Search across spaces
  - Access page hierarchies
  - Extract documentation
- **Setup**: MCP server integration via Atlassian API
- **API Key**: Confluence API token

### **25. Obsidian Local Vault** 🧠
- **Purpose**: Local markdown knowledge base
- **Cost**: **FREE** (local files)
- **Best for**: Personal knowledge management, research notes
- **Features**:
  - Full-text search
  - Markdown files
  - Graph relationships
- **Setup**: Direct file system access via MCP
- **No API key needed** - uses local file access

### **26. Linear MCP Server** ⚡
- **Purpose**: Project management and issue tracking
- **Cost**: Free tier available, $8/user/month for teams
- **Best for**: Client project tracking, task management
- **Features**:
  - Issue tracking
  - Project roadmaps
  - Team workflows
- **Setup**: MCP server via Linear API
- **API Key**: https://linear.app/settings/api

### **27. Airtable API** 🗄️
- **Purpose**: Flexible database/spreadsheet hybrid
- **Cost**: **FREE** tier (1,200 records/base), $20/month unlimited
- **Best for**: Client databases, CRM, project tracking
- **Features**:
  - Structured data storage
  - API access to bases
  - Automations
- **Setup**: `pip install pyairtable`
- **API Key**: https://airtable.com/account

---

## 📈 Business Intelligence & Market Research APIs

### **28. Statista** 📊
- **Purpose**: Statistics and market data
- **Cost**: **Starting at $59/month** for basic access
- **Best for**: Market statistics, industry reports, demographic data
- **Features**:
  - 1M+ statistics
  - Industry forecasts
  - Consumer insights
- **API**: Available with premium plans
- **Website**: https://statista.com

### **29. IBISWorld** 🌐
- **Purpose**: Industry research and analysis
- **Cost**: **Starting at $1,995/year** per industry
- **Best for**: Deep industry analysis, competitive landscape
- **Features**:
  - 700+ industry reports
  - Market size data
  - Trend analysis
- **API**: Contact for enterprise access
- **Website**: https://ibisworld.com

### **30. Euromonitor International** 🌍
- **Purpose**: Global market research
- **Cost**: **Custom pricing** (expensive - enterprise level)
- **Best for**: International market data, consumer trends
- **Features**:
  - Global market data
  - Consumer insights
  - Industry forecasts
- **API**: Available with subscription
- **Website**: https://euromonitor.com

### **31. Grand View Research** 📑 AFFORDABLE
- **Purpose**: Market research reports
- **Cost**: **Reports from $2,500-5,000** (one-time purchase)
- **Best for**: Specific industry reports at lower cost
- **Features**:
  - Industry-specific reports
  - Market sizing
  - Competitive analysis
- **No API** - downloadable PDF reports
- **Website**: https://grandviewresearch.com

### **32. MarketResearch.com** 💼
- **Purpose**: Aggregated market research
- **Cost**: **Reports from $350+** per report
- **Best for**: Budget-friendly industry reports
- **Features**:
  - 1M+ reports from various publishers
  - Wide industry coverage
  - Instant download
- **Website**: https://marketresearch.com

### **33. Google Trends API** 📈 FREE
- **Purpose**: Search trend analysis
- **Cost**: **100% FREE** (unofficial API)
- **Best for**: Market sentiment, trending topics, demand analysis
- **Features**:
  - Interest over time
  - Regional interest
  - Related queries
- **Setup**: `pip install pytrends`
- **No API key needed**

---

## 🏢 Company Data & Business Intelligence APIs

### **34. Crunchbase API** 🚀
- **Purpose**: Company funding, investors, acquisitions
- **Cost**: **Starting at $29/month** (basic), $99/month (pro)
- **Best for**: Startup research, funding data, investor tracking
- **Features**:
  - 3M+ organizations
  - Funding rounds
  - Key people data
- **API**: Available with pro plans
- **Website**: https://crunchbase.com/enterprise

### **35. Clearbit API** 🎯
- **Purpose**: Company enrichment and intelligence
- **Cost**: **Free tier** (50 requests/month), paid starts at $99/month
- **Best for**: Company research, lead enrichment, technographics
- **Features**:
  - Company lookup by domain
  - Employee count, revenue estimates
  - Technology stack
- **Setup**: RESTful API
- **API Key**: https://clearbit.com

### **36. ZoomInfo** 📞 ENTERPRISE
- **Purpose**: B2B contact and company database
- **Cost**: **Custom pricing** (expensive - $15k+/year)
- **Best for**: B2B prospecting, contact data, org charts
- **Features**:
  - 100M+ business contacts
  - Direct dials
  - Org charts
- **API**: Available with subscription
- **Website**: https://zoominfo.com

### **37. PitchBook** 📊 ENTERPRISE
- **Purpose**: Private market intelligence
- **Cost**: **$20k-40k/year** (enterprise only)
- **Best for**: Private equity, venture capital, M&A data
- **Features**:
  - PE/VC deal data
  - Company valuations
  - Investor analysis
- **API**: Available with subscription
- **Website**: https://pitchbook.com

### **38. Apollo.io** 🎪 AFFORDABLE
- **Purpose**: B2B database and sales intelligence
- **Cost**: **FREE tier** (60 credits/month), $49/month for 12k credits
- **Best for**: Contact discovery, company research, lead generation
- **Features**:
  - 275M+ contacts
  - Company search
  - Technographics
- **API**: Available on paid plans
- **Website**: https://apollo.io

### **39. Hunter.io** 📧
- **Purpose**: Email finder and verification
- **Cost**: **FREE** (25 searches/month), $49/month for 500 searches
- **Best for**: Finding business email addresses
- **Features**:
  - Email pattern detection
  - Email verification
  - Domain search
- **API**: Available on all plans
- **Website**: https://hunter.io

### **40. BuiltWith** 🔧
- **Purpose**: Technology profiling for websites
- **Cost**: **$295/month** for API access
- **Best for**: Tech stack analysis, competitive intelligence
- **Features**:
  - Website technology detection
  - Ecommerce data
  - Trend analysis
- **API**: https://api.builtwith.com
- **Website**: https://builtwith.com

### **41. SimilarWeb** 📊
- **Purpose**: Website traffic and analytics
- **Cost**: **Free basic**, $125/month for pro
- **Best for**: Competitor analysis, traffic estimation
- **Features**:
  - Website traffic estimates
  - Traffic sources
  - Audience insights
- **API**: Available with pro plans
- **Website**: https://similarweb.com

### **42. Owler** 🦉
- **Purpose**: Company profiles and competitive intelligence
- **Cost**: **FREE tier available**, $35/month pro
- **Best for**: Competitor tracking, company news
- **Features**:
  - Company profiles
  - Competitor alerts
  - Revenue estimates
- **API**: Available with pro plans
- **Website**: https://owler.com

---

## 🏛️ Government & Open Data Sources

### **43. Data.gov** 🇺🇸 FREE
- **Purpose**: U.S. government open data
- **Cost**: **100% FREE**
- **Best for**: Economic data, demographics, public datasets
- **Features**:
  - 300k+ datasets
  - Economic indicators
  - Census data
- **No API key needed**
- **Website**: https://data.gov

### **44. World Bank Open Data** 🌍 FREE
- **Purpose**: Global development data
- **Cost**: **100% FREE**
- **Best for**: International economic data, development indicators
- **Features**:
  - Global economic data
  - Development indicators
  - Country statistics
- **API**: Open API available
- **Website**: https://data.worldbank.org

### **45. U.S. Census Bureau API** 📊 FREE
- **Purpose**: U.S. demographic and economic data
- **Cost**: **100% FREE**
- **Best for**: Population data, business statistics, economic indicators
- **Features**:
  - Population demographics
  - Business patterns
  - Economic Census
- **API Key**: Free registration
- **Website**: https://census.gov/data/developers

### **46. FRED (Federal Reserve)** 💰 FREE
- **Purpose**: U.S. economic time series data
- **Cost**: **100% FREE**
- **Best for**: Economic indicators, financial data, market trends
- **Features**:
  - 816k+ time series
  - Economic indicators
  - Historical data
- **API Key**: Free registration
- **Website**: https://fred.stlouisfed.org

---

## 🎯 Recommended Stack for smeConsulting.ai

### **Knowledge Base Integration (MCP)**
1. ✅ **Notion MCP** - Client documentation and project knowledge
2. ✅ **Airtable** - Client CRM and structured data
3. ✅ **Linear** - Project and task management
4. ✅ **Google Drive MCP** - Document storage (already have)

### **Market Research (Essential for Consulting)**
1. 💰 **Apollo.io** - $49/month (B2B data, contact research)
2. ✅ **Google Trends** - FREE (market sentiment)
3. 💰 **MarketResearch.com** - Pay per report ($350+)
4. ✅ **FRED API** - FREE (economic data)
5. ✅ **Census Bureau** - FREE (demographic data)

### **Company Intelligence (Client Research)**
1. 💰 **Clearbit** - $99/month (company enrichment)
2. 💰 **Apollo.io** - $49/month (company + contact data)
3. 💰 **Hunter.io** - $49/month (email finding)
4. ✅ **Owler** - FREE tier (competitor tracking)

### **Web Research (Already Have)**
1. ✅ **Brave Search** - FREE
2. ✅ **Tavily AI** - FREE tier
3. ✅ **Jina Reader** - FREE

---

## 💰 Cost Analysis for smeConsulting.ai

### **Phase 1: Free Tier Only ($0/month)**
- All existing free tools (Brave, Tavily, arXiv, YouTube, etc.)
- Google Trends
- FRED Economic Data
- Census Bureau
- Notion API (with existing Notion account)
- Owler free tier
- Clearbit free tier (50 requests/month)
- **Total: $0/month**

### **Phase 2: Essential Paid Tools ($150-200/month)**
- Apollo.io: $49/month (B2B intelligence)
- Clearbit Pro: $99/month (company enrichment)
- Hunter.io: $49/month (email finding)
- Airtable: $20/month (client CRM)
- Linear: $8/month (project management)
- **Total: ~$225/month**

### **Phase 3: Advanced Market Research (Pay-per-report)**
- MarketResearch.com reports: $350-2,000 per report (as needed)
- Grand View Research: $2,500-5,000 per report (as needed)
- **Cost: Variable based on client projects**

### **Phase 4: Enterprise (Not recommended initially)**
- ZoomInfo: $15k+/year
- PitchBook: $20-40k/year
- IBISWorld: $2k+/year per industry
- **Only needed for high-value enterprise clients**

---

## 🚀 Implementation Priority for smeConsulting.ai

### **Week 1: Knowledge Base Foundation**
1. Set up Notion MCP for client documentation
2. Configure Airtable for client database
3. Set up Linear for project tracking
4. Test Google Drive MCP integration

### **Week 2: Free Research Tools**
1. Integrate Google Trends API
2. Set up FRED economic data access
3. Configure Census Bureau API
4. Test Owler free tier

### **Week 3: Paid Essential Tools**
1. Subscribe to Apollo.io ($49/month)
2. Upgrade Clearbit to Pro ($99/month)
3. Subscribe to Hunter.io ($49/month)
4. Test full workflow with client research

### **Week 4: Market Research Setup**
1. Create MarketResearch.com account
2. Identify key industry reports needed
3. Budget for report purchases per project
4. Set up reporting workflow

---

## 📝 API Keys Needed for .env

```bash
# Knowledge Base Connectors
NOTION_API_KEY=your_notion_key
AIRTABLE_API_KEY=your_airtable_key
LINEAR_API_KEY=your_linear_key

# Company Intelligence
APOLLO_API_KEY=your_apollo_key
CLEARBIT_API_KEY=your_clearbit_key
HUNTER_API_KEY=your_hunter_key
OWLER_API_KEY=your_owler_key

# Market Research
GOOGLE_TRENDS_API=no_key_needed
FRED_API_KEY=your_fred_key
CENSUS_API_KEY=your_census_key

# Business Intelligence
BUILTWITH_API_KEY=your_builtwith_key  # if using
SIMILARWEB_API_KEY=your_similarweb_key  # if using
CRUNCHBASE_API_KEY=your_crunchbase_key  # if using

# Existing (already have)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
BRAVE_SEARCH_API_KEY=your_brave_key
TAVILY_API_KEY=your_tavily_key
```

---

## 🎯 Consulting-Specific Use Cases

### **Client Research Workflow**
1. **Company Discovery**: Apollo.io → Find potential clients
2. **Company Enrichment**: Clearbit → Get company details
3. **Contact Finding**: Hunter.io → Find decision makers
4. **Competitive Analysis**: Owler → Track competitors
5. **Market Context**: Google Trends + FRED → Market sizing

### **Project Research Workflow**
1. **Industry Research**: MarketResearch.com → Industry reports
2. **Economic Data**: FRED + Census → Market context
3. **Competitor Intel**: SimilarWeb + BuiltWith → Competitive landscape
4. **Academic Research**: arXiv + Semantic Scholar → Latest research
5. **Web Research**: Brave + Tavily → Current trends

### **Knowledge Management Workflow**
1. **Client Docs**: Notion → Project documentation
2. **CRM**: Airtable → Client relationships
3. **Tasks**: Linear → Project management
4. **Files**: Google Drive → Document storage
5. **Memory**: Secure Memory MCP → Confidential data

---

## 📊 Total Cost Summary

| Tier | Monthly Cost | Annual Cost | Best For |
|------|-------------|-------------|----------|
| **Free Only** | $0 | $0 | Getting started, proof of concept |
| **Essential** | $225 | $2,700 | Active consulting business |
| **+ Reports** | $225 + reports | $2,700 + $3-10k | Per-project market research |
| **Enterprise** | $4,000+ | $50k+ | Large consulting firm |

**Recommended Starting Point: $225/month ($2,700/year)**

---

## ✅ Next Actions

1. **Review this document** and identify which tools are needed first
2. **Get API keys** for free services (FRED, Census, Google Trends)
3. **Subscribe** to essential paid tools (Apollo, Clearbit, Hunter)
4. **Set up MCP servers** for Notion, Linear, Airtable
5. **Test workflows** with sample client research project
6. **Document findings** in your knowledge base

---

**Last Updated**: October 14, 2025
**Project**: smeConsulting.ai
**Location**: /Users/yourox/AI-Workspace/docs/DATA_SOURCES.md
