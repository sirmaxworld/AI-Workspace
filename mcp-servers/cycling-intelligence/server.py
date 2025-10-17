#!/usr/bin/env python3
"""
Cycling Intelligence MCP Server
Exposes cycling industry insights from Pinkbike articles

Provides semantic search and structured queries for:
- Mountain Bikes & Components
- Cycling Trends & Technology
- Gear Recommendations & Reviews
- Community Sentiment & Feedback
- Field Test Results
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "Cycling Intelligence",
    instructions="Query-only access to Pinkbike cycling insights. Read-only database."
)

# Data directory
DATA_DIR = Path("/Users/yourox/AI-Workspace/data/pinkbike_insights")


class CyclingIntelligenceDB:
    """In-memory cycling intelligence database with rich query capabilities"""

    def __init__(self):
        self.insights_files = []
        self.all_data = {
            'bikes': [],
            'components': [],
            'apparel': [],
            'tech_trends': [],
            'market_trends': [],
            'geometry_trends': [],
            'editor_picks': [],
            'field_tests': [],
            'value_picks': [],
            'reliability_issues': [],
            'compatibility_issues': [],
            'availability_pricing': [],
            'community_sentiment': [],
            'user_validation': [],
            'feature_requests': [],
            'brand_perception': [],
            'product_launches': [],
            'brand_news': []
        }
        self.load_all_insights()

    def load_all_insights(self):
        """Load all cycling intelligence JSON files"""
        if not DATA_DIR.exists():
            logger.warning(f"Data directory does not exist: {DATA_DIR}")
            return

        for file_path in DATA_DIR.glob("*_insights.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    article_id = data.get('meta', {}).get('article_id', file_path.stem.replace('_insights', ''))

                    # Add article metadata to each item
                    meta = {
                        'article_id': article_id,
                        'article_title': data.get('meta', {}).get('title', ''),
                        'article_url': data.get('meta', {}).get('url', ''),
                        'article_type': data.get('meta', {}).get('article_type', ''),
                        'source_file': str(file_path),
                        'data_source': 'pinkbike'
                    }

                    # Extract all cycling data
                    self._extract_bikes(data, meta)
                    self._extract_components(data, meta)
                    self._extract_apparel(data, meta)
                    self._extract_trends(data, meta)
                    self._extract_recommendations(data, meta)
                    self._extract_problems(data, meta)
                    self._extract_community(data, meta)
                    self._extract_industry_news(data, meta)

                    self.insights_files.append(file_path.name)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

    def _extract_bikes(self, data: dict, meta: dict):
        """Extract mountain bikes"""
        bikes = data.get('cycling_products', {}).get('mountain_bikes', [])
        for bike in bikes:
            self.all_data['bikes'].append({**bike, **meta})

    def _extract_components(self, data: dict, meta: dict):
        """Extract components"""
        components = data.get('cycling_products', {}).get('components', [])
        for component in components:
            self.all_data['components'].append({**component, **meta})

    def _extract_apparel(self, data: dict, meta: dict):
        """Extract apparel and gear"""
        apparel = data.get('cycling_products', {}).get('apparel_gear', [])
        for item in apparel:
            self.all_data['apparel'].append({**item, **meta})

    def _extract_trends(self, data: dict, meta: dict):
        """Extract cycling trends"""
        tech_trends = data.get('cycling_trends', {}).get('technology_trends', [])
        market_trends = data.get('cycling_trends', {}).get('market_trends', [])
        geo_trends = data.get('cycling_trends', {}).get('geometry_trends', [])

        for trend in tech_trends:
            self.all_data['tech_trends'].append({**trend, **meta})
        for trend in market_trends:
            self.all_data['market_trends'].append({**trend, **meta})
        for trend in geo_trends:
            self.all_data['geometry_trends'].append({**trend, **meta})

    def _extract_recommendations(self, data: dict, meta: dict):
        """Extract gear recommendations"""
        editor_picks = data.get('gear_recommendations', {}).get('editor_picks', [])
        field_tests = data.get('gear_recommendations', {}).get('field_test_results', [])
        value_picks = data.get('gear_recommendations', {}).get('value_picks', [])

        for pick in editor_picks:
            self.all_data['editor_picks'].append({**pick, **meta})
        for test in field_tests:
            self.all_data['field_tests'].append({**test, **meta})
        for pick in value_picks:
            self.all_data['value_picks'].append({**pick, **meta})

    def _extract_problems(self, data: dict, meta: dict):
        """Extract cycling problems and issues"""
        reliability = data.get('cycling_problems', {}).get('reliability_issues', [])
        compatibility = data.get('cycling_problems', {}).get('compatibility_issues', [])
        availability = data.get('cycling_problems', {}).get('availability_pricing', [])

        for issue in reliability:
            self.all_data['reliability_issues'].append({**issue, **meta})
        for issue in compatibility:
            self.all_data['compatibility_issues'].append({**issue, **meta})
        for issue in availability:
            self.all_data['availability_pricing'].append({**issue, **meta})

    def _extract_community(self, data: dict, meta: dict):
        """Extract community insights"""
        sentiment = data.get('community_insights', {}).get('comment_sentiment', [])
        validation = data.get('community_insights', {}).get('user_validation', [])
        features = data.get('community_insights', {}).get('feature_requests', [])
        brands = data.get('community_insights', {}).get('brand_perception', [])

        for item in sentiment:
            self.all_data['community_sentiment'].append({**item, **meta})
        for item in validation:
            self.all_data['user_validation'].append({**item, **meta})
        for item in features:
            self.all_data['feature_requests'].append({**item, **meta})
        for item in brands:
            self.all_data['brand_perception'].append({**item, **meta})

    def _extract_industry_news(self, data: dict, meta: dict):
        """Extract industry news"""
        launches = data.get('industry_news', {}).get('product_launches', [])
        news = data.get('industry_news', {}).get('brand_news', [])

        for launch in launches:
            self.all_data['product_launches'].append({**launch, **meta})
        for item in news:
            self.all_data['brand_news'].append({**item, **meta})

    def search(self, query: str, category: str, filters: dict = None) -> List[dict]:
        """Search across all data with optional filters"""
        if category not in self.all_data:
            return []

        items = self.all_data[category]
        results = []

        query_lower = query.lower() if query else ""

        for item in items:
            # Text search
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
            'total_bikes': len(self.all_data['bikes']),
            'total_components': len(self.all_data['components']),
            'total_apparel': len(self.all_data['apparel']),
            'total_tech_trends': len(self.all_data['tech_trends']),
            'total_market_trends': len(self.all_data['market_trends']),
            'total_geometry_trends': len(self.all_data['geometry_trends']),
            'total_editor_picks': len(self.all_data['editor_picks']),
            'total_field_tests': len(self.all_data['field_tests']),
            'total_value_picks': len(self.all_data['value_picks']),
            'total_reliability_issues': len(self.all_data['reliability_issues']),
            'total_compatibility_issues': len(self.all_data['compatibility_issues']),
            'total_availability_issues': len(self.all_data['availability_pricing']),
            'total_community_sentiment': len(self.all_data['community_sentiment']),
            'total_user_validations': len(self.all_data['user_validation']),
            'total_feature_requests': len(self.all_data['feature_requests']),
            'total_brand_perceptions': len(self.all_data['brand_perception']),
            'total_product_launches': len(self.all_data['product_launches']),
            'total_brand_news': len(self.all_data['brand_news']),
            'files_loaded': self.insights_files
        }


# Initialize database
logger.info("Loading Cycling Intelligence Database...")
db = CyclingIntelligenceDB()
logger.info(f"Loaded {len(db.insights_files)} files with {sum(len(v) for v in db.all_data.values())} total insights")


# Resources
@mcp.resource("cycling://stats")
def get_cycling_stats() -> str:
    """Get Cycling Intelligence database statistics"""
    stats = db.get_stats()
    return f"""🚴 Cycling Intelligence Stats (Pinkbike)
{'=' * 40}
Files Loaded: {stats['total_files']}

