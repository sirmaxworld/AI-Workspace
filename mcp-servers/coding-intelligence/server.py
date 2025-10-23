#!/usr/bin/env python3
"""
Coding Intelligence MCP Server
SEMANTIC SEARCH for coding patterns, best practices, libraries, and tools

This MCP provides intelligent coding assistance through semantic search:
- Search coding patterns by description
- Find best practices for specific use cases
- Discover suitable OSS libraries
- Get security recommendations
- Find relevant MCP tools
- Architecture guidance

All powered by vector embeddings for semantic understanding.
"""

import os
import json
import logging
import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from mcp.server.fastmcp import FastMCP

# Load environment
load_dotenv('/Users/yourox/AI-Workspace/.env')

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level="INFO")

# Initialize MCP server
mcp = FastMCP(
    "Coding Intelligence",
    instructions="""SEMANTIC CODING INTELLIGENCE: Search patterns, best practices, libraries, and tools using natural language queries.

Use this MCP to:
- Find coding patterns by description (e.g., "testing framework for Node.js")
- Get best practices for specific use cases (e.g., "secure user authentication")
- Discover suitable OSS libraries (e.g., "lightweight date library")
- Find relevant MCP tools (e.g., "database integration tools")
- Get security and architecture recommendations

All searches use semantic understanding, not just keywords."""
)

# Database connection
DATABASE_URL = os.getenv('RAILWAY_DATABASE_URL')

# Load embedding model (cached after first load)
logger.info("Loading sentence-transformers model...")
MODEL = SentenceTransformer('all-MiniLM-L6-v2')
logger.info("Model loaded! (384 dimensions)")

def get_db_connection():
    """Get a database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def semantic_search(
    query: str,
    table: str,
    columns: List[str],
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 5
) -> List[Dict]:
    """
    Perform semantic search on a table

    Args:
        query: Natural language search query
        table: Table name to search
        columns: Columns to return in results
        filters: Optional WHERE clause filters
        limit: Maximum results to return

    Returns:
        List of matching records with similarity scores
    """
    try:
        # Generate query embedding
        query_embedding = MODEL.encode(query).tolist()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build WHERE clause
        where_clauses = ["embedding IS NOT NULL"]
        params = [query_embedding, query_embedding]

        if filters:
            for key, value in filters.items():
                where_clauses.append(f"{key} = %s")
                params.append(value)

        where_sql = " AND ".join(where_clauses)
        columns_str = ', '.join(columns)

        # Vector similarity search
        sql = f"""
            SELECT
                {columns_str},
                1 - (embedding <=> %s::vector) as similarity
            FROM {table}
            WHERE {where_sql}
            ORDER BY embedding <=> %s::vector
            LIMIT {limit};
        """

        cursor.execute(sql, params)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return []


# Resources
@mcp.resource("intelligence://stats")
def get_intelligence_stats() -> str:
    """Get Coding Intelligence database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get table counts
        cursor.execute("SELECT COUNT(*) as count FROM coding_patterns;")
        patterns_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM coding_rules;")
        rules_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM oss_commercial_repos;")
        oss_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM mcp_servers;")
        mcp_count = cursor.fetchone()['count']

        # Get embedding coverage
        cursor.execute("SELECT COUNT(*) as count FROM coding_patterns WHERE embedding IS NOT NULL;")
        patterns_embedded = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM coding_rules WHERE embedding IS NOT NULL;")
        rules_embedded = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM oss_commercial_repos WHERE embedding IS NOT NULL;")
        oss_embedded = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM mcp_servers WHERE embedding IS NOT NULL;")
        mcp_embedded = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        return f"""📊 Coding Intelligence Stats
{'=' * 50}
Coding Patterns: {patterns_count:,}
  Embedded: {patterns_embedded:,} ({(patterns_embedded/patterns_count*100):.1f}%)

Coding Rules: {rules_count:,}
  Embedded: {rules_embedded:,} ({(rules_embedded/rules_count*100):.1f}%)

OSS Libraries: {oss_count:,}
  Embedded: {oss_embedded:,} ({(oss_embedded/oss_count*100):.1f}%)

MCP Servers: {mcp_count:,}
  Embedded: {mcp_embedded:,} ({(mcp_embedded/mcp_count*100):.1f}%)

Total Intelligence Records: {patterns_count + rules_count + oss_count + mcp_count:,}
Total Embeddings: {patterns_embedded + rules_embedded + oss_embedded + mcp_embedded:,}

Embedding Model: all-MiniLM-L6-v2 (384d)
Search Type: Semantic Vector Search"""
    except Exception as e:
        return f"Error getting stats: {e}"


