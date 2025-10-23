#!/usr/bin/env python3
"""
Railway PostgreSQL MCP Server
LOW-LEVEL DATABASE ACCESS for advanced users

⚠️ For curated, safe access to intelligence data, use BI-Vault instead!

This MCP provides direct SQL access to Railway PostgreSQL:
- Raw database queries (execute_sql_query)
- Direct table access
- Advanced filtering and analytics
- Read-only access for safety

Use Cases:
- Advanced database operations
- Custom SQL queries
- Direct data exploration
- Power user access

For most use cases, prefer BI-Vault which provides safe, curated intelligence tools.
"""

import os
import json
import logging
import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

# Load environment
load_dotenv('/Users/yourox/AI-Workspace/.env')

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "Railway PostgreSQL",
    instructions="LOW-LEVEL DATABASE ACCESS: Direct SQL queries on Railway PostgreSQL. For curated intelligence, use BI-Vault. Read-only for safety."
)

# Database connection
DATABASE_URL = os.getenv('RAILWAY_DATABASE_URL')

def get_db_connection():
    """Get a database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


# Resources
@mcp.resource("railway://stats")
def get_database_stats() -> str:
    """Get Railway PostgreSQL database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get table counts
        cursor.execute("SELECT COUNT(*) FROM yc_companies_enriched;")
        yc_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) FROM videos;")
        video_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) FROM video_transcripts;")
        transcript_count = cursor.fetchone()['count']

        # Get enrichment stats
        cursor.execute("SELECT COUNT(*) FROM yc_companies_enriched WHERE phase1_complete = TRUE;")
        phase1 = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) FROM yc_companies_enriched WHERE phase8_complete = TRUE;")
        phase8 = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        return f"""📊 Railway PostgreSQL Stats
{'=' * 40}
YC Companies: {yc_count:,}
  Phase 1 (Web Data): {phase1:,} ({(phase1/yc_count*100):.1f}%)
  Phase 8 (AI Insights): {phase8:,} ({(phase8/yc_count*100):.1f}%)

Video Transcripts: {video_count:,}
  Transcripts: {transcript_count:,}

Database: Railway PostgreSQL 16.10
Extensions: pgvector 0.8.1
Mode: READ-ONLY"""
    except Exception as e:
        return f"Error getting stats: {e}"


@mcp.resource("railway://schema")
def get_database_schema() -> str:
    """Get database schema information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()

        schema_info = "📋 Railway PostgreSQL Schema\n"
        schema_info += "=" * 40 + "\n\n"

        for table in tables:
            table_name = table['table_name']
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()['count']

            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
                LIMIT 10;
            """)
            columns = cursor.fetchall()

            schema_info += f"\n{table_name} ({count:,} records)\n"
            schema_info += "-" * 40 + "\n"
            for col in columns:
                schema_info += f"  - {col['column_name']}: {col['data_type']}\n"

        cursor.close()
        conn.close()

        return schema_info
    except Exception as e:
        return f"Error getting schema: {e}"


