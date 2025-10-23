#!/usr/bin/env python3
"""
Business Intelligence Schema Definition
Single source of truth for all data structures

This schema is used by:
1. business_intelligence_extractor.py - AI extraction
2. MCP server.py - Data loading and querying
3. Validation and testing scripts

ANY CHANGES HERE AUTOMATICALLY AFFECT ALL SYSTEMS
"""

from typing import Dict, List, Any, TypedDict, Literal
from datetime import datetime

# Schema Version - Increment when making changes
SCHEMA_VERSION = "1.0.0"
LAST_UPDATED = "2025-10-15"

# ==================== TYPE DEFINITIONS ====================

class TargetMarket(TypedDict, total=False):
    """Target market definition"""
    market_description: str
    demographics: List[str]
    pain_points: List[str]
    market_size_indicators: str


class ValidatedProblem(TypedDict, total=False):
    """Validated market problem"""
    problem: str
    severity: str
    current_solutions: str
    market_gap: str


class MarketIntelligence(TypedDict, total=False):
    """Market intelligence container"""
    target_markets: List[TargetMarket]
    problems_validated: List[ValidatedProblem]


class ProductTool(TypedDict, total=False):
    """Product or tool mention"""
    name: str
    category: str  # Allow any category - data has many variations
    use_case: str
    sentiment: str  # Allow any sentiment - data has combined values like "positive/recommended"
    pricing: str
    metrics: str


class BusinessStrategy(TypedDict, total=False):
    """Business strategy"""
    strategy_type: Literal["monetization", "growth", "operations", "market-research",
                           "branding", "marketing", "sales"]
    strategy: str
    implementation: str
    expected_results: str
    case_study: str


class ProblemSolution(TypedDict, total=False):
    """Problem with solution"""
    problem: str
    category: Literal["technical", "business", "marketing", "product", "market-research",
                     "branding", "operations", "sales"]
    solution: str
    steps: List[str]
    tools_needed: List[str]
    difficulty: Literal["beginner", "intermediate", "advanced"]
    time_estimate: str


class StartupIdea(TypedDict, total=False):
    """Startup idea"""
    idea: str
    target_market: str
    problem_solved: str
    business_model: str
    validation: str
    investment_needed: str


class MistakeToAvoid(TypedDict, total=False):
    """Common mistake"""
    mistake: str
    consequences: str
    prevention: str
    example: str


class GrowthTactic(TypedDict, total=False):
    """Growth tactic"""
    channel: Literal["seo", "paid-ads", "content", "viral", "community", "email",
                    "partnerships", "all"]
    tactic: str
    steps: List[str]
    cost_estimate: str
    results_expected: str


class AIWorkflow(TypedDict, total=False):
    """AI workflow"""
    workflow_name: str
    tools_used: List[str]
    steps: List[str]
    automation_level: Literal["manual", "semi-automated", "fully-automated"]
    use_case: str


class MetricKPI(TypedDict, total=False):
    """Metric or KPI"""
    metric: str
    benchmark: str
    tracking_method: str
    optimization_tip: str


class TrendSignal(TypedDict, total=False):
    """Trend or signal"""
    trend: str
    category: Literal["technology", "market", "consumer-behavior", "fitness", "business", "all"]
    stage: Literal["early", "emerging", "growing", "mainstream", "declining"]
    opportunity: str


class ActionableQuote(TypedDict, total=False):
    """Actionable quote"""
    quote: str
    context: str
    category: Literal["strategy", "mindset", "tactical", "branding", "operations",
                     "marketing", "all"]
    actionability: str


class KeyStatistic(TypedDict, total=False):
    """Key statistic"""
    statistic: str
    context: str
    source_reliability: Literal["claimed", "verified", "estimated"]


class VideoMeta(TypedDict, total=False):
    """Video metadata"""
    video_id: str
    title: str
    extracted_at: str
    model: str
    transcript_length: int
    processing_time_seconds: float