🚲 Products:
Mountain Bikes: {stats['total_bikes']}
Components: {stats['total_components']}
Apparel & Gear: {stats['total_apparel']}

📈 Trends:
Technology Trends: {stats['total_tech_trends']}
Market Trends: {stats['total_market_trends']}
Geometry Trends: {stats['total_geometry_trends']}

⭐ Recommendations:
Editor Picks: {stats['total_editor_picks']}
Field Test Results: {stats['total_field_tests']}
Value Picks: {stats['total_value_picks']}

⚠️  Issues:
Reliability Issues: {stats['total_reliability_issues']}
Compatibility Issues: {stats['total_compatibility_issues']}
Availability/Pricing: {stats['total_availability_issues']}

💬 Community:
Sentiment Analysis: {stats['total_community_sentiment']}
User Validations: {stats['total_user_validations']}
Feature Requests: {stats['total_feature_requests']}
Brand Perceptions: {stats['total_brand_perceptions']}

🗞️  Industry:
Product Launches: {stats['total_product_launches']}
Brand News: {stats['total_brand_news']}

Database: {DATA_DIR}
Mode: READ-ONLY"""


# Tools
@mcp.tool()
def search_mountain_bikes(query: str, category: str = "all", sentiment: str = "all", limit: int = 20) -> str:
    """
    Search mountain bikes from Pinkbike reviews and field tests

    Args:
        query: Search term (brand, model, features)
        category: Bike category (xc, trail, enduro, downhill, e-bike, all)
        sentiment: Review sentiment (positive, negative, highly-recommended, best-value, all)
        limit: Maximum results (default: 20)
    """
    filters = {}
    if category != "all":
        filters["category"] = category
    if sentiment != "all":
        filters["sentiment"] = sentiment

    results = db.search(query, "bikes", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_components(query: str, category: str = "all", sentiment: str = "all", limit: int = 20) -> str:
    """
    Search cycling components (forks, shocks, drivetrains, brakes, wheels, etc.)

    Args:
        query: Search term (brand, model, tech features)
        category: Component type (fork, shock, drivetrain, brakes, wheels, tires, all)
        sentiment: Review sentiment (positive, recommended, cautioned, all)
        limit: Maximum results (default: 20)
    """
    filters = {}
    if category != "all":
        filters["category"] = category
    if sentiment != "all":
        filters["sentiment"] = sentiment

    results = db.search(query, "components", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_cycling_trends(query: str, trend_type: str = "all", stage: str = "all", limit: int = 20) -> str:
    """
    Search cycling industry trends (technology, market, geometry)

    Args:
        query: Trend search term
        trend_type: Trend category (technology, market, geometry, all)
        stage: Adoption stage (emerging, growing, mainstream, all)
        limit: Maximum results (default: 20)
    """
    filters = {}
    if stage != "all":
        filters["adoption_stage"] = stage

    # Search across all trend types or specific
    if trend_type == "all":
        tech = db.search(query, "tech_trends", filters)
        market = db.search(query, "market_trends", filters)
        geo = db.search(query, "geometry_trends", filters)
        results = (tech + market + geo)[:limit]
    elif trend_type == "technology":
        results = db.search(query, "tech_trends", filters)[:limit]
    elif trend_type == "market":
        results = db.search(query, "market_trends", filters)[:limit]
    elif trend_type == "geometry":
        results = db.search(query, "geometry_trends", filters)[:limit]
    else:
        results = []

    return json.dumps({
        "query": query,
        "trend_type": trend_type,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_field_tests(query: str = "", year: str = "all", limit: int = 20) -> str:
    """
    Search Pinkbike field test results and rankings

    Args:
        query: Search term (bike category, brand, etc.)
        year: Test year filter (2024, 2025, all)
        limit: Maximum results (default: 20)
    """
    filters = {}
    if year != "all":
        filters["year"] = year

    results = db.search(query, "field_tests", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_gear_recommendations(query: str, rec_type: str = "all", limit: int = 20) -> str:
    """
    Search gear recommendations from editors and tests

    Args:
        query: Search term (product, category)
        rec_type: Recommendation type (editor-picks, field-tests, value-picks, all)
        limit: Maximum results (default: 20)
    """
    if rec_type == "all":
        editor = db.search(query, "editor_picks", {})
        tests = db.search(query, "field_tests", {})
        value = db.search(query, "value_picks", {})
        results = (editor + tests + value)[:limit]
    elif rec_type == "editor-picks":
        results = db.search(query, "editor_picks", {})[:limit]
    elif rec_type == "field-tests":
        results = db.search(query, "field_tests", {})[:limit]
    elif rec_type == "value-picks":
        results = db.search(query, "value_picks", {})[:limit]
    else:
        results = []

    return json.dumps({
        "query": query,
        "rec_type": rec_type,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_brand_perception(brand: str = "", limit: int = 10) -> str:
    """
    Search community perception of cycling brands

    Args:
        brand: Brand name to search (optional)
        limit: Maximum results (default: 10)
    """
    results = db.search(brand, "brand_perception", {})[:limit]

    return json.dumps({
        "brand": brand,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def search_reliability_issues(query: str = "", severity: str = "all", limit: int = 20) -> str:
    """
    Search known reliability issues with products

    Args:
        query: Search term (product, issue)
        severity: Issue severity (critical, major, minor, all)
        limit: Maximum results (default: 20)
    """
    filters = {}
    if severity != "all":
        filters["severity"] = severity

    results = db.search(query, "reliability_issues", filters)[:limit]

    return json.dumps({
        "query": query,
        "filters": filters,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def get_database_stats() -> str:
    """
    Get comprehensive cycling intelligence database statistics
    """
    stats = db.get_stats()
    return json.dumps(stats, indent=2)


if __name__ == "__main__":
    logger.info("Starting Cycling Intelligence MCP Server")
    logger.info(f"Database: {DATA_DIR} (read-only mode)")
    mcp.run(transport="stdio")