# Tools
@mcp.tool()
def search_yc_companies(
    query: str = "",
    batch: str = None,
    phase1_complete: bool = None,
    phase8_complete: bool = None,
    limit: int = 20
) -> str:
    """
    Search Y Combinator companies in Railway PostgreSQL

    Args:
        query: Search term (searches name, slug, website)
        batch: Filter by YC batch (e.g., "Summer 2017", "W21")
        phase1_complete: Filter by Phase 1 completion status
        phase8_complete: Filter by Phase 8 (AI insights) completion status
        limit: Maximum results to return (default: 20, max: 100)

    Returns:
        JSON with matching companies including all enrichment data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query
        where_clauses = []
        params = []

        if query:
            where_clauses.append("(name ILIKE %s OR slug ILIKE %s OR website ILIKE %s)")
            search_pattern = f"%{query}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        if batch:
            where_clauses.append("batch = %s")
            params.append(batch)

        if phase1_complete is not None:
            where_clauses.append("phase1_complete = %s")
            params.append(phase1_complete)

        if phase8_complete is not None:
            where_clauses.append("phase8_complete = %s")
            params.append(phase8_complete)

        where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

        # Limit to max 100
        limit = min(limit, 100)

        sql = f"""
            SELECT
                slug, name, yc_id, batch, website,
                phase1_complete, phase2_complete, phase3_complete, phase4_complete,
                phase5_complete, phase6_complete, phase7_complete, phase8_complete,
                web_data, ai_insights,
                enriched_at, created_at
            FROM yc_companies_enriched
            WHERE {where_sql}
            ORDER BY name
            LIMIT %s;
        """

        params.append(limit)
        cursor.execute(sql, params)
        results = cursor.fetchall()

        # Convert to list of dicts
        companies = []
        for row in results:
            company = dict(row)
            # Convert JSONB to dict
            if company.get('web_data'):
                company['web_data'] = dict(company['web_data'])
            if company.get('ai_insights'):
                company['ai_insights'] = dict(company['ai_insights'])
            companies.append(company)

        cursor.close()
        conn.close()

        return json.dumps({
            "query": query,
            "filters": {
                "batch": batch,
                "phase1_complete": phase1_complete,
                "phase8_complete": phase8_complete
            },
            "count": len(companies),
            "results": companies
        }, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_yc_company_by_slug(slug: str) -> str:
    """
    Get a specific YC company by slug with all enrichment data

    Args:
        slug: Company slug (e.g., "stripe", "airbnb", "dropbox")

    Returns:
        JSON with complete company data including all enrichment phases
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM yc_companies_enriched
            WHERE slug = %s;
        """, (slug,))

        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return json.dumps({"error": f"Company not found: {slug}"}, indent=2)

        company = dict(result)

        # Convert JSONB fields to dicts
        jsonb_fields = ['web_data', 'geographic_data', 'github_data', 'network_data',
                        'patent_data', 'reviews_data', 'hiring_data', 'ai_insights', 'enriched_data']

        for field in jsonb_fields:
            if company.get(field):
                company[field] = dict(company[field])

        cursor.close()
        conn.close()

        return json.dumps(company, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def search_videos(
    query: str = "",
    channel_name: str = None,
    min_transcript_length: int = 1000,
    limit: int = 20
) -> str:
    """
    Search video transcripts in Railway PostgreSQL

    Args:
        query: Search term (searches title, channel, transcript)
        channel_name: Filter by channel name
        min_transcript_length: Minimum transcript length in characters
        limit: Maximum results to return (default: 20, max: 100)

    Returns:
        JSON with matching videos including transcripts
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        where_clauses = []
        params = []

        if query:
            where_clauses.append("""
                (v.title ILIKE %s OR v.channel_name ILIKE %s OR vt.transcript_full ILIKE %s)
            """)
            search_pattern = f"%{query}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        if channel_name:
            where_clauses.append("v.channel_name = %s")
            params.append(channel_name)

        if min_transcript_length:
            where_clauses.append("LENGTH(vt.transcript_full) >= %s")
            params.append(min_transcript_length)

        where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

        limit = min(limit, 100)

        sql = f"""
            SELECT
                v.video_id, v.title, v.url, v.channel_name, v.channel_id,
                v.duration_seconds, v.published_date,
                LENGTH(vt.transcript_full) as transcript_length,
                SUBSTRING(vt.transcript_full, 1, 500) as transcript_preview,
                v.metadata
            FROM videos v
            JOIN video_transcripts vt ON v.video_id = vt.video_id
            WHERE {where_sql}
            ORDER BY v.created_at DESC
            LIMIT %s;
        """

        params.append(limit)
        cursor.execute(sql, params)
        results = cursor.fetchall()

        videos = []
        for row in results:
            video = dict(row)
            if video.get('metadata'):
                video['metadata'] = dict(video['metadata'])
            videos.append(video)

        cursor.close()
        conn.close()

        return json.dumps({
            "query": query,
            "filters": {
                "channel_name": channel_name,
                "min_transcript_length": min_transcript_length
            },
            "count": len(videos),
            "results": videos
        }, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_video_transcript(video_id: str) -> str:
    """
    Get full transcript for a specific video

    Args:
        video_id: YouTube video ID

    Returns:
        JSON with complete video data and full transcript
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                v.video_id, v.title, v.url, v.channel_name,
                v.duration_seconds, v.published_date,
                vt.transcript_full,
                v.metadata
            FROM videos v
            JOIN video_transcripts vt ON v.video_id = vt.video_id
            WHERE v.video_id = %s;
        """, (video_id,))

        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return json.dumps({"error": f"Video not found: {video_id}"}, indent=2)

        video = dict(result)
        if video.get('metadata'):
            video['metadata'] = dict(video['metadata'])

        cursor.close()
        conn.close()

        return json.dumps(video, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_yc_batch_stats(batch: str = None) -> str:
    """
    Get statistics for YC batches

    Args:
        batch: Specific batch to analyze (optional, e.g., "Summer 2017")
               If not provided, returns stats for all batches

    Returns:
        JSON with batch statistics including enrichment completion rates
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if batch:
            cursor.execute("""
                SELECT
                    batch,
                    COUNT(*) as total_companies,
                    SUM(CASE WHEN phase1_complete THEN 1 ELSE 0 END) as phase1_count,
                    SUM(CASE WHEN phase8_complete THEN 1 ELSE 0 END) as phase8_count
                FROM yc_companies_enriched
                WHERE batch = %s
                GROUP BY batch;
            """, (batch,))
        else:
            cursor.execute("""
                SELECT
                    batch,
                    COUNT(*) as total_companies,
                    SUM(CASE WHEN phase1_complete THEN 1 ELSE 0 END) as phase1_count,
                    SUM(CASE WHEN phase8_complete THEN 1 ELSE 0 END) as phase8_count
                FROM yc_companies_enriched
                GROUP BY batch
                ORDER BY batch DESC
                LIMIT 50;
            """)

        results = cursor.fetchall()

        batch_stats = []
        for row in results:
            stats = dict(row)
            stats['phase1_percentage'] = round((stats['phase1_count'] / stats['total_companies'] * 100), 1)
            stats['phase8_percentage'] = round((stats['phase8_count'] / stats['total_companies'] * 100), 1)
            batch_stats.append(stats)

        cursor.close()
        conn.close()

        return json.dumps({
            "batch": batch,
            "count": len(batch_stats),
            "results": batch_stats
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def execute_sql_query(sql: str, limit: int = 100) -> str:
    """
    Execute a custom SQL query on Railway PostgreSQL (READ-ONLY)

    Args:
        sql: SQL query to execute (SELECT only, no modifications allowed)
        limit: Maximum rows to return (default: 100, max: 1000)

    Returns:
        JSON with query results

    Security:
        - Only SELECT queries allowed
        - Automatically adds LIMIT clause
        - Read-only transaction mode
    """
    try:
        # Security: only allow SELECT queries
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith('SELECT'):
            return json.dumps({
                "error": "Only SELECT queries are allowed. No modifications permitted."
            }, indent=2)

        # Check for dangerous keywords
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return json.dumps({
                    "error": f"Query contains forbidden keyword: {keyword}"
                }, indent=2)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Add LIMIT if not present
        limit = min(limit, 1000)
        if 'LIMIT' not in sql_upper:
            sql = f"{sql.rstrip(';')} LIMIT {limit};"

        cursor.execute(sql)
        results = cursor.fetchall()

        # Convert to list of dicts
        rows = [dict(row) for row in results]

        cursor.close()
        conn.close()

        return json.dumps({
            "query": sql,
            "count": len(rows),
            "results": rows
        }, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


if __name__ == "__main__":
    logger.info("Starting Railway PostgreSQL MCP Server")
    logger.info(f"Database: Railway PostgreSQL (read-only mode)")

    # Test connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()['version']
        logger.info(f"Connected to: {version.split(',')[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        exit(1)

    mcp.run(transport="stdio")