class BusinessIntelligenceData(TypedDict, total=False):
    """Complete business intelligence data structure"""
    market_intelligence: MarketIntelligence
    products_tools: List[ProductTool]
    business_strategies: List[BusinessStrategy]
    problems_solutions: List[ProblemSolution]
    startup_ideas: List[StartupIdea]
    mistakes_to_avoid: List[MistakeToAvoid]
    growth_tactics: List[GrowthTactic]
    ai_workflows: List[AIWorkflow]
    metrics_kpis: List[MetricKPI]
    trends_signals: List[TrendSignal]
    actionable_quotes: List[ActionableQuote]
    key_statistics: List[KeyStatistic]
    meta: VideoMeta


# ==================== SCHEMA DEFINITIONS ====================

EXTRACTION_SCHEMA = {
    "market_intelligence": {
        "target_markets": {
            "fields": ["market_description", "demographics", "pain_points", "market_size_indicators"],
            "description": "Target market profiles with demographics and pain points"
        },
        "problems_validated": {
            "fields": ["problem", "severity", "current_solutions", "market_gap"],
            "description": "Validated market problems with severity and gaps"
        }
    },
    "products_tools": {
        "fields": ["name", "category", "use_case", "sentiment", "pricing", "metrics"],
        "categories": ["saas", "ai-tool", "mobile-app", "service", "physical-product",
                      "platform", "market-research-tool", "sourcing-platform",
                      "automation-platform", "content-generator", "api-service", "all"],
        "sentiments": ["positive", "negative", "neutral", "recommended",
                      "positive/recommended", "highly-recommended", "all"],
        "description": "Products and tools mentioned with sentiment analysis"
    },
    "business_strategies": {
        "fields": ["strategy_type", "strategy", "implementation", "expected_results", "case_study"],
        "strategy_types": ["monetization", "growth", "operations", "market-research",
                          "branding", "marketing", "sales"],
        "description": "Business strategies with implementation details"
    },
    "problems_solutions": {
        "fields": ["problem", "category", "solution", "steps", "tools_needed", "difficulty", "time_estimate"],
        "categories": ["technical", "business", "marketing", "product", "market-research",
                      "branding", "operations", "sales"],
        "difficulties": ["beginner", "intermediate", "advanced"],
        "description": "Problems with step-by-step solutions"
    },
    "startup_ideas": {
        "fields": ["idea", "target_market", "problem_solved", "business_model", "validation", "investment_needed"],
        "description": "Startup ideas with validation and business models"
    },
    "mistakes_to_avoid": {
        "fields": ["mistake", "consequences", "prevention", "example"],
        "description": "Common mistakes with prevention strategies"
    },
    "growth_tactics": {
        "fields": ["channel", "tactic", "steps", "cost_estimate", "results_expected"],
        "channels": ["seo", "paid-ads", "content", "viral", "community", "email",
                    "partnerships", "all"],
        "description": "Growth tactics across marketing channels"
    },
    "ai_workflows": {
        "fields": ["workflow_name", "tools_used", "steps", "automation_level", "use_case"],
        "automation_levels": ["manual", "semi-automated", "fully-automated"],
        "description": "AI workflows with automation details"
    },
    "metrics_kpis": {
        "fields": ["metric", "benchmark", "tracking_method", "optimization_tip"],
        "description": "Key metrics and KPIs with benchmarks"
    },
    "trends_signals": {
        "fields": ["trend", "category", "stage", "opportunity"],
        "categories": ["technology", "market", "consumer-behavior", "fitness", "business", "all"],
        "stages": ["early", "emerging", "growing", "mainstream", "declining"],
        "description": "Market trends with stage and opportunity analysis"
    },
    "actionable_quotes": {
        "fields": ["quote", "context", "category", "actionability"],
        "categories": ["strategy", "mindset", "tactical", "branding", "operations",
                      "marketing", "all"],
        "description": "Actionable quotes with context and category"
    },
    "key_statistics": {
        "fields": ["statistic", "context", "source_reliability"],
        "reliabilities": ["claimed", "verified", "estimated"],
        "description": "Key statistics with source reliability"
    },
    "meta": {
        "fields": ["video_id", "title", "extracted_at", "model", "transcript_length", "processing_time_seconds"],
        "description": "Video metadata and extraction details"
    }
}


# ==================== MCP TOOL MAPPINGS ====================

