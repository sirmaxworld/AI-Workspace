#!/usr/bin/env python3
"""
Business Intelligence MCP Server
Exposes AI-extracted business insights from 49+ YouTube videos

Provides semantic search and structured queries for:
- Products & Tools (210+)
- Problems & Solutions (82+)
- Startup Ideas (63+)
- Growth Tactics (64+)
- AI Workflows (69+)
- Target Markets (72+)
- Trends & Signals (104+)
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "Business Intelligence",
    instructions="Query-only access to YouTube/BI knowledge insights. Read-only database."
)

# Data directories
DATA_DIR = Path("/Users/yourox/AI-Workspace/data/business_insights")
ENRICHED_DIR = Path("/Users/yourox/AI-Workspace/data/enriched_insights")
SUMMARIES_DIR = Path("/Users/yourox/AI-Workspace/data/video_summaries")
META_DIR = Path("/Users/yourox/AI-Workspace/data/meta_intelligence")


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
        """Load Y Combinator companies from cache"""
        yc_cache = Path("/Users/yourox/AI-Workspace/data/yc_companies/all_companies.json")

        if not yc_cache.exists():
            logger.warning("YC companies cache not found. Run: python3 scripts/yc_companies_extractor.py")
            return

        try:
            with open(yc_cache, 'r') as f:
                companies = json.load(f)

            # Add to all_data
            for company in companies:
                # Add metadata
                company['source'] = 'yc_companies'
                company['source_file'] = str(yc_cache)
                self.all_data['yc_companies'].append(company)

            logger.info(f"Loaded {len(companies)} YC companies")
        except Exception as e:
            logger.error(f"Error loading YC companies: {e}")

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
    return f"""📊 Business Intelligence Stats
{'=' * 40}
Files Loaded: {stats['total_files']}
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

🚀 Y Combinator Companies:
YC Companies: {stats['total_yc_companies']}

🧠 Enriched Intelligence:
Enriched Insights: {stats['total_enriched_insights']}
Video Summaries: {stats['total_video_summaries']}
Meta-Intelligence: {'✅ Loaded' if stats['meta_intelligence_loaded'] else '❌ Not Found'}

Database: {DATA_DIR}
Mode: READ-ONLY"""


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


if __name__ == "__main__":
    logger.info("Starting Business Intelligence MCP Server")
    logger.info(f"Database: {DATA_DIR} (read-only mode)")
    mcp.run(transport="stdio")
