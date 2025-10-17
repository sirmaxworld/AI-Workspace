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
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import mcp.server.stdio
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types

# Data directory
DATA_DIR = Path("/Users/yourox/AI-Workspace/data/business_insights")

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
            'mistakes': []
        }
        self.load_all_insights()

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

                    self.insights_files.append(file_path.name)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

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
            'files_loaded': self.insights_files
        }


# Initialize database
db = BusinessIntelligenceDB()

# Create MCP server
server = Server("business-intelligence")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available business intelligence query tools"""
    return [
        types.Tool(
            name="search_products",
            description="""Search products and tools from business intelligence database.

            Returns products mentioned across 49+ analyzed videos with:
            - Product name, category, use case
            - Sentiment (positive/negative/neutral)
            - Pricing information
            - Performance metrics
            - Source video metadata

            Example: Search for 'ai tools' in 'ai-tool' category with positive sentiment""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (e.g., 'chatgpt', 'saas', 'marketing tool')"
                    },
                    "category": {
                        "type": "string",
                        "description": "Product category filter",
                        "enum": ["ai-tool", "saas", "physical-product", "platform", "service", "market-research-tool", "sourcing-platform", "all"]
                    },
                    "sentiment": {
                        "type": "string",
                        "description": "Sentiment filter",
                        "enum": ["positive", "negative", "neutral", "recommended", "all"]
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results to return (default: 20)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="search_problems",
            description="""Search problems and their solutions from business intelligence.

            Returns validated problems with:
            - Problem description and category
            - Solution steps and implementation
            - Tools needed
            - Difficulty level and time estimates
            - Real-world case studies

            Example: Find 'market research' problems in 'beginner' difficulty""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Problem search term"
                    },
                    "category": {
                        "type": "string",
                        "description": "Problem category",
                        "enum": ["market-research", "branding", "operations", "marketing", "sales", "product", "all"]
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "Difficulty filter",
                        "enum": ["beginner", "intermediate", "advanced", "all"]
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default: 20)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="search_startup_ideas",
            description="""Search validated startup ideas from business intelligence.

            Returns startup concepts with:
            - Business idea and target market
            - Problem being solved
            - Business model
            - Validation evidence
            - Investment requirements

            Example: Find 'saas' ideas for 'entrepreneurs'""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Startup idea search term"
                    },
                    "target_market": {
                        "type": "string",
                        "description": "Target market filter (optional)"
                    },
                    "business_model": {
                        "type": "string",
                        "description": "Business model filter (e.g., 'saas', 'marketplace', 'agency')"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default: 20)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="search_growth_tactics",
            description="""Search proven growth tactics and marketing strategies.

            Returns tactics with:
            - Channel and tactic description
            - Implementation steps
            - Cost estimates
            - Expected results and metrics
            - Real-world examples

            Example: Find 'viral' tactics for 'content' channel""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Growth tactic search term"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Marketing channel",
                        "enum": ["content", "paid-ads", "seo", "email", "viral", "partnerships", "all"]
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default: 20)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="search_ai_workflows",
            description="""Search AI automation workflows and implementations.

            Returns workflows with:
            - Workflow name and description
            - Tools used (AI models, platforms)
            - Step-by-step implementation
            - Automation level
            - Use cases and results

            Example: Find 'youtube' workflows or 'chatgpt' automations""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "AI workflow search term"
                    },
                    "automation_level": {
                        "type": "string",
                        "description": "Automation level filter",
                        "enum": ["fully-automated", "semi-automated", "manual", "all"]
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default: 20)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="search_target_markets",
            description="""Search target market intelligence and audience insights.

            Returns market data with:
            - Market description and demographics
            - Pain points and needs
            - Market size indicators
            - Validated problems
            - Opportunity analysis

            Example: Find 'fitness' markets or 'young women' demographics""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Market search term"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default: 20)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="search_trends",
            description="""Search market trends and opportunity signals.

            Returns trends with:
            - Trend description and category
            - Stage (emerging/growing/mainstream)
            - Opportunity analysis
            - Market implications

            Example: Find 'growing' trends in 'technology' category""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Trend search term"
                    },
                    "category": {
                        "type": "string",
                        "description": "Trend category",
                        "enum": ["technology", "consumer-behavior", "market", "fitness", "business", "all"]
                    },
                    "stage": {
                        "type": "string",
                        "description": "Trend stage filter",
                        "enum": ["emerging", "early", "growing", "mainstream", "declining", "all"]
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default: 20)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="search_business_strategies",
            description="""Search proven business strategies and implementations.

            Returns strategies with:
            - Strategy type and description
            - Implementation details
            - Expected results
            - Case studies and validation

            Example: Find 'branding' or 'market-research' strategies""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Strategy search term"
                    },
                    "strategy_type": {
                        "type": "string",
                        "description": "Strategy type filter",
                        "enum": ["market-research", "branding", "operations", "marketing", "sales", "all"]
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default: 20)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_market_opportunities",
            description="""Analyze and return top market opportunities based on BI data.

            Combines:
            - Growing trends
            - Validated problems
            - Target markets with pain points
            - Low competition signals

            Returns ranked opportunities with supporting evidence.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_growth_stage": {
                        "type": "string",
                        "description": "Minimum trend stage",
                        "enum": ["emerging", "early", "growing", "mainstream"]
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum opportunities (default: 10)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_actionable_quotes",
            description="""Get actionable quotes and insights by category.

            Returns high-value quotes with:
            - Quote text and context
            - Category (strategy, branding, operations, etc.)
            - Actionability description
            - Source video

            Example: Get 'branding' quotes or 'strategy' insights""",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Quote category",
                        "enum": ["strategy", "branding", "operations", "marketing", "mindset", "all"]
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum quotes (default: 20)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_key_metrics",
            description="""Get key metrics, KPIs, and benchmarks from BI data.

            Returns metrics with:
            - Metric name and description
            - Benchmark values
            - Tracking methods
            - Optimization tips

            Example: Get metrics for revenue, conversion, or growth""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Metric search term (optional)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum metrics (default: 20)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_mistakes_to_avoid",
            description="""Get common mistakes and how to avoid them.

            Returns mistakes with:
            - Mistake description
            - Consequences
            - Prevention strategies
            - Real examples

            Helps agents learn from others' failures.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Mistake search term (optional)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum mistakes (default: 20)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_database_stats",
            description="""Get comprehensive business intelligence database statistics.

            Returns counts for all data categories and loaded files.
            Useful for understanding data coverage and scope.""",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution"""

    if arguments is None:
        arguments = {}

    try:
        if name == "search_products":
            query = arguments.get("query", "")
            category = arguments.get("category", "all")
            sentiment = arguments.get("sentiment", "all")
            limit = arguments.get("limit", 20)

            filters = {}
            if category != "all":
                filters["category"] = category
            if sentiment != "all":
                filters["sentiment"] = sentiment

            results = db.search(query, "products", filters)[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "filters": filters,
                    "count": len(results),
                    "results": results
                }, indent=2)
            )]

        elif name == "search_problems":
            query = arguments.get("query", "")
            category = arguments.get("category", "all")
            difficulty = arguments.get("difficulty", "all")
            limit = arguments.get("limit", 20)

            filters = {}
            if category != "all":
                filters["category"] = category
            if difficulty != "all":
                filters["difficulty"] = difficulty

            results = db.search(query, "problems", filters)[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "filters": filters,
                    "count": len(results),
                    "results": results
                }, indent=2)
            )]

        elif name == "search_startup_ideas":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 20)

            filters = {}
            if "target_market" in arguments:
                filters["target_market"] = arguments["target_market"]
            if "business_model" in arguments:
                filters["business_model"] = arguments["business_model"]

            results = db.search(query, "startup_ideas", filters)[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "filters": filters,
                    "count": len(results),
                    "results": results
                }, indent=2)
            )]

        elif name == "search_growth_tactics":
            query = arguments.get("query", "")
            channel = arguments.get("channel", "all")
            limit = arguments.get("limit", 20)

            filters = {}
            if channel != "all":
                filters["channel"] = channel

            results = db.search(query, "growth_tactics", filters)[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "filters": filters,
                    "count": len(results),
                    "results": results
                }, indent=2)
            )]

        elif name == "search_ai_workflows":
            query = arguments.get("query", "")
            automation_level = arguments.get("automation_level", "all")
            limit = arguments.get("limit", 20)

            filters = {}
            if automation_level != "all":
                filters["automation_level"] = automation_level

            results = db.search(query, "ai_workflows", filters)[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "filters": filters,
                    "count": len(results),
                    "results": results
                }, indent=2)
            )]

        elif name == "search_target_markets":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 20)

            results = db.search(query, "target_markets", {})[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "count": len(results),
                    "results": results
                }, indent=2)
            )]

        elif name == "search_trends":
            query = arguments.get("query", "")
            category = arguments.get("category", "all")
            stage = arguments.get("stage", "all")
            limit = arguments.get("limit", 20)

            filters = {}
            if category != "all":
                filters["category"] = category
            if stage != "all":
                filters["stage"] = stage

            results = db.search(query, "trends", filters)[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "filters": filters,
                    "count": len(results),
                    "results": results
                }, indent=2)
            )]

        elif name == "search_business_strategies":
            query = arguments.get("query", "")
            strategy_type = arguments.get("strategy_type", "all")
            limit = arguments.get("limit", 20)

            filters = {}
            if strategy_type != "all":
                filters["strategy_type"] = strategy_type

            results = db.search(query, "strategies", filters)[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "filters": filters,
                    "count": len(results),
                    "results": results
                }, indent=2)
            )]

        elif name == "get_market_opportunities":
            min_growth_stage = arguments.get("min_growth_stage", "emerging")
            limit = arguments.get("limit", 10)

            # Get growing trends
            stage_order = ["emerging", "early", "growing", "mainstream"]
            min_index = stage_order.index(min_growth_stage)
            valid_stages = stage_order[min_index:]

            growing_trends = [t for t in db.all_data["trends"] if t.get("stage") in valid_stages]

            # Get validated problems
            problems = db.all_data["problems"]

            # Get target markets
            markets = db.all_data["target_markets"]

            # Combine into opportunities
            opportunities = []
            for trend in growing_trends[:limit]:
                opportunity = {
                    "trend": trend,
                    "related_problems": [p for p in problems if any(
                        keyword in json.dumps(p).lower()
                        for keyword in trend.get("trend", "").lower().split()[:3]
                    )][:3],
                    "related_markets": [m for m in markets if any(
                        keyword in json.dumps(m).lower()
                        for keyword in trend.get("trend", "").lower().split()[:3]
                    )][:3]
                }
                opportunities.append(opportunity)

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "min_growth_stage": min_growth_stage,
                    "count": len(opportunities),
                    "opportunities": opportunities
                }, indent=2)
            )]

        elif name == "get_actionable_quotes":
            category = arguments.get("category", "all")
            limit = arguments.get("limit", 20)

            filters = {}
            if category != "all":
                filters["category"] = category

            results = db.search("", "quotes", filters)[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "category": category,
                    "count": len(results),
                    "quotes": results
                }, indent=2)
            )]

        elif name == "get_key_metrics":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 20)

            results = db.search(query, "metrics", {})[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "count": len(results),
                    "metrics": results
                }, indent=2)
            )]

        elif name == "get_mistakes_to_avoid":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 20)

            results = db.search(query, "mistakes", {})[:limit]

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "count": len(results),
                    "mistakes": results
                }, indent=2)
            )]

        elif name == "get_database_stats":
            stats = db.get_stats()

            return [types.TextContent(
                type="text",
                text=json.dumps(stats, indent=2)
            )]

        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


async def main():
    """Main entry point for MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="business-intelligence",
            server_version="1.0.0",
            capabilities=server.get_capabilities(
                notification_options=types.NotificationOptions(),
                experimental_capabilities={}
            )
        )
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