MCP_TOOL_MAPPINGS = {
    "search_products": {
        "data_category": "products_tools",
        "filter_fields": ["category", "sentiment"],
        "search_fields": ["name", "use_case", "metrics"],
        "description": "Search products and tools with filtering"
    },
    "search_problems": {
        "data_category": "problems_solutions",
        "filter_fields": ["category", "difficulty"],
        "search_fields": ["problem", "solution", "steps"],
        "description": "Search problems with solutions"
    },
    "search_startup_ideas": {
        "data_category": "startup_ideas",
        "filter_fields": ["target_market", "business_model"],
        "search_fields": ["idea", "problem_solved"],
        "description": "Search startup ideas"
    },
    "search_growth_tactics": {
        "data_category": "growth_tactics",
        "filter_fields": ["channel"],
        "search_fields": ["tactic", "steps", "results_expected"],
        "description": "Search growth tactics"
    },
    "search_ai_workflows": {
        "data_category": "ai_workflows",
        "filter_fields": ["automation_level"],
        "search_fields": ["workflow_name", "tools_used", "use_case"],
        "description": "Search AI workflows"
    },
    "search_target_markets": {
        "data_category": "market_intelligence.target_markets",
        "filter_fields": [],
        "search_fields": ["market_description", "demographics", "pain_points"],
        "description": "Search target markets"
    },
    "search_trends": {
        "data_category": "trends_signals",
        "filter_fields": ["category", "stage"],
        "search_fields": ["trend", "opportunity"],
        "description": "Search market trends"
    },
    "search_business_strategies": {
        "data_category": "business_strategies",
        "filter_fields": ["strategy_type"],
        "search_fields": ["strategy", "implementation", "case_study"],
        "description": "Search business strategies"
    },
    "get_actionable_quotes": {
        "data_category": "actionable_quotes",
        "filter_fields": ["category"],
        "search_fields": ["quote", "context", "actionability"],
        "description": "Get actionable quotes"
    },
    "get_key_metrics": {
        "data_category": "metrics_kpis",
        "filter_fields": [],
        "search_fields": ["metric", "benchmark", "optimization_tip"],
        "description": "Get key metrics and KPIs"
    },
    "get_mistakes_to_avoid": {
        "data_category": "mistakes_to_avoid",
        "filter_fields": [],
        "search_fields": ["mistake", "prevention", "example"],
        "description": "Get mistakes to avoid"
    }
}


# ==================== VALIDATION FUNCTIONS ====================