@mcp.resource("intelligence://languages")
def get_supported_languages() -> str:
    """Get list of programming languages covered"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get languages from patterns
        cursor.execute("""
            SELECT language, COUNT(*) as pattern_count
            FROM coding_patterns
            WHERE language IS NOT NULL
            GROUP BY language
            ORDER BY pattern_count DESC;
        """)
        pattern_langs = cursor.fetchall()

        # Get languages from OSS repos
        cursor.execute("""
            SELECT primary_language, COUNT(*) as repo_count
            FROM oss_commercial_repos
            WHERE primary_language IS NOT NULL
            GROUP BY primary_language
            ORDER BY repo_count DESC
            LIMIT 20;
        """)
        oss_langs = cursor.fetchall()

        cursor.close()
        conn.close()

        result = "📚 Supported Programming Languages\n"
        result += "=" * 50 + "\n\n"

        result += "Coding Patterns Coverage:\n"
        result += "-" * 50 + "\n"
        for lang in pattern_langs:
            result += f"  {lang['language']}: {lang['pattern_count']} patterns\n"

        result += "\nOSS Libraries Coverage:\n"
        result += "-" * 50 + "\n"
        for lang in oss_langs:
            result += f"  {lang['primary_language']}: {lang['repo_count']} libraries\n"

        return result
    except Exception as e:
        return f"Error getting languages: {e}"


# Core Tools
@mcp.tool()
def search_patterns(
    query: str,
    language: Optional[str] = None,
    pattern_type: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Search for coding patterns using natural language

    Args:
        query: Natural language description of what you're looking for
               Examples: "testing framework", "error handling", "database ORM"
        language: Optional filter by programming language (e.g., "JavaScript", "Python")
        pattern_type: Optional filter by pattern type (e.g., "framework", "library", "tool")
        limit: Maximum results to return (default: 5, max: 20)

    Returns:
        JSON with matching patterns and similarity scores

    Examples:
        - "unit testing framework for JavaScript"
        - "Python async web framework"
        - "React state management"
    """
    try:
        filters = {}
        if language:
            filters['language'] = language
        if pattern_type:
            filters['pattern_type'] = pattern_type

        limit = min(limit, 20)

        results = semantic_search(
            query=query,
            table='coding_patterns',
            columns=['pattern_name', 'description', 'language', 'pattern_type', 'framework'],
            filters=filters,
            limit=limit
        )

        return json.dumps({
            "query": query,
            "filters": {"language": language, "pattern_type": pattern_type},
            "count": len(results),
            "results": results
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_best_practices(
    query: str,
    category: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Find best practices and coding rules for specific use cases

    Args:
        query: Natural language description of the practice you need
               Examples: "secure user input", "API design", "error handling"
        category: Optional filter by category (e.g., "security", "performance", "style")
        limit: Maximum results to return (default: 5, max: 20)

    Returns:
        JSON with matching best practices and rules

    Examples:
        - "security best practices for authentication"
        - "performance optimization for databases"
        - "clean code principles"
    """
    try:
        filters = {}
        if category:
            filters['rule_category'] = category

        limit = min(limit, 20)

        results = semantic_search(
            query=query,
            table='coding_rules',
            columns=['rule_title', 'rule_description', 'rule_category', 'extracted_from'],
            filters=filters,
            limit=limit
        )

        return json.dumps({
            "query": query,
            "filters": {"category": category},
            "count": len(results),
            "results": results
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def suggest_library(
    query: str,
    language: Optional[str] = None,
    license_type: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Find suitable open-source libraries for your use case

    Args:
        query: Natural language description of what you need
               Examples: "date formatting", "HTTP client", "testing framework"
        language: Optional filter by programming language
        license_type: Optional filter by license (e.g., "MIT", "Apache-2.0")
        limit: Maximum results to return (default: 5, max: 20)

    Returns:
        JSON with matching libraries including GitHub info

    Examples:
        - "lightweight date library for JavaScript"
        - "Python HTTP client with async support"
        - "React component library"
    """
    try:
        filters = {}
        if language:
            filters['primary_language'] = language
        if license_type:
            filters['license_type'] = license_type

        limit = min(limit, 20)

        results = semantic_search(
            query=query,
            table='oss_commercial_repos',
            columns=['repo_full_name', 'description', 'primary_language', 'license_type',
                    'stars', 'repo_url'],
            filters=filters,
            limit=limit
        )

        return json.dumps({
            "query": query,
            "filters": {"language": language, "license_type": license_type},
            "count": len(results),
            "results": results
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def find_mcp_tool(
    query: str,
    category: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Discover MCP servers and tools for your use case

    Args:
        query: Natural language description of what you need
               Examples: "database integration", "web scraping", "file management"
        category: Optional filter by category
        limit: Maximum results to return (default: 5, max: 20)

    Returns:
        JSON with matching MCP servers

    Examples:
        - "database query tools"
        - "browser automation"
        - "API integration"
    """
    try:
        filters = {}
        if category:
            filters['category'] = category

        limit = min(limit, 20)

        results = semantic_search(
            query=query,
            table='mcp_servers',
            columns=['server_name', 'description', 'category', 'source_url', 'install_command'],
            filters=filters,
            limit=limit
        )

        return json.dumps({
            "query": query,
            "filters": {"category": category},
            "count": len(results),
            "results": results
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def analyze_security(
    query: str,
    limit: int = 5
) -> str:
    """
    Get security recommendations and best practices

    Args:
        query: Natural language description of security concern
               Examples: "SQL injection prevention", "password hashing", "XSS protection"
        limit: Maximum results to return (default: 5, max: 20)

    Returns:
        JSON with security-related best practices and patterns

    Examples:
        - "secure user authentication"
        - "prevent SQL injection"
        - "API security best practices"
    """
    try:
        limit = min(limit, 20)

        # Search both rules and patterns for security info
        # Use semantic search to find security-related content
        security_query = f"security {query}"
        rules = semantic_search(
            query=security_query,
            table='coding_rules',
            columns=['rule_title', 'rule_description', 'rule_category', 'extracted_from'],
            filters=None,
            limit=limit
        )

        patterns = semantic_search(
            query=query,
            table='coding_patterns',
            columns=['pattern_name', 'description', 'language', 'framework'],
            limit=limit // 2
        )

        return json.dumps({
            "query": query,
            "security_rules": {
                "count": len(rules),
                "results": rules
            },
            "security_patterns": {
                "count": len(patterns),
                "results": patterns
            }
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_architecture_advice(
    query: str,
    limit: int = 5
) -> str:
    """
    Get architecture and design pattern recommendations

    Args:
        query: Natural language description of architecture need
               Examples: "microservices pattern", "event-driven architecture", "API design"
        limit: Maximum results to return (default: 5, max: 20)

    Returns:
        JSON with architecture patterns and best practices

    Examples:
        - "scalable API architecture"
        - "microservices communication patterns"
        - "database design for multi-tenancy"
    """
    try:
        limit = min(limit, 20)

        # Search patterns and rules for architecture info
        patterns = semantic_search(
            query=query,
            table='coding_patterns',
            columns=['pattern_name', 'description', 'language', 'pattern_type', 'framework'],
            limit=limit // 2
        )

        rules = semantic_search(
            query=query,
            table='coding_rules',
            columns=['rule_title', 'rule_description', 'rule_category', 'extracted_from'],
            limit=limit // 2
        )

        return json.dumps({
            "query": query,
            "architecture_patterns": {
                "count": len(patterns),
                "results": patterns
            },
            "design_rules": {
                "count": len(rules),
                "results": rules
            }
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def discover_similar(
    item_type: str,
    item_name: str,
    limit: int = 5
) -> str:
    """
    Find similar patterns, libraries, or tools

    Args:
        item_type: Type of item to find similar to ("pattern", "library", "mcp_tool")
        item_name: Name of the item to find similar items for
        limit: Maximum results to return (default: 5, max: 20)

    Returns:
        JSON with similar items based on semantic similarity

    Examples:
        - discover_similar("library", "axios")
        - discover_similar("pattern", "Jest Testing")
        - discover_similar("mcp_tool", "database-query")
    """
    try:
        limit = min(limit, 20)

        # Map item types to tables
        type_mapping = {
            'pattern': ('coding_patterns', 'pattern_name',
                       ['pattern_name', 'description', 'language', 'pattern_type', 'framework']),
            'library': ('oss_commercial_repos', 'repo_full_name',
                       ['repo_full_name', 'description', 'primary_language', 'stars', 'repo_url']),
            'mcp_tool': ('mcp_servers', 'server_name',
                        ['server_name', 'description', 'category', 'source_url'])
        }

        if item_type not in type_mapping:
            return json.dumps({
                "error": f"Invalid item_type: {item_type}. Must be 'pattern', 'library', or 'mcp_tool'"
            }, indent=2)

        table, name_column, columns = type_mapping[item_type]

        # Get the item's description to use as search query
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT description
            FROM {table}
            WHERE {name_column} = %s
            LIMIT 1;
        """, (item_name,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return json.dumps({
                "error": f"Item not found: {item_name}"
            }, indent=2)

        # Use description as search query to find similar items
        description = result['description'] or item_name

        results = semantic_search(
            query=description,
            table=table,
            columns=columns,
            limit=limit + 1  # Get one extra to exclude the original item
        )

        # Filter out the original item
        results = [r for r in results if r.get(name_column) != item_name][:limit]

        return json.dumps({
            "item_type": item_type,
            "item_name": item_name,
            "count": len(results),
            "similar_items": results
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def check_code(
    code_description: str,
    language: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Validate code approach against best practices and rules

    Args:
        code_description: Natural language description of your code/approach
                         Examples: "storing passwords in database", "handling user input"
        language: Optional programming language filter
        limit: Maximum rules to return (default: 5, max: 20)

    Returns:
        JSON with relevant best practices and potential issues

    Examples:
        - "storing user passwords in plain text"
        - "handling file uploads from users"
        - "building SQL queries with string concatenation"
    """
    try:
        limit = min(limit, 20)

        filters = {}
        if language:
            # Try to find language-specific rules
            filters['language'] = language

        results = semantic_search(
            query=code_description,
            table='coding_rules',
            columns=['rule_title', 'rule_description', 'rule_category', 'extracted_from'],
            filters=filters if language else None,
            limit=limit
        )

        return json.dumps({
            "code_description": code_description,
            "language": language,
            "count": len(results),
            "relevant_rules": results,
            "recommendation": "Review these best practices before proceeding"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


if __name__ == "__main__":
    logger.info("Starting Coding Intelligence MCP Server")
    logger.info(f"Embedding Model: all-MiniLM-L6-v2 (384 dimensions)")
    logger.info(f"Search Type: Semantic Vector Search")

    # Test connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()['version']
        logger.info(f"Connected to: {version.split(',')[0]}")

        # Test embedding model
        test_embedding = MODEL.encode("test query")
        logger.info(f"Embedding model ready: {len(test_embedding)} dimensions")

        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        exit(1)

    logger.info("🚀 Coding Intelligence MCP Server ready!")
    mcp.run(transport="stdio")
