#!/usr/bin/env python3
"""
BI-Vault MCP Server
Comprehensive Business Intelligence Vault with AI-extracted insights

🗄️ THE INTELLIGENCE VAULT:
All transcripts, business intelligence, YC companies, enriched data, and meta-analysis

Data Sources:
1. Railway PostgreSQL: YC companies (5,487) + Video transcripts (454)
2. Local JSON: Business insights, enriched data, meta-intelligence
3. Future: RSS feeds, news feeds, domain intelligence

Provides semantic search and structured queries for:
- 📹 Video Transcripts (454 with full text)
- 🚀 YC Companies (5,487 with enrichments)
- 🛠️ Products & Tools (210+)
- 💡 Problems & Solutions (82+)
- 🎯 Startup Ideas (63+)
- 📈 Growth Tactics (64+)
- 🤖 AI Workflows (69+)
- 🎪 Target Markets (72+)
- 📊 Trends & Signals (104+)
- 🧠 Cross-video Meta-Intelligence
"""

import os
import json
import logging
import psycopg2
import psycopg2.extras
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

load_dotenv('/Users/yourox/AI-Workspace/.env')

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "BI-Vault",
    instructions="""🗄️ THE INTELLIGENCE VAULT - Your Business Intelligence Database

📊 WHAT'S INSIDE:
• 454 Video Transcripts (full-text searchable via Railway PostgreSQL)
• 5,487 Y Combinator Companies (with AI enrichments)
• 210+ Products & Tools | 82+ Problems & Solutions | 63+ Startup Ideas
• 64+ Growth Tactics | 69+ AI Workflows | 104+ Trends & Signals
• Comment Intelligence (validated user insights, high-engagement signals)
• Meta-Intelligence (cross-video patterns, expert consensus, strategy playbooks)
• Enriched Insights (quality-scored: actionability, specificity, evidence)

🎯 QUICK START (Check these resources first):
1. bi://guide - Complete query guide (READ THIS FIRST!)
2. bi://schema - Data structure reference
3. bi://tools-index - All 23 tools with examples
4. bi://stats - Database statistics

💡 COMMON USE CASES:
→ Market Research: get_meta_trends() + search_target_markets()
→ Startup Ideas: search_startup_ideas() + get_opportunity_matrix()
→ Product Discovery: get_product_ecosystem() + search_products()
→ Growth Strategies: get_strategy_playbooks() + search_growth_tactics()
→ YC Research: search_yc_companies(batch="W24", top_company=True)
→ Expert Opinions: get_expert_consensus() + search_validated_comments()

⚡ PRO TIPS:
• Start with META-intelligence tools (get_meta_*, get_strategy_playbooks, get_expert_consensus)
• Use enrichment filters for quality (min_actionability=80, min_evidence=75)
• Comment data = user validation (high likes = strong market signal)
• Empty queries work (query="") - use filters instead
• Combine tools: Start broad → drill into specifics

🔌 MODE: READ-ONLY | Railway PostgreSQL + Local JSON
📖 Full Documentation: Check bi://guide resource for detailed query patterns
"""
)

# Data directories
DATA_DIR = Path("/Users/yourox/AI-Workspace/data/business_insights")
ENRICHED_DIR = Path("/Users/yourox/AI-Workspace/data/enriched_insights")
SUMMARIES_DIR = Path("/Users/yourox/AI-Workspace/data/video_summaries")
META_DIR = Path("/Users/yourox/AI-Workspace/data/meta_intelligence")

# Database connection
DATABASE_URL = os.getenv('RAILWAY_DATABASE_URL')

def get_db_connection():
    """Get a Railway PostgreSQL connection"""
    if not DATABASE_URL:
        logger.warning("RAILWAY_DATABASE_URL not set. Railway DB features disabled.")
        return None
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