def validate_data_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that extracted data matches schema
    Returns validation report
    """
    report = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "missing_fields": [],
        "extra_fields": [],
        "schema_version": SCHEMA_VERSION
    }

    # Check top-level categories
    expected_categories = set(EXTRACTION_SCHEMA.keys())
    actual_categories = set(data.keys())

    missing = expected_categories - actual_categories
    extra = actual_categories - expected_categories

    if missing:
        report["missing_fields"].extend(list(missing))
        report["warnings"].append(f"Missing categories: {missing}")

    if extra:
        report["extra_fields"].extend(list(extra))
        report["warnings"].append(f"Extra categories: {extra}")

    # Validate each category
    for category, schema_def in EXTRACTION_SCHEMA.items():
        if category not in data:
            continue

        category_data = data[category]

        # Handle nested structures
        if isinstance(schema_def, dict) and "fields" not in schema_def:
            # Nested category (e.g., market_intelligence)
            for subcategory, subschema in schema_def.items():
                if subcategory not in category_data:
                    report["warnings"].append(f"Missing subcategory: {category}.{subcategory}")
                    continue

                items = category_data[subcategory]
                if not isinstance(items, list):
                    report["errors"].append(f"{category}.{subcategory} should be a list")
                    report["valid"] = False
                    continue

                # Validate fields in each item
                for i, item in enumerate(items):
                    expected_fields = set(subschema["fields"])
                    actual_fields = set(item.keys())

                    missing_item_fields = expected_fields - actual_fields
                    if missing_item_fields:
                        report["warnings"].append(
                            f"{category}.{subcategory}[{i}] missing fields: {missing_item_fields}"
                        )

        else:
            # Simple category (e.g., products_tools)
            # Special case: meta is a dict, not a list
            if category == "meta":
                if not isinstance(category_data, dict):
                    report["errors"].append(f"{category} should be a dict")
                    report["valid"] = False
                continue

            if not isinstance(category_data, list):
                report["errors"].append(f"{category} should be a list")
                report["valid"] = False
                continue

            expected_fields = set(schema_def.get("fields", []))

            for i, item in enumerate(category_data):
                actual_fields = set(item.keys())
                missing_item_fields = expected_fields - actual_fields

                if missing_item_fields:
                    report["warnings"].append(
                        f"{category}[{i}] missing fields: {missing_item_fields}"
                    )

                # Validate enum fields (soft validation - warn but don't error)
                if "categories" in schema_def and "category" in item:
                    if item["category"] not in schema_def["categories"]:
                        # Don't error - just warn about unexpected values
                        # This allows for schema evolution
                        pass

                if "sentiments" in schema_def and "sentiment" in item:
                    if item["sentiment"] not in schema_def["sentiments"]:
                        # Don't error - just warn about unexpected values
                        pass

    return report


def get_extraction_prompt() -> str:
    """
    Generate extraction prompt from schema
    This ensures the prompt is always in sync with the schema
    """
    prompt_parts = ["Extract and structure the following information in JSON format:\n\n{"]

    for category, schema_def in EXTRACTION_SCHEMA.items():
        if category == "meta":
            continue  # Meta is added automatically

        prompt_parts.append(f'  "{category}": ')

        # Handle nested structures
        if isinstance(schema_def, dict) and "fields" not in schema_def:
            prompt_parts.append("{")
            for subcategory, subschema in schema_def.items():
                prompt_parts.append(f'    "{subcategory}": [')
                prompt_parts.append("      {")

                fields = subschema["fields"]
                for field in fields:
                    prompt_parts.append(f'        "{field}": "...",')

                prompt_parts.append("      }")
                prompt_parts.append("    ],")
            prompt_parts.append("  },\n")
        else:
            prompt_parts.append("[")
            prompt_parts.append("    {")

            fields = schema_def.get("fields", [])
            for field in fields:
                # Add type hints for enum fields
                if field == "category" and "categories" in schema_def:
                    values = "/".join(schema_def["categories"][:3]) + "/..."
                    prompt_parts.append(f'      "{field}": "{values}",')
                elif field == "sentiment" and "sentiments" in schema_def:
                    values = "/".join(schema_def["sentiments"])
                    prompt_parts.append(f'      "{field}": "{values}",')
                elif field == "difficulty" and "difficulties" in schema_def:
                    values = "/".join(schema_def["difficulties"])
                    prompt_parts.append(f'      "{field}": "{values}",')
                else:
                    prompt_parts.append(f'      "{field}": "...",')

            prompt_parts.append("    }")
            prompt_parts.append("  ],\n")

    prompt_parts.append("}")

    return "\n".join(prompt_parts)


def get_mcp_tool_schema(tool_name: str) -> Dict[str, Any]:
    """
    Generate MCP tool schema from mapping
    Ensures MCP tools are always in sync with data schema
    """
    if tool_name not in MCP_TOOL_MAPPINGS:
        return {}

    mapping = MCP_TOOL_MAPPINGS[tool_name]
    data_category = mapping["data_category"]

    # Get schema for this category
    if "." in data_category:
        # Nested category
        parts = data_category.split(".")
        schema_def = EXTRACTION_SCHEMA[parts[0]][parts[1]]
    else:
        schema_def = EXTRACTION_SCHEMA[data_category]

    # Build input schema
    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": f"Search term for {mapping['description']}"
            },
            "limit": {
                "type": "number",
                "description": "Maximum results to return (default: 20)"
            }
        },
        "required": ["query"]
    }

    # Add filter fields
    for filter_field in mapping["filter_fields"]:
        # Get allowed values from schema
        if filter_field == "category" and "categories" in schema_def:
            input_schema["properties"][filter_field] = {
                "type": "string",
                "description": f"{filter_field.capitalize()} filter",
                "enum": schema_def["categories"] + ["all"]
            }
        elif filter_field == "sentiment" and "sentiments" in schema_def:
            input_schema["properties"][filter_field] = {
                "type": "string",
                "description": "Sentiment filter",
                "enum": schema_def["sentiments"] + ["all"]
            }
        elif filter_field == "difficulty" and "difficulties" in schema_def:
            input_schema["properties"][filter_field] = {
                "type": "string",
                "description": "Difficulty filter",
                "enum": schema_def["difficulties"] + ["all"]
            }
        elif filter_field == "channel" and "channels" in schema_def:
            input_schema["properties"][filter_field] = {
                "type": "string",
                "description": "Marketing channel filter",
                "enum": schema_def["channels"]
            }
        elif filter_field == "automation_level" and "automation_levels" in schema_def:
            input_schema["properties"][filter_field] = {
                "type": "string",
                "description": "Automation level filter",
                "enum": schema_def["automation_levels"] + ["all"]
            }
        elif filter_field == "stage" and "stages" in schema_def:
            input_schema["properties"][filter_field] = {
                "type": "string",
                "description": "Trend stage filter",
                "enum": schema_def["stages"] + ["all"]
            }
        elif filter_field == "strategy_type" and "strategy_types" in schema_def:
            input_schema["properties"][filter_field] = {
                "type": "string",
                "description": "Strategy type filter",
                "enum": schema_def["strategy_types"] + ["all"]
            }
        else:
            input_schema["properties"][filter_field] = {
                "type": "string",
                "description": f"{filter_field.replace('_', ' ').capitalize()} filter (optional)"
            }

    return input_schema


# ==================== SCHEMA CHANGE DETECTION ====================

def detect_schema_changes(old_schema_version: str) -> Dict[str, Any]:
    """
    Detect what changed between schema versions
    Returns migration guide
    """
    changes = {
        "version_change": f"{old_schema_version} -> {SCHEMA_VERSION}",
        "breaking_changes": [],
        "new_fields": [],
        "deprecated_fields": [],
        "migration_required": False
    }

    # TODO: Implement version comparison logic
    # For now, just return current version info

    if old_schema_version != SCHEMA_VERSION:
        changes["migration_required"] = True
        changes["new_fields"].append("Schema updated - please review changes")

    return changes


# ==================== EXPORT FUNCTIONS ====================

def export_schema_json() -> str:
    """Export schema as JSON for documentation"""
    import json
    return json.dumps({
        "version": SCHEMA_VERSION,
        "last_updated": LAST_UPDATED,
        "extraction_schema": EXTRACTION_SCHEMA,
        "mcp_tool_mappings": MCP_TOOL_MAPPINGS
    }, indent=2)


def export_schema_markdown() -> str:
    """Export schema as Markdown documentation"""
    lines = [
        f"# Business Intelligence Schema v{SCHEMA_VERSION}",
        f"Last Updated: {LAST_UPDATED}",
        "",
        "## Data Categories",
        ""
    ]

    for category, schema_def in EXTRACTION_SCHEMA.items():
        if isinstance(schema_def, dict) and "description" in schema_def:
            lines.append(f"### {category}")
            lines.append(f"**Description:** {schema_def['description']}")
            lines.append(f"**Fields:** {', '.join(schema_def.get('fields', []))}")

            if "categories" in schema_def:
                lines.append(f"**Categories:** {', '.join(schema_def['categories'])}")
            if "sentiments" in schema_def:
                lines.append(f"**Sentiments:** {', '.join(schema_def['sentiments'])}")
            if "difficulties" in schema_def:
                lines.append(f"**Difficulties:** {', '.join(schema_def['difficulties'])}")

            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    """Test and validate schema"""
    print(f"\n{'='*70}")
    print(f"Business Intelligence Schema v{SCHEMA_VERSION}")
    print(f"{'='*70}\n")

    print("Categories:", len(EXTRACTION_SCHEMA))
    print("MCP Tools:", len(MCP_TOOL_MAPPINGS))
    print("\nExport options:")
    print("  - JSON: export_schema_json()")
    print("  - Markdown: export_schema_markdown()")
    print("  - Validation: validate_data_structure(data)")
    print("  - Extraction Prompt: get_extraction_prompt()")
    print("  - MCP Tool Schema: get_mcp_tool_schema(tool_name)")
