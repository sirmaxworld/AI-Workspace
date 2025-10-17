#!/usr/bin/env python3
"""
Y Combinator Companies MCP Server
Provides MCP-compliant access to YC company database
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "YC Companies",
    instructions="Access and search Y Combinator company data with 5,490+ companies from all YC batches."
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")


def get_supabase_client():
    """Get or create Supabase client"""
    try:
        from supabase import create_client
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except ImportError:
        raise ImportError("supabase-py not installed. Install with: pip install supabase")


@mcp.resource("yc://stats")
def get_yc_stats() -> str:
    """Get Y Combinator companies statistics"""
    try:
        supabase = get_supabase_client()

        # Get all companies for statistics
        response = supabase.table('yc_companies').select('batch,status,industry,is_hiring,top_company,nonprofit,team_size').execute()
        companies = response.data

        if not companies:
            return "No YC companies data available yet. Run the extractor first."

        # Calculate statistics
        total = len(companies)
        hiring = sum(1 for c in companies if c.get('is_hiring'))
        top = sum(1 for c in companies if c.get('top_company'))
        nonprofit = sum(1 for c in companies if c.get('nonprofit'))

        # Status breakdown
        statuses = {}
        for company in companies:
            status = company.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1

        # Top industries
        industries = {}
        for company in companies:
            industry = company.get('industry', 'unknown')
            industries[industry] = industries.get(industry, 0) + 1

        top_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:10]

        # Recent batches
        batches = {}
        for company in companies:
            batch = company.get('batch', 'unknown')
            batches[batch] = batches.get(batch, 0) + 1

        recent_batches = sorted(batches.items(), reverse=True)[:10]

        # Average team size
        team_sizes = [c.get('team_size', 0) for c in companies if c.get('team_size')]
        avg_team_size = round(sum(team_sizes) / len(team_sizes), 1) if team_sizes else 0

        # Format response
        lines = [
            "📊 Y Combinator Companies Statistics",
            "=" * 60,
            f"Total Companies: {total}",
            f"Currently Hiring: {hiring}",
            f"Top Companies: {top}",
            f"Non-profit: {nonprofit}",
            f"Average Team Size: {avg_team_size}",
            "",
            "By Status:",
        ]

        for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {status}: {count}")

        lines.append("")
        lines.append("Top Industries:")
        for industry, count in top_industries:
            lines.append(f"  {industry}: {count}")

        lines.append("")
        lines.append("Recent Batches:")
        for batch, count in recent_batches:
            lines.append(f"  {batch}: {count} companies")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching statistics: {str(e)}"


@mcp.resource("yc://recent")
def get_recent_companies() -> str:
    """Get recently added YC companies"""
    try:
        supabase = get_supabase_client()

        # Get 20 most recent companies
        response = supabase.table('yc_companies').select('name,one_liner,batch,status,is_hiring,website').order('created_at', desc=True).limit(20).execute()

        companies = response.data
        if not companies:
            return "No companies found."

        lines = ["📋 Recently Added YC Companies", "=" * 60, ""]

        for company in companies:
            hiring_badge = " 🟢 HIRING" if company.get('is_hiring') else ""
            lines.append(f"**{company['name']}** ({company.get('batch', 'N/A')}){hiring_badge}")
            lines.append(f"   {company.get('one_liner', 'No description')}")
            lines.append(f"   Status: {company.get('status', 'unknown')} | {company.get('website', 'No website')}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching recent companies: {str(e)}"


@mcp.resource("yc://hiring")
def get_hiring_companies() -> str:
    """Get YC companies that are currently hiring"""
    try:
        supabase = get_supabase_client()

        # Get companies that are hiring
        response = supabase.table('yc_companies').select('name,one_liner,batch,industry,team_size,website').eq('is_hiring', True).limit(50).execute()

        companies = response.data
        if not companies:
            return "No hiring companies found."

        lines = [f"🟢 YC Companies Currently Hiring ({len(companies)})", "=" * 60, ""]

        for company in companies:
            team_size = company.get('team_size', 'N/A')
            lines.append(f"**{company['name']}** ({company.get('batch', 'N/A')})")
            lines.append(f"   {company.get('one_liner', 'No description')}")
            lines.append(f"   Industry: {company.get('industry', 'N/A')} | Team: {team_size} | {company.get('website', 'No website')}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching hiring companies: {str(e)}"


@mcp.tool()
def search_companies(
    query: Optional[str] = None,
    batch: Optional[str] = None,
    industry: Optional[str] = None,
    status: Optional[str] = None,
    is_hiring: Optional[bool] = None,
    top_company: Optional[bool] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search Y Combinator companies with filters

    Args:
        query: Text to search in company name and description
        batch: Filter by YC batch (e.g., "W21", "S20")
        industry: Filter by industry
        status: Filter by status (Active, Acquired, Public, etc.)
        is_hiring: Filter by hiring status
        top_company: Filter top companies only
        limit: Maximum results to return

    Returns:
        List of matching companies with details
    """
    try:
        supabase = get_supabase_client()

        # Build query
        query_builder = supabase.table('yc_companies').select('*')

        # Apply filters
        if batch:
            query_builder = query_builder.eq('batch', batch)
        if industry:
            query_builder = query_builder.eq('industry', industry)
        if status:
            query_builder = query_builder.eq('status', status)
        if is_hiring is not None:
            query_builder = query_builder.eq('is_hiring', is_hiring)
        if top_company is not None:
            query_builder = query_builder.eq('top_company', top_company)

        # Text search
        if query:
            query_builder = query_builder.or_(f"name.ilike.%{query}%,one_liner.ilike.%{query}%")

        # Execute query
        query_builder = query_builder.limit(limit)
        response = query_builder.execute()

        return response.data

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_company_by_slug(slug: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific YC company by slug

    Args:
        slug: Company slug (e.g., "airbnb", "stripe", "openai")

    Returns:
        Company details including full description, founders, etc.
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table('yc_companies').select('*').eq('slug', slug).execute()

        if not response.data:
            return {"error": f"Company '{slug}' not found"}

        return response.data[0]

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_companies_by_batch(batch: str) -> List[Dict[str, Any]]:
    """
    Get all companies from a specific YC batch

    Args:
        batch: YC batch code (e.g., "W21", "S20", "F25")

    Returns:
        List of companies from that batch
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table('yc_companies').select('*').eq('batch', batch).execute()

        return response.data

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_companies_by_industry(industry: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get companies from a specific industry

    Args:
        industry: Industry name (e.g., "B2B", "Healthcare", "Fintech")
        limit: Maximum results to return

    Returns:
        List of companies in that industry
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table('yc_companies').select('*').eq('industry', industry).limit(limit).execute()

        return response.data

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_top_companies(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get YC top companies

    Args:
        limit: Maximum results to return

    Returns:
        List of top YC companies
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table('yc_companies').select('*').eq('top_company', True).limit(limit).execute()

        return response.data

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_batches() -> List[Dict[str, Any]]:
    """
    Get list of all YC batches with company counts

    Returns:
        List of batches with metadata
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table('yc_companies').select('batch').execute()

        # Count companies per batch
        batch_counts = {}
        for company in response.data:
            batch = company.get('batch', 'unknown')
            batch_counts[batch] = batch_counts.get(batch, 0) + 1

        batches = [
            {"batch": batch, "count": count}
            for batch, count in batch_counts.items()
        ]

        # Sort by batch (most recent first)
        batches.sort(key=lambda x: x['batch'], reverse=True)

        return batches

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_industries() -> List[Dict[str, Any]]:
    """
    Get list of all YC industries with company counts

    Returns:
        List of industries with metadata
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table('yc_companies').select('industry').execute()

        # Count companies per industry
        industry_counts = {}
        for company in response.data:
            industry = company.get('industry', 'unknown')
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        industries = [
            {"industry": industry, "count": count}
            for industry, count in industry_counts.items()
        ]

        # Sort by count (most companies first)
        industries.sort(key=lambda x: x['count'], reverse=True)

        return industries

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def search_similar_companies(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Semantic search for YC companies using embeddings

    Args:
        query: Natural language search query (e.g., "AI companies working on healthcare")
        limit: Maximum results to return

    Returns:
        List of semantically similar companies
    """
    try:
        from openai import OpenAI

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return [{"error": "OpenAI API key not configured"}]

        # Generate embedding for query
        openai_client = OpenAI(api_key=openai_api_key)
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding

        # Search using the search function
        supabase = get_supabase_client()
        result = supabase.rpc(
            'search_yc_companies',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.5,
                'match_count': limit
            }
        ).execute()

        return result.data

    except Exception as e:
        return [{"error": str(e)}]


if __name__ == "__main__":
    print("Starting YC Companies MCP Server...")
    print(f"Supabase configured: {bool(SUPABASE_URL and SUPABASE_KEY)}")
    mcp.run(transport="stdio")