class BusinessIntelligenceDB:
    """In-memory business intelligence database with rich query capabilities"""

    def __init__(self):
        self.insights_files = []
        self.all_data = {
            'products': [],
            'problems': [],
            'startup_ideas': [],
            'growth_tactics': [],
            'ai_workflows': [],
            'target_markets': [],
            'trends': [],
            'strategies': [],
            'metrics': [],
            'quotes': [],
            'statistics': [],
            'mistakes': [],
            'comment_insights': [],
            'top_validated_comments': [],
            'comment_derived_trends': [],
            'yc_companies': [],  # Added YC companies
            'enriched_insights': [],  # Enriched insight-level metrics
            'video_summaries': [],  # Video-level summaries
        }
        self.meta_intelligence = {}  # Cross-video meta-intelligence
        self.load_all_insights()
        self.load_yc_companies()
        self.load_enriched_data()
        self.load_video_summaries()
        self.load_meta_intelligence()

    def load_all_insights(self):
        """Load all business intelligence JSON files"""
        for file_path in DATA_DIR.glob("*_insights.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    video_id = data.get('meta', {}).get('video_id', file_path.stem.replace('_insights', ''))

                    # Add video metadata to each item
                    meta = {
                        'video_id': video_id,
                        'video_title': data.get('meta', {}).get('title', ''),
                        'source_file': str(file_path)
                    }

                    # Extract and categorize all data
                    self._extract_products(data, meta)
                    self._extract_problems(data, meta)
                    self._extract_startup_ideas(data, meta)
                    self._extract_growth_tactics(data, meta)
                    self._extract_ai_workflows(data, meta)
                    self._extract_target_markets(data, meta)
                    self._extract_trends(data, meta)
                    self._extract_strategies(data, meta)
                    self._extract_metrics(data, meta)
                    self._extract_quotes(data, meta)
                    self._extract_statistics(data, meta)
                    self._extract_mistakes(data, meta)
                    self._extract_comment_insights(data, meta)
                    self._extract_top_validated_comments(data, meta)
                    self._extract_comment_derived_trends(data, meta)

                    self.insights_files.append(file_path.name)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

    def _extract_products(self, data: dict, meta: dict):
        """Extract products and tools"""
        for product in data.get('products_tools', []):
            self.all_data['products'].append({**product, **meta})

    def _extract_problems(self, data: dict, meta: dict):
        """Extract problems and solutions"""
        for problem in data.get('problems_solutions', []):
            self.all_data['problems'].append({**problem, **meta})

    def _extract_startup_ideas(self, data: dict, meta: dict):
        """Extract startup ideas"""
        for idea in data.get('startup_ideas', []):
            self.all_data['startup_ideas'].append({**idea, **meta})

    def _extract_growth_tactics(self, data: dict, meta: dict):
        """Extract growth tactics"""
        for tactic in data.get('growth_tactics', []):
            self.all_data['growth_tactics'].append({**tactic, **meta})

    def _extract_ai_workflows(self, data: dict, meta: dict):
        """Extract AI workflows"""
        for workflow in data.get('ai_workflows', []):
            self.all_data['ai_workflows'].append({**workflow, **meta})

    def _extract_target_markets(self, data: dict, meta: dict):
        """Extract target markets"""
        markets = data.get('market_intelligence', {}).get('target_markets', [])
        for market in markets:
            self.all_data['target_markets'].append({**market, **meta})

    def _extract_trends(self, data: dict, meta: dict):
        """Extract trends and signals"""
        for trend in data.get('trends_signals', []):
            self.all_data['trends'].append({**trend, **meta})

    def _extract_strategies(self, data: dict, meta: dict):
        """Extract business strategies"""
        for strategy in data.get('business_strategies', []):
            self.all_data['strategies'].append({**strategy, **meta})

    def _extract_metrics(self, data: dict, meta: dict):
        """Extract metrics and KPIs"""
        for metric in data.get('metrics_kpis', []):
            self.all_data['metrics'].append({**metric, **meta})

    def _extract_quotes(self, data: dict, meta: dict):
        """Extract actionable quotes"""
        for quote in data.get('actionable_quotes', []):
            self.all_data['quotes'].append({**quote, **meta})

    def _extract_statistics(self, data: dict, meta: dict):
        """Extract key statistics"""
        for stat in data.get('key_statistics', []):
            self.all_data['statistics'].append({**stat, **meta})

    def _extract_mistakes(self, data: dict, meta: dict):
        """Extract mistakes to avoid"""
        for mistake in data.get('mistakes_to_avoid', []):
            self.all_data['mistakes'].append({**mistake, **meta})

    def _extract_comment_insights(self, data: dict, meta: dict):
        """Extract comment-derived insights"""
        for insight in data.get('comment_insights', []):
            self.all_data['comment_insights'].append({**insight, **meta})

    def _extract_top_validated_comments(self, data: dict, meta: dict):
        """Extract high-engagement validated comments"""
        for comment in data.get('top_validated_comments', []):
            self.all_data['top_validated_comments'].append({**comment, **meta})

    def _extract_comment_derived_trends(self, data: dict, meta: dict):
        """Extract trends identified from comments"""
        for trend in data.get('comment_derived_trends', []):
            self.all_data['comment_derived_trends'].append({**trend, **meta})

    def load_yc_companies(self):
        """Load Y Combinator companies from Railway PostgreSQL"""
        try:
            conn = get_db_connection()
            if not conn:
                logger.warning("Railway DB not available. Trying JSON fallback...")
                self._load_yc_companies_from_json()
                return

            cursor = conn.cursor()

            # Load all companies with enrichment data
            cursor.execute("""
                SELECT
                    slug, name, yc_id, batch, website,
                    phase1_complete, phase8_complete,
                    web_data, ai_insights,
                    enriched_at
                FROM yc_companies_enriched
                ORDER BY name;
            """)

            companies = cursor.fetchall()

            # Add to all_data
            for company_row in companies:
                company = dict(company_row)

                # Convert JSONB to dict
                if company.get('web_data'):
                    company['web_data'] = dict(company['web_data'])
                if company.get('ai_insights'):
                    company['ai_insights'] = dict(company['ai_insights'])

                # Add metadata
                company['source'] = 'railway_postgresql'
                company['data_source'] = 'Railway PostgreSQL'

                self.all_data['yc_companies'].append(company)

            cursor.close()
            conn.close()

            logger.info(f"Loaded {len(companies)} YC companies from Railway PostgreSQL")

        except Exception as e:
            logger.error(f"Error loading YC companies from Railway: {e}")
            logger.info("Falling back to JSON cache...")
            self._load_yc_companies_from_json()

    def _load_yc_companies_from_json(self):
        """Fallback: Load YC companies from JSON cache"""
        yc_cache = Path("/Users/yourox/AI-Workspace/data/yc_companies/all_companies.json")

        if not yc_cache.exists():
            logger.warning("YC companies cache not found. Run: python3 scripts/yc_companies_extractor.py")
            return

        try:
            with open(yc_cache, 'r') as f:
                companies = json.load(f)

            for company in companies:
                company['source'] = 'json_cache'
                company['source_file'] = str(yc_cache)
                self.all_data['yc_companies'].append(company)

            logger.info(f"Loaded {len(companies)} YC companies from JSON fallback")
        except Exception as e:
            logger.error(f"Error loading YC companies from JSON: {e}")

    def load_enriched_data(self):
        """Load enriched insights with computed metrics"""
        if not ENRICHED_DIR.exists():
            logger.warning(f"Enriched directory not found: {ENRICHED_DIR}")
            return

        count = 0
        for file_path in ENRICHED_DIR.glob("*_enriched.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['source_file'] = str(file_path)
                    self.all_data['enriched_insights'].append(data)
                    count += 1
            except Exception as e:
                logger.error(f"Error loading enriched {file_path}: {e}")

        logger.info(f"Loaded {count} enriched insight files")

    def load_video_summaries(self):
        """Load video-level summaries"""
        if not SUMMARIES_DIR.exists():
            logger.warning(f"Summaries directory not found: {SUMMARIES_DIR}")
            return

        count = 0
        for file_path in SUMMARIES_DIR.glob("*_summary.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['source_file'] = str(file_path)
                    self.all_data['video_summaries'].append(data)
                    count += 1
            except Exception as e:
                logger.error(f"Error loading summary {file_path}: {e}")

        logger.info(f"Loaded {count} video summaries")

    def load_meta_intelligence(self):
        """Load cross-video meta-intelligence report"""
        meta_file = META_DIR / "meta_intelligence_report.json"

        if not meta_file.exists():
            logger.warning(f"Meta-intelligence report not found: {meta_file}")
            return

        try:
            with open(meta_file, 'r') as f:
                self.meta_intelligence = json.load(f)
            logger.info("Loaded meta-intelligence report")
        except Exception as e:
            logger.error(f"Error loading meta-intelligence: {e}")

    def search(self, query: str, category: str, filters: dict = None) -> List[dict]:
        """
        Search across all data with optional filters

        Args:
            query: Search term (case-insensitive, partial match)
            category: Data category to search (products, problems, etc.)
            filters: Additional filters (e.g., {'sentiment': 'positive'})
        """
        if category not in self.all_data:
            return []

        items = self.all_data[category]
        results = []

        query_lower = query.lower() if query else ""

        for item in items:
            # Text search across all string fields
            if query_lower:
                item_text = json.dumps(item).lower()
                if query_lower not in item_text:
                    continue

            # Apply filters
            if filters:
                match = True
                for key, value in filters.items():
                    if key in item and item[key] != value:
                        match = False
                        break
                if not match:
                    continue

            results.append(item)

        return results

    def get_stats(self) -> dict:
        """Get database statistics"""
        return {
            'total_files': len(self.insights_files),
            'total_products': len(self.all_data['products']),
            'total_problems': len(self.all_data['problems']),
            'total_startup_ideas': len(self.all_data['startup_ideas']),
            'total_growth_tactics': len(self.all_data['growth_tactics']),
            'total_ai_workflows': len(self.all_data['ai_workflows']),
            'total_target_markets': len(self.all_data['target_markets']),
            'total_trends': len(self.all_data['trends']),
            'total_strategies': len(self.all_data['strategies']),
            'total_metrics': len(self.all_data['metrics']),
            'total_quotes': len(self.all_data['quotes']),
            'total_statistics': len(self.all_data['statistics']),
            'total_mistakes': len(self.all_data['mistakes']),
            'total_comment_insights': len(self.all_data['comment_insights']),
            'total_validated_comments': len(self.all_data['top_validated_comments']),
            'total_comment_trends': len(self.all_data['comment_derived_trends']),
            'total_yc_companies': len(self.all_data['yc_companies']),
            'total_enriched_insights': len(self.all_data['enriched_insights']),
            'total_video_summaries': len(self.all_data['video_summaries']),
            'meta_intelligence_loaded': len(self.meta_intelligence) > 0,
            'files_loaded': self.insights_files
        }


# Initialize database
logger.info("Loading Business Intelligence Database...")
db = BusinessIntelligenceDB()
logger.info(f"Loaded {len(db.insights_files)} files with {sum(len(v) for v in db.all_data.values())} total insights")


# Resources
@mcp.resource("bi://stats")
def get_bi_stats() -> str:
    """Get Business Intelligence database statistics"""
    stats = db.get_stats()

    # Check Railway DB status
    railway_status = "✅ Connected" if DATABASE_URL else "❌ Not Configured"

    return f"""📊 Business Intelligence Stats
{'=' * 40}
📁 JSON Insights Files: {stats['total_files']}
Products & Tools: {stats['total_products']}
Problems & Solutions: {stats['total_problems']}
Startup Ideas: {stats['total_startup_ideas']}
Growth Tactics: {stats['total_growth_tactics']}
AI Workflows: {stats['total_ai_workflows']}
Target Markets: {stats['total_target_markets']}
Trends & Signals: {stats['total_trends']}
Business Strategies: {stats['total_strategies']}
Metrics & KPIs: {stats['total_metrics']}
Actionable Quotes: {stats['total_quotes']}
Key Statistics: {stats['total_statistics']}
Mistakes to Avoid: {stats['total_mistakes']}

💬 Comment Intelligence:
Comment Insights: {stats['total_comment_insights']}
Validated Comments: {stats['total_validated_comments']}
Comment-Derived Trends: {stats['total_comment_trends']}

🚀 Y Combinator Companies (Railway PostgreSQL):
YC Companies: {stats['total_yc_companies']}

🧠 Enriched Intelligence:
Enriched Insights: {stats['total_enriched_insights']}
Video Summaries: {stats['total_video_summaries']}
Meta-Intelligence: {'✅ Loaded' if stats['meta_intelligence_loaded'] else '❌ Not Found'}

🔌 Data Sources:
Railway PostgreSQL: {railway_status}
Local JSON: {DATA_DIR}
Mode: READ-ONLY"""


@mcp.resource("bi://guide")
def get_query_guide() -> str:
    """
    Complete query guide and best practices for using the BI Vault effectively.
    Read this first to understand how to query the vault optimally.
    """
    return """🎯 BI-VAULT QUERY GUIDE
{'=' * 60}

📋 QUICK REFERENCE - WHAT TO USE WHEN

┌─────────────────────────┬──────────────────────────────────┐
│ YOUR GOAL               │ RECOMMENDED TOOL(S)              │
├─────────────────────────┼──────────────────────────────────┤
│ Find startup ideas      │ search_startup_ideas             │
│                         │ → get_opportunity_matrix         │
├─────────────────────────┼──────────────────────────────────┤
│ Research markets/trends │ search_trends                    │
│                         │ → get_meta_trends                │
│                         │ → search_target_markets          │
├─────────────────────────┼──────────────────────────────────┤
│ Find tools/products     │ search_products                  │
│                         │ → get_product_ecosystem          │
├─────────────────────────┼──────────────────────────────────┤
│ Solve specific problems │ search_problems                  │
│                         │ → get_user_problems_from_comments│
├─────────────────────────┼──────────────────────────────────┤
│ Growth/marketing        │ search_growth_tactics            │
│                         │ → get_strategy_playbooks         │
├─────────────────────────┼──────────────────────────────────┤
│ YC company research     │ search_yc_companies              │
├─────────────────────────┼──────────────────────────────────┤
│ AI automation ideas     │ search_ai_workflows              │
├─────────────────────────┼──────────────────────────────────┤
│ Expert opinions         │ get_expert_consensus             │
│                         │ → search_validated_comments      │
├─────────────────────────┼──────────────────────────────────┤
│ Read video content      │ search_video_transcripts         │
│                         │ → get_video_transcript           │
├─────────────────────────┼──────────────────────────────────┤
│ High-value insights     │ get_high_value_insights          │
│                         │ → search_enriched_insights       │
└─────────────────────────┴──────────────────────────────────┘

🔍 QUERY PATTERNS

1️⃣ EXPLORATORY RESEARCH (No specific query)
   ✅ search_trends(query="", stage="growing", limit=20)
   ✅ search_startup_ideas(query="", limit=30)
   ✅ get_meta_trends(min_frequency=3)
   ✅ get_strategy_playbooks()

2️⃣ KEYWORD SEARCH (Specific topic)
   ✅ search_products(query="chatgpt", sentiment="positive")
   ✅ search_problems(query="customer acquisition")
   ✅ search_video_transcripts(query="email marketing")

3️⃣ FILTERED DISCOVERY (Narrow down)
   ✅ search_trends(query="ai", category="technology", stage="early")
   ✅ search_yc_companies(batch="W24", is_hiring=True)
   ✅ search_growth_tactics(query="", channel="content")

4️⃣ HIGH-QUALITY FILTERING (Best insights only)
   ✅ get_high_value_insights(min_score=85, metric_type="actionability")
   ✅ search_validated_comments(min_likes=10000)
   ✅ search_enriched_insights(min_actionability=80)

5️⃣ CROSS-VIDEO ANALYSIS (Meta-intelligence)
   ✅ get_meta_trends() - Find patterns across all videos
   ✅ get_product_ecosystem() - See most recommended tools
   ✅ get_strategy_playbooks() - Recurring successful strategies
   ✅ get_expert_consensus(topic="ai_tools")

📊 DATA LAYERS (Progressive depth)

   Layer 1: RAW INSIGHTS
   ↓ search_products, search_problems, search_trends, etc.
   │ → Individual insights from each video

   Layer 2: ENRICHED DATA
   ↓ search_enriched_insights, get_high_value_insights
   │ → Same insights + quality scores (actionability, specificity, evidence)

   Layer 3: META-INTELLIGENCE
   ↓ get_meta_trends, get_product_ecosystem, get_strategy_playbooks
   │ → Cross-video patterns, consensus, recurring themes

   Layer 4: COMMENT INTELLIGENCE
   ↓ search_comment_insights, get_user_problems_from_comments
   │ → Audience validation, real user problems, high-engagement signals

⚡ PERFORMANCE TIPS

• Start broad, then narrow: search_trends(query="") → filter results client-side
• Use limits: Default 20 is good, increase only if needed
• Combine tools: Start with meta-intelligence, then drill into specifics
• Check stats first: get_database_stats() to understand coverage

🎪 COMMON WORKFLOWS

A) Market Opportunity Research:
   1. get_meta_trends(min_frequency=2, stage="growing")
   2. search_target_markets(query="<trending_category>")
   3. search_problems(query="<market_term>")
   4. get_opportunity_matrix(opportunity_type="market_gaps")

B) Product/Tool Discovery:
   1. get_product_ecosystem(min_mentions=2, sentiment="highly_positive")
   2. search_products(query="<category>", sentiment="recommended")
   3. search_validated_comments(query="<product_name>", min_likes=5000)

C) Startup Idea Validation:
   1. search_startup_ideas(query="<your_idea>")
   2. search_trends(query="<related_trend>", stage="growing")
   3. get_user_problems_from_comments(min_engagement=1000)
   4. search_yc_companies(query="<similar_company>")

D) Growth Strategy Research:
   1. get_strategy_playbooks()
   2. search_growth_tactics(query="<your_channel>")
   3. get_expert_consensus(topic="<relevant_topic>")

💡 PRO TIPS

1. Empty queries work! Many tools accept query="" to get all results with filters
2. Meta-intelligence is gold - use it to find validated patterns, not one-off mentions
3. Comment data = user validation - high likes = strong signal
4. Enrichment scores = quality filter - min_actionability=80 for actionable-only insights
5. YC companies DB has 5,487 companies with enrichments - great for competitive research
6. Video transcripts (454 total) - full text search across hours of content

📖 EXAMPLE QUERIES

❓ "What are the hottest AI trends right now?"
→ get_meta_trends(category="technology", stage="growing", min_frequency=2)

❓ "Show me validated SaaS startup ideas"
→ search_startup_ideas(query="saas", limit=20)
→ search_yc_companies(industry="B2B", status="Active", top_company=True)

❓ "What problems do fitness enthusiasts have?"
→ search_target_markets(query="fitness")
→ get_user_problems_from_comments(min_engagement=1000)

❓ "Best tools for content marketing?"
→ get_product_ecosystem(category="saas", sentiment="highly_positive")
→ search_products(query="content marketing", sentiment="recommended")

❓ "What do experts say about paid ads?"
→ get_expert_consensus(topic="paid_ads")

📚 RESOURCES TO CHECK

• bi://stats - Database statistics and coverage
• bi://guide - This guide
• bi://schema - Data structure reference (see below)
• bi://tools-index - Complete tool listing with examples

⚙️ NEED HELP?

Check get_database_stats() to see what data is available.
Most tools return JSON - parse and analyze client-side for complex queries.
"""


@mcp.resource("bi://schema")
def get_schema_reference() -> str:
    """
    Data structure reference for all insight types in the BI Vault.
    Use this to understand what fields are available for filtering.
    """
    return """📐 BI-VAULT DATA SCHEMA
{'=' * 60}

🛠️ PRODUCTS & TOOLS

{
  "name": "string",
  "category": "ai-tool | saas | platform | mobile-app | physical-product",
  "description": "string",
  "sentiment": "positive | negative | neutral | recommended",
  "use_case": "string",
  "pricing": "string (optional)",
  "url": "string (optional)",
  "video_id": "string",
  "video_title": "string"
}

🔧 PROBLEMS & SOLUTIONS

{
  "problem": "string",
  "solution": "string",
  "category": "market-research | branding | operations | marketing | sales | product",
  "difficulty": "beginner | intermediate | advanced",
  "steps": ["string"],
  "expected_outcome": "string (optional)",
  "video_id": "string",
  "video_title": "string"
}

💡 STARTUP IDEAS

{
  "idea": "string",
  "description": "string",
  "target_market": "string",
  "business_model": "SaaS | Marketplace | Agency | E-commerce | Content",
  "validation": "string (optional)",
  "revenue_potential": "string (optional)",
  "implementation_complexity": "low | medium | high (optional)",
  "video_id": "string",
  "video_title": "string"
}

📈 GROWTH TACTICS

{
  "tactic": "string",
  "channel": "content | paid-ads | seo | email | viral | partnerships | community",
  "description": "string",
  "implementation_steps": ["string"],
  "expected_results": "string (optional)",
  "timeframe": "string (optional)",
  "cost": "low | medium | high (optional)",
  "video_id": "string",
  "video_title": "string"
}

🤖 AI WORKFLOWS

{
  "workflow_name": "string",
  "automation_level": "fully-automated | semi-automated | manual",
  "description": "string",
  "tools_used": ["string"],
  "steps": ["string"],
  "use_case": "string",
  "expected_output": "string (optional)",
  "video_id": "string",
  "video_title": "string"
}

🎯 TARGET MARKETS

{
  "market": "string",
  "demographics": "string",
  "pain_points": ["string"],
  "market_size": "string (optional)",
  "growth_rate": "string (optional)",
  "opportunities": ["string"],
  "video_id": "string",
  "video_title": "string"
}

📊 TRENDS & SIGNALS

{
  "trend": "string",
  "category": "technology | consumer-behavior | market | business",
  "stage": "emerging | early | growing | mainstream | declining",
  "description": "string",
  "opportunity": "string",
  "evidence": "string (optional)",
  "timeframe": "string (optional)",
  "video_id": "string",
  "video_title": "string"
}

💬 COMMENT INSIGHTS

{
  "insight": "string",
  "type": "problem | use_case | validation | feedback | trend",
  "engagement": "integer (likes)",
  "comment_text": "string",
  "business_implication": "string (optional)",
  "video_id": "string",
  "video_title": "string"
}

🚀 YC COMPANIES

{
  "slug": "string",
  "name": "string",
  "yc_id": "string",
  "batch": "W21 | S20 | etc.",
  "website": "string",
  "industry": "string",
  "status": "Active | Acquired | Public",
  "isHiring": "boolean",
  "top_company": "boolean",
  "web_data": {
    "description": "string",
    "technologies": ["string"],
    "team_size": "integer"
  },
  "ai_insights": {
    "business_model": "string",
    "market": "string",
    "traction": "string"
  },
  "source": "railway_postgresql | json_cache"
}

🧠 ENRICHED INSIGHTS

{
  "video_id": "string",
  "video_title": "string",
  "video_type": "entrepreneurship | tutorial | interview | case_study",
  "video_level_metrics": {
    "avg_actionability_score": "integer (0-100)",
    "avg_specificity_score": "integer (0-100)",
    "avg_evidence_strength": "integer (0-100)",
    "total_insights": "integer",
    "high_value_count": "integer"
  },
  "insight_metrics": {
    "products": [{"..insight..": "string", "actionability_score": 85}],
    "problems": [{"..insight..": "string", "specificity_score": 90}],
    ...
  }
}

📹 VIDEO TRANSCRIPTS (Railway PostgreSQL - 454 videos)

{
  "video_id": "string",
  "title": "string",
  "channel_name": "string",
  "transcript": "string (full text)",
  "transcript_length": "integer",
  "published_at": "ISO timestamp",
  "metadata": "jsonb"
}

🎪 META-INTELLIGENCE (Cross-video aggregates)

See: get_meta_trends(), get_product_ecosystem(),
     get_strategy_playbooks(), get_expert_consensus(),
     get_opportunity_matrix()

These aggregate data across ALL videos to find patterns,
consensus, and validated strategies.
"""


@mcp.resource("bi://examples")
def get_query_examples() -> str:
    """
    Real-world query examples for common business intelligence tasks.
    Copy and adapt these for your specific needs.
    """
    return """📖 BI-VAULT QUERY EXAMPLES
{'=' * 60}

🚀 STARTUP IDEA RESEARCH

Q: "Find SaaS startup ideas in growing markets"
→ search_trends(query="", stage="growing", category="technology", limit=20)
→ search_startup_ideas(query="saas", business_model="SaaS", limit=20)
→ get_opportunity_matrix(opportunity_type="startup_ideas", limit=15)

Q: "What problems do people need solved?"
→ get_user_problems_from_comments(min_engagement=1000, limit=30)
→ search_problems(query="", category="all", limit=20)

───────────────────────────────────────────────────────────

📊 MARKET RESEARCH

Q: "What are emerging AI trends?"
→ get_meta_trends(category="technology", stage="early", min_frequency=2, limit=20)
→ search_trends(query="ai", stage="growing", limit=20)

Q: "Research the fitness market"
→ search_target_markets(query="fitness", limit=10)
→ search_trends(query="fitness", limit=15)
→ get_user_problems_from_comments(min_engagement=500, limit=20)
   Then filter for fitness-related

───────────────────────────────────────────────────────────

🛠️ PRODUCT & TOOL DISCOVERY

Q: "Best AI tools recommended by experts"
→ get_product_ecosystem(category="ai-tool", sentiment="highly_positive", min_mentions=2)
→ search_products(query="ai", sentiment="recommended", limit=20)
→ search_validated_comments(query="ai tool", min_likes=5000)

Q: "What tools do successful founders use?"
→ search_products(query="", category="all", sentiment="positive", limit=50)
→ get_product_ecosystem(min_mentions=3, limit=30)

───────────────────────────────────────────────────────────

📈 GROWTH & MARKETING STRATEGIES

Q: "How to grow through content marketing?"
→ get_strategy_playbooks(limit=20) # Look for content strategies
→ search_growth_tactics(query="content", channel="content", limit=20)
→ get_expert_consensus(topic="content_marketing")

Q: "Proven viral marketing tactics"
→ search_growth_tactics(query="viral", channel="viral", limit=15)
→ search_growth_tactics(query="viral", channel="content", limit=15)

───────────────────────────────────────────────────────────

🏢 Y COMBINATOR RESEARCH

Q: "Find YC companies like mine"
→ search_yc_companies(query="saas analytics", industry="B2B", limit=20)
→ search_yc_companies(batch="W24", status="Active", limit=30)

Q: "YC companies that are hiring"
→ search_yc_companies(query="", is_hiring=True, top_company=True, limit=20)

───────────────────────────────────────────────────────────

🤖 AI AUTOMATION RESEARCH

Q: "Find AI workflows I can implement"
→ search_ai_workflows(query="", automation_level="semi-automated", limit=20)
→ search_ai_workflows(query="content", limit=15)

Q: "Fully automated AI systems"
→ search_ai_workflows(query="", automation_level="fully-automated", limit=20)

───────────────────────────────────────────────────────────

💬 USER VALIDATION & INSIGHTS

Q: "What do real users say about this?"
→ search_validated_comments(query="<your_topic>", min_likes=5000, limit=20)
→ search_comment_insights(query="<topic>", insight_type="validation", limit=20)

Q: "High-engagement problems people face"
→ get_user_problems_from_comments(min_engagement=2000, limit=30)
→ search_comment_insights(query="", insight_type="problem", min_engagement=1000)

───────────────────────────────────────────────────────────

🎯 HIGH-QUALITY INSIGHTS ONLY

Q: "Most actionable business insights"
→ get_high_value_insights(min_score=85, metric_type="actionability", limit=30)

Q: "Well-evidenced insights only"
→ search_enriched_insights(min_evidence=80, min_specificity=75, limit=25)

Q: "Best insights for beginners"
→ search_video_summaries(query="", experience_level="beginner", limit=15)

───────────────────────────────────────────────────────────

🔍 DEEP RESEARCH WORKFLOWS

A) COMPREHENSIVE MARKET OPPORTUNITY ANALYSIS:
   1. get_meta_trends(stage="growing", min_frequency=2, limit=20)
   2. For each trend → search_target_markets(query="<trend>", limit=10)
   3. For each market → search_problems(query="<market>", limit=15)
   4. get_opportunity_matrix(opportunity_type="market_gaps", limit=20)
   5. search_yc_companies(query="<opportunity>", status="Active")

B) VALIDATE A STARTUP IDEA:
   1. search_startup_ideas(query="<your_idea_keywords>", limit=20)
   2. search_trends(query="<related_keywords>", stage="growing", limit=15)
   3. search_yc_companies(query="<similar_companies>", limit=15)
   4. get_user_problems_from_comments(min_engagement=1000, limit=30)
      → Filter for relevant problems
   5. search_validated_comments(query="<your_space>", min_likes=3000)
   6. get_expert_consensus(topic="<relevant_topic>")

C) COMPETITIVE INTELLIGENCE:
   1. search_yc_companies(query="<competitor_space>", limit=30)
   2. search_products(query="<category>", sentiment="positive", limit=25)
   3. get_product_ecosystem(category="<type>", min_mentions=2)
   4. search_video_transcripts(query="<competitor_name>", limit=10)

D) BUILD A GROWTH STRATEGY:
   1. get_strategy_playbooks(limit=20)
   2. search_growth_tactics(query="", channel="<your_channel>", limit=20)
   3. get_expert_consensus(topic="<growth_topic>")
   4. search_case_studies via:
      → search_video_summaries(query="case study", video_type="case_study")
   5. get_high_value_insights(min_score=80, metric_type="actionability")

───────────────────────────────────────────────────────────

💡 ADVANCED TECHNIQUES

1. EMPTY QUERY EXPLORATION:
   Most tools accept query="" to browse ALL data with filters
   Example: search_products(query="", category="ai-tool", sentiment="recommended")

2. PROGRESSIVE FILTERING:
   Start broad → Narrow down client-side → Drill deeper
   Example:
   → get_meta_trends() returns 30 trends
   → Pick interesting ones client-side
   → search_target_markets(query="picked_trend")

3. CROSS-REFERENCING:
   Validate signals across multiple sources
   Example:
   → get_meta_trends() shows "AI automation" trending
   → search_comment_insights(query="automation", insight_type="validation")
   → search_yc_companies(query="automation", batch="W24")
   → get_expert_consensus(topic="ai_tools")

4. QUALITY LAYERING:
   Start with enriched/meta → Drill into raw insights
   Example:
   → get_high_value_insights(min_score=85, metric_type="all")
   → Find video_id from results
   → get_video_transcript(video_id="...") for full context

5. ENGAGEMENT SIGNALS:
   Use comment engagement as validation metric
   Example:
   → search_validated_comments(min_likes=10000) = VERY strong signal
   → get_user_problems_from_comments(min_engagement=2000) = strong signal
   → search_comment_insights(min_engagement=500) = moderate signal
"""


@mcp.resource("bi://tools-index")
def get_tools_index() -> str:
    """
    Complete index of all 23 tools with use cases and examples.
    """
    return """🔧 BI-VAULT TOOLS INDEX
{'=' * 60}

📦 BASIC SEARCH TOOLS (Query specific categories)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. search_products(query, category, sentiment, limit)
   → Find tools, SaaS products, AI tools
   Example: search_products("ai writing", category="ai-tool", sentiment="positive")

2. search_problems(query, category, difficulty, limit)
   → Find validated problems with solutions
   Example: search_problems("customer retention", difficulty="intermediate")

3. search_startup_ideas(query, target_market, business_model, limit)
   → Discover validated startup concepts
   Example: search_startup_ideas("", business_model="SaaS", limit=30)

4. search_growth_tactics(query, channel, limit)
   → Find proven marketing strategies
   Example: search_growth_tactics("", channel="content")

5. search_ai_workflows(query, automation_level, limit)
   → Get AI automation workflows
   Example: search_ai_workflows("content creation", automation_level="semi-automated")

6. search_target_markets(query, limit)
   → Market intelligence and demographics
   Example: search_target_markets("fitness enthusiasts")

7. search_trends(query, category, stage, limit)
   → Market trends and opportunities
   Example: search_trends("ai", stage="growing", category="technology")

💬 COMMENT INTELLIGENCE TOOLS (User validation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8. search_comment_insights(query, insight_type, min_engagement, limit)
   → Insights from YouTube comments
   Example: search_comment_insights("pricing", insight_type="problem", min_engagement=500)

9. search_validated_comments(query, min_likes, limit)
   → High-engagement comments (strong signals)
   Example: search_validated_comments("", min_likes=5000)

10. search_comment_trends(query, limit)
    → Trends identified across comments
    Example: search_comment_trends("automation")

11. get_user_problems_from_comments(min_engagement, limit)
    → Problem-type insights from comments
    Example: get_user_problems_from_comments(min_engagement=1000)

🚀 YC COMPANIES TOOLS (Railway PostgreSQL - 5,487 companies)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

12. search_yc_companies(query, batch, industry, status, is_hiring, top_company, limit)
    → Search YC company database
    Example: search_yc_companies("", batch="W24", is_hiring=True, top_company=True)

🧠 ENRICHED INTELLIGENCE TOOLS (Quality-scored insights)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

13. search_enriched_insights(video_type, min_actionability, min_specificity, min_evidence, limit)
    → Filter by quality scores
    Example: search_enriched_insights(min_actionability=80, min_specificity=75)

14. get_high_value_insights(min_score, metric_type, limit)
    → Top insights by quality metric
    Example: get_high_value_insights(min_score=85, metric_type="actionability")

15. search_video_summaries(query, video_type, experience_level, limit)
    → Video-level summaries
    Example: search_video_summaries("marketing", video_type="tutorial")

📹 VIDEO TRANSCRIPT TOOLS (Railway PostgreSQL - 454 videos)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

16. search_video_transcripts(query, channel_name, min_length, limit)
    → Full-text search across all transcripts
    Example: search_video_transcripts("email marketing", min_length=5000)

17. get_video_transcript(video_id)
    → Get complete transcript for one video
    Example: get_video_transcript("dQw4w9WgXcQ")

🎪 META-INTELLIGENCE TOOLS (Cross-video analysis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

18. get_meta_trends(min_frequency, category, stage, limit)
    → Trends mentioned across multiple videos
    Example: get_meta_trends(min_frequency=3, stage="growing")

19. get_product_ecosystem(min_mentions, category, sentiment, limit)
    → Most recommended products across all videos
    Example: get_product_ecosystem(min_mentions=2, sentiment="highly_positive")

20. get_strategy_playbooks(limit)
    → Recurring strategy patterns across videos
    Example: get_strategy_playbooks()

21. get_expert_consensus(topic)
    → Expert agreement on key topics
    Example: get_expert_consensus(topic="ai_tools")
    Topics: ai_tools, paid_ads, content_marketing, saas_business, community_building

22. get_opportunity_matrix(opportunity_type, limit)
    → Comprehensive opportunities across all data
    Example: get_opportunity_matrix(opportunity_type="market_gaps")
    Types: startup_ideas, market_gaps, trend_opportunities, all

📊 UTILITY TOOLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

23. get_database_stats()
    → Database statistics and coverage
    Example: get_database_stats()

💡 CHOOSING THE RIGHT TOOL

Start with:        Then drill down with:
─────────────     ──────────────────────
Meta-tools    →   Specific searches
(get_meta_*)      (search_*)

High-level    →   Detailed data
(playbooks,       (individual insights,
 consensus)        transcripts)

Cross-video   →   Single-video
(meta-intel)      (video summaries,
                   transcripts)

Quality filter →  All data
(enriched,        (basic search)
 high-value)
"""


# Tools
@mcp.tool()
def search_products(query: str, category: str = "all", sentiment: str = "all", limit: int = 20) -> str:
    """
    Search products and tools from business intelligence database

    Args:
        query: Search term (e.g., 'chatgpt', 'saas', 'marketing tool')
        category: Product category filter (ai-tool, saas, platform, service, all)
        sentiment: Sentiment filter (positive, negative, neutral, recommended, all)
        limit: Maximum results to return (default: 20)
    """
    filters = {}
    if category != "all":
        filters["category"] = category
    if sentiment != "all":
        filters["sentiment"] = sentiment

    results = db.search(query, "products", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_problems(query: str, category: str = "all", difficulty: str = "all", limit: int = 20) -> str:
    """
    Search problems and their solutions from business intelligence

    Args:
        query: Problem search term
        category: Problem category (market-research, branding, operations, marketing, sales, product, all)
        difficulty: Difficulty filter (beginner, intermediate, advanced, all)
        limit: Maximum results (default: 20)
    """
    filters = {}
    if category != "all":
        filters["category"] = category
    if difficulty != "all":
        filters["difficulty"] = difficulty

    results = db.search(query, "problems", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_startup_ideas(query: str, target_market: str = None, business_model: str = None, limit: int = 20) -> str:
    """
    Search validated startup ideas from business intelligence

    Args:
        query: Startup idea search term
        target_market: Target market filter (optional)
        business_model: Business model filter (e.g., 'saas', 'marketplace', 'agency')
        limit: Maximum results (default: 20)
    """
    filters = {}
    if target_market:
        filters["target_market"] = target_market
    if business_model:
        filters["business_model"] = business_model

    results = db.search(query, "startup_ideas", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_growth_tactics(query: str, channel: str = "all", limit: int = 20) -> str:
    """
    Search proven growth tactics and marketing strategies

    Args:
        query: Growth tactic search term
        channel: Marketing channel (content, paid-ads, seo, email, viral, partnerships, all)
        limit: Maximum results (default: 20)
    """
    filters = {}
    if channel != "all":
        filters["channel"] = channel

    results = db.search(query, "growth_tactics", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_ai_workflows(query: str, automation_level: str = "all", limit: int = 20) -> str:
    """
    Search AI automation workflows and implementations

    Args:
        query: AI workflow search term
        automation_level: Automation level filter (fully-automated, semi-automated, manual, all)
        limit: Maximum results (default: 20)
    """
    filters = {}
    if automation_level != "all":
        filters["automation_level"] = automation_level

    results = db.search(query, "ai_workflows", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_target_markets(query: str, limit: int = 20) -> str:
    """
    Search target market intelligence and audience insights

    Args:
        query: Market search term
        limit: Maximum results (default: 20)
    """
    results = db.search(query, "target_markets", {})[:limit]

    return json.dumps({
        "query": query,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_trends(query: str, category: str = "all", stage: str = "all", limit: int = 20) -> str:
    """
    Search market trends and opportunity signals

    Args:
        query: Trend search term
        category: Trend category (technology, consumer-behavior, market, fitness, business, all)
        stage: Trend stage filter (emerging, early, growing, mainstream, declining, all)
        limit: Maximum results (default: 20)
    """
    filters = {}
    if category != "all":
        filters["category"] = category
    if stage != "all":
        filters["stage"] = stage

    results = db.search(query, "trends", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_comment_insights(query: str, insight_type: str = "all", min_engagement: int = 0, limit: int = 20) -> str:
    """
    Search insights derived from YouTube comments

    Args:
        query: Search term in insight text
        insight_type: Type filter (problem, use_case, validation, feedback, trend, all)
        min_engagement: Minimum likes on comment (default: 0)
        limit: Maximum results (default: 20)

    Returns:
        JSON with matching comment insights
    """
    filters = {}
    if insight_type != "all":
        filters["type"] = insight_type

    results = db.search(query, "comment_insights", filters)

    # Filter by engagement
    if min_engagement > 0:
        results = [r for r in results if r.get('engagement', 0) >= min_engagement]

    results = results[:limit]

    return json.dumps({
        "query": query,
        "filters": {"type": insight_type, "min_engagement": min_engagement},
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_validated_comments(query: str = "", min_likes: int = 10000, limit: int = 20) -> str:
    """
    Search high-engagement validated comments from viewers

    Args:
        query: Search term (optional)
        min_likes: Minimum engagement threshold (default: 10,000 likes)
        limit: Maximum results (default: 20)

    Returns:
        JSON with high-engagement comments and their business insights
    """
    results = db.search(query, "top_validated_comments", {})

    # Filter by likes
    results = [r for r in results if r.get('likes', 0) >= min_likes]
    results = sorted(results, key=lambda x: x.get('likes', 0), reverse=True)[:limit]

    return json.dumps({
        "query": query,
        "min_likes": min_likes,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_comment_trends(query: str = "", limit: int = 20) -> str:
    """
    Search trends identified from patterns across multiple comments

    Args:
        query: Search term in trend description
        limit: Maximum results (default: 20)

    Returns:
        JSON with comment-derived trends and business implications
    """
    results = db.search(query, "comment_derived_trends", {})[:limit]

    return json.dumps({
        "query": query,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def get_user_problems_from_comments(min_engagement: int = 1000, limit: int = 20) -> str:
    """
    Get user problems and pain points revealed in comments

    Args:
        min_engagement: Minimum likes to filter high-signal problems (default: 1000)
        limit: Maximum results (default: 20)

    Returns:
        JSON with problem-type comment insights sorted by engagement
    """
    filters = {"type": "problem"}
    results = db.search("", "comment_insights", filters)

    # Filter and sort by engagement
    results = [r for r in results if r.get('engagement', 0) >= min_engagement]
    results = sorted(results, key=lambda x: x.get('engagement', 0), reverse=True)[:limit]

    return json.dumps({
        "min_engagement": min_engagement,
        "count": len(results),
        "problems": results
    }, indent=2)


@mcp.tool()
def get_database_stats() -> str:
    """
    Get comprehensive business intelligence database statistics

    Returns counts for all data categories and loaded files.
    Useful for understanding data coverage and scope.
    """
    stats = db.get_stats()
    return json.dumps(stats, indent=2)


@mcp.tool()
def search_yc_companies(
    query: str,
    batch: str = None,
    industry: str = None,
    status: str = None,
    is_hiring: bool = None,
    top_company: bool = None,
    limit: int = 20
) -> str:
    """
    Search Y Combinator companies from the database

    Args:
        query: Search term (company name, description, industry, etc.)
        batch: YC batch filter (e.g., "W21", "S20", "F25")
        industry: Industry filter (e.g., "B2B", "Healthcare", "Fintech")
        status: Status filter (e.g., "Active", "Acquired", "Public")
        is_hiring: Filter for hiring companies only
        top_company: Filter for YC top companies only
        limit: Maximum results to return (default: 20)

    Returns:
        JSON with matching YC companies
    """
    filters = {}
    if batch:
        filters["batch"] = batch
    if industry:
        filters["industry"] = industry
    if status:
        filters["status"] = status
    if is_hiring is not None:
        filters["isHiring"] = is_hiring
    if top_company is not None:
        filters["top_company"] = top_company

    results = db.search(query, "yc_companies", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_enriched_insights(
    video_type: str = "all",
    min_actionability: int = 0,
    min_specificity: int = 0,
    min_evidence: int = 0,
    limit: int = 20
) -> str:
    """
    Search enriched insights with metric filters

    Args:
        video_type: Filter by video type (entrepreneurship, tutorial, interview, case_study, market_research, all)
        min_actionability: Minimum actionability score (0-100)
        min_specificity: Minimum specificity score (0-100)
        min_evidence: Minimum evidence strength (0-100)
        limit: Maximum results (default: 20)

    Returns:
        JSON with enriched insights matching filters
    """
    results = []

    for insight in db.all_data['enriched_insights']:
        # Filter by video type
        if video_type != "all" and insight.get('video_type') != video_type:
            continue

        # Filter by metrics
        video_metrics = insight.get('video_level_metrics', {})
        if video_metrics.get('avg_actionability_score', 0) < min_actionability:
            continue
        if video_metrics.get('avg_specificity_score', 0) < min_specificity:
            continue
        if video_metrics.get('avg_evidence_strength', 0) < min_evidence:
            continue

        results.append(insight)

    results = results[:limit]

    return json.dumps({
        "filters": {
            "video_type": video_type,
            "min_actionability": min_actionability,
            "min_specificity": min_specificity,
            "min_evidence": min_evidence
        },
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def get_high_value_insights(
    min_score: int = 80,
    metric_type: str = "actionability",
    limit: int = 20
) -> str:
    """
    Get top high-value insights by metric score

    Args:
        min_score: Minimum score threshold (default: 80)
        metric_type: Metric to filter by (actionability, specificity, evidence, all)
        limit: Maximum results (default: 20)

    Returns:
        JSON with high-value insights sorted by score
    """
    results = []

    for enriched in db.all_data['enriched_insights']:
        video_id = enriched.get('video_id')
        video_title = enriched.get('video_title', '')

        # Check all insight categories
        for category, insights in enriched.get('insight_metrics', {}).items():
            if not isinstance(insights, list):
                continue

            for insight in insights:
                score_field = f"{metric_type}_score" if metric_type != "all" else None

                if metric_type == "all":
                    # Average of all metrics
                    avg_score = (
                        insight.get('actionability_score', 0) +
                        insight.get('specificity_score', 0) +
                        insight.get('evidence_strength', 0)
                    ) / 3
                    if avg_score >= min_score:
                        results.append({
                            'video_id': video_id,
                            'video_title': video_title,
                            'category': category,
                            'insight': insight,
                            'average_score': round(avg_score, 1)
                        })
                elif score_field and insight.get(score_field, 0) >= min_score:
                    results.append({
                        'video_id': video_id,
                        'video_title': video_title,
                        'category': category,
                        'insight': insight,
                        'score': insight.get(score_field, 0)
                    })

    # Sort by score
    sort_key = 'average_score' if metric_type == "all" else 'score'
    results = sorted(results, key=lambda x: x.get(sort_key, 0), reverse=True)[:limit]

    return json.dumps({
        "min_score": min_score,
        "metric_type": metric_type,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_video_summaries(
    query: str = "",
    video_type: str = "all",
    experience_level: str = "all",
    limit: int = 20
) -> str:
    """
    Search video summaries by content and filters

    Args:
        query: Search term (searches in title, themes, takeaways)
        video_type: Filter by video type (entrepreneurship, tutorial, interview, etc.)
        experience_level: Filter by experience level (beginner, intermediate, advanced, all)
        limit: Maximum results (default: 20)

    Returns:
        JSON with matching video summaries
    """
    results = []
    query_lower = query.lower()

    for summary in db.all_data['video_summaries']:
        # Filter by video type
        content_profile = summary.get('content_profile', {})
        if video_type != "all" and content_profile.get('video_type') != video_type:
            continue

        # Filter by experience level
        if experience_level != "all" and content_profile.get('experience_level') != experience_level:
            continue

        # Text search
        if query:
            summary_text = json.dumps(summary).lower()
            if query_lower not in summary_text:
                continue

        results.append(summary)

    results = results[:limit]

    return json.dumps({
        "query": query,
        "filters": {
            "video_type": video_type,
            "experience_level": experience_level
        },
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def get_meta_trends(
    min_frequency: int = 2,
    category: str = "all",
    stage: str = "all",
    limit: int = 30
) -> str:
    """
    Get cross-video trend analysis from meta-intelligence

    Args:
        min_frequency: Minimum trend mentions (default: 2)
        category: Trend category filter (technology, market, consumer-behavior, all)
        stage: Trend stage filter (early, growing, mainstream, all)
        limit: Maximum results (default: 30)

    Returns:
        JSON with cross-video trends, frequency, and opportunities
    """
    if not db.meta_intelligence:
        return json.dumps({"error": "Meta-intelligence not loaded"}, indent=2)

    trends = db.meta_intelligence.get('cross_video_trends', {}).get('top_trends', [])
    results = []

    for trend in trends:
        # Filter by frequency
        if trend.get('frequency', 0) < min_frequency:
            continue

        # Filter by category
        if category != "all" and trend.get('category') != category:
            continue

        # Filter by stage
        if stage != "all" and trend.get('stage') != stage:
            continue

        results.append(trend)

    results = results[:limit]

    return json.dumps({
        "filters": {
            "min_frequency": min_frequency,
            "category": category,
            "stage": stage
        },
        "count": len(results),
        "total_unique_trends": db.meta_intelligence.get('cross_video_trends', {}).get('total_unique_trends', 0),
        "results": results
    }, indent=2)


@mcp.tool()
def get_product_ecosystem(
    min_mentions: int = 2,
    category: str = "all",
    sentiment: str = "all",
    limit: int = 30
) -> str:
    """
    Get product ecosystem analysis from meta-intelligence

    Args:
        min_mentions: Minimum product mentions (default: 2)
        category: Product category (ai-tool, saas, mobile-app, all)
        sentiment: Sentiment filter (highly_positive, neutral, all)
        limit: Maximum results (default: 30)

    Returns:
        JSON with product recommendations, sentiment, use cases, and metrics
    """
    if not db.meta_intelligence:
        return json.dumps({"error": "Meta-intelligence not loaded"}, indent=2)

    products = db.meta_intelligence.get('product_ecosystem', {}).get('most_recommended_tools', [])
    results = []

    for product in products:
        # Filter by mentions
        if product.get('mention_count', 0) < min_mentions:
            continue

        # Filter by category
        if category != "all" and product.get('primary_category') != category:
            continue

        # Filter by sentiment
        if sentiment != "all" and product.get('sentiment_score') != sentiment:
            continue

        results.append(product)

    results = results[:limit]

    return json.dumps({
        "filters": {
            "min_mentions": min_mentions,
            "category": category,
            "sentiment": sentiment
        },
        "count": len(results),
        "total_unique_products": db.meta_intelligence.get('product_ecosystem', {}).get('total_unique_products', 0),
        "results": results
    }, indent=2)


@mcp.tool()
def get_strategy_playbooks(limit: int = 20) -> str:
    """
    Get recurring strategy playbooks from meta-intelligence

    Args:
        limit: Maximum playbooks to return (default: 20)

    Returns:
        JSON with strategy playbooks, frequency, examples, and expected outcomes
    """
    if not db.meta_intelligence:
        return json.dumps({"error": "Meta-intelligence not loaded"}, indent=2)

    playbooks = db.meta_intelligence.get('strategy_playbooks', {}).get('recurring_playbooks', [])
    results = playbooks[:limit]

    return json.dumps({
        "count": len(results),
        "total_strategy_mentions": db.meta_intelligence.get('strategy_playbooks', {}).get('total_strategy_mentions', 0),
        "playbooks": results
    }, indent=2)


@mcp.tool()
def get_expert_consensus(topic: str = "all") -> str:
    """
    Get expert consensus analysis on key topics

    Args:
        topic: Topic to analyze (ai_tools, paid_ads, content_marketing, saas_business, community_building, all)

    Returns:
        JSON with consensus level, sentiment distribution, and examples
    """
    if not db.meta_intelligence:
        return json.dumps({"error": "Meta-intelligence not loaded"}, indent=2)

    consensus_data = db.meta_intelligence.get('expert_consensus', {})

    if topic == "all":
        return json.dumps({
            "topics": list(consensus_data.keys()),
            "consensus": consensus_data
        }, indent=2)

    if topic not in consensus_data:
        return json.dumps({"error": f"Topic '{topic}' not found. Available: {list(consensus_data.keys())}"}, indent=2)

    return json.dumps({
        "topic": topic,
        "data": consensus_data[topic]
    }, indent=2)


@mcp.tool()
def get_opportunity_matrix(
    opportunity_type: str = "all",
    limit: int = 20
) -> str:
    """
    Get comprehensive opportunity matrix from meta-intelligence

    Args:
        opportunity_type: Type filter (startup_ideas, market_gaps, trend_opportunities, all)
        limit: Maximum results (default: 20)

    Returns:
        JSON with categorized opportunities from across all videos
    """
    if not db.meta_intelligence:
        return json.dumps({"error": "Meta-intelligence not loaded"}, indent=2)

    matrix = db.meta_intelligence.get('opportunity_matrix', {})

    if opportunity_type == "all":
        return json.dumps({
            "total_opportunities": matrix.get('total_opportunities', 0),
            "by_type": matrix.get('by_type', {}),
            "top_startup_ideas": matrix.get('top_startup_ideas', [])[:limit],
            "top_market_gaps": matrix.get('top_market_gaps', [])[:limit],
            "top_trend_opportunities": matrix.get('top_trend_opportunities', [])[:limit]
        }, indent=2)

    results = matrix.get(f"top_{opportunity_type}", [])[:limit]

    return json.dumps({
        "opportunity_type": opportunity_type,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_video_transcripts(
    query: str,
    channel_name: str = None,
    min_length: int = 1000,
    limit: int = 20
) -> str:
    """
    Search across 454 video transcripts in Railway PostgreSQL

    Args:
        query: Search term to find in transcripts
        channel_name: Filter by channel name (optional)
        min_length: Minimum transcript length in characters (default: 1000)
        limit: Maximum results (default: 20)

    Returns:
        JSON with matching videos and transcript excerpts
    """
    try:
        conn = get_db_connection()
        if not conn:
            return json.dumps({"error": "Railway PostgreSQL not available"}, indent=2)

        cursor = conn.cursor()

        # Build query
        sql = """
            SELECT
                video_id,
                title,
                channel_name,
                transcript,
                LENGTH(transcript) as transcript_length,
                published_at
            FROM video_transcripts
            WHERE 1=1
        """
        params = []

        # Add search filter
        if query:
            sql += " AND (title ILIKE %s OR transcript ILIKE %s)"
            search_term = f"%{query}%"
            params.extend([search_term, search_term])

        # Add channel filter
        if channel_name:
            sql += " AND channel_name ILIKE %s"
            params.append(f"%{channel_name}%")

        # Add length filter
        sql += " AND LENGTH(transcript) >= %s"
        params.append(min_length)

        # Order and limit
        sql += " ORDER BY published_at DESC LIMIT %s;"
        params.append(limit)

        cursor.execute(sql, params)
        results = cursor.fetchall()

        # Format results with excerpt
        formatted_results = []
        for row in results:
            video_dict = dict(row)

            # Extract excerpt around query term
            transcript = video_dict.get('transcript', '')
            excerpt = transcript[:500] + "..." if len(transcript) > 500 else transcript

            if query and transcript:
                query_lower = query.lower()
                transcript_lower = transcript.lower()
                pos = transcript_lower.find(query_lower)
                if pos >= 0:
                    start = max(0, pos - 200)
                    end = min(len(transcript), pos + 300)
                    excerpt = "..." + transcript[start:end] + "..."

            formatted_results.append({
                'video_id': video_dict['video_id'],
                'title': video_dict['title'],
                'channel_name': video_dict['channel_name'],
                'transcript_length': video_dict['transcript_length'],
                'published_at': video_dict['published_at'].isoformat() if video_dict.get('published_at') else None,
                'excerpt': excerpt
            })

        cursor.close()
        conn.close()

        return json.dumps({
            "query": query,
            "filters": {
                "channel_name": channel_name,
                "min_length": min_length
            },
            "count": len(formatted_results),
            "results": formatted_results
        }, indent=2)

    except Exception as e:
        logger.error(f"Error searching video transcripts: {e}")
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_video_transcript(video_id: str) -> str:
    """
    Get full transcript for a specific video from Railway PostgreSQL

    Args:
        video_id: YouTube video ID

    Returns:
        JSON with complete video metadata and full transcript
    """
    try:
        conn = get_db_connection()
        if not conn:
            return json.dumps({"error": "Railway PostgreSQL not available"}, indent=2)

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                video_id,
                title,
                channel_name,
                transcript,
                LENGTH(transcript) as transcript_length,
                published_at,
                metadata
            FROM video_transcripts
            WHERE video_id = %s;
        """, (video_id,))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if not result:
            return json.dumps({"error": f"Video '{video_id}' not found"}, indent=2)

        video_dict = dict(result)

        # Convert timestamp
        if video_dict.get('published_at'):
            video_dict['published_at'] = video_dict['published_at'].isoformat()

        return json.dumps(video_dict, indent=2)

    except Exception as e:
        logger.error(f"Error fetching video transcript: {e}")
        return json.dumps({"error": str(e)}, indent=2)


if __name__ == "__main__":
    logger.info("Starting BI-Vault MCP Server - The Intelligence Vault")
    logger.info(f"Database: {DATA_DIR} (read-only mode)")
    mcp.run(transport="stdio")
