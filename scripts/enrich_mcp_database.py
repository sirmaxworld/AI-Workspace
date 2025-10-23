#!/usr/bin/env python3
"""
MCP Database Enrichment Script
Automatically extracts and populates MCP server metadata, tools, and use cases
"""
import os
import re
import json
import psycopg2
import psycopg2.extras
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'),
                           cursor_factory=psycopg2.extras.RealDictCursor)

def extract_server_info(file_path):
    """Extract server information from Python file"""
    with open(file_path, 'r') as f:
        content = f.read()

    info = {
        'description': None,
        'tools': [],
        'resources': [],
        'env_vars': [],
        'categories': []
    }

    # Extract description from docstring
    doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if doc_match:
        full_doc = doc_match.group(1).strip()
        # Get first paragraph as description
        paragraphs = [p.strip() for p in full_doc.split('\n\n') if p.strip()]
        if paragraphs:
            info['description'] = paragraphs[0].replace('\n', ' ')

    # Extract tools with full details
    tool_pattern = r'@mcp\.tool\(\)\s*def\s+(\w+)\(([^)]*)\)\s*->\s*str:\s*"""(.*?)"""'
    tool_matches = re.findall(tool_pattern, content, re.DOTALL)

    for tool_name, params_str, tool_doc in tool_matches:
        # Parse tool documentation
        doc_lines = [line.strip() for line in tool_doc.strip().split('\n') if line.strip()]
        tool_desc = doc_lines[0] if doc_lines else ''

        # Extract Args section
        args = []
        in_args = False
        in_returns = False
        for line in doc_lines:
            if line.startswith('Args:'):
                in_args = True
                in_returns = False
                continue
            elif line.startswith('Returns:'):
                in_args = False
                in_returns = True
                continue
            elif in_args and line and not line.endswith(':'):
                # Parse arg line: "param: description"
                if ':' in line:
                    param_name = line.split(':')[0].strip()
                    args.append(param_name)

        info['tools'].append({
            'name': tool_name,
            'description': tool_desc,
            'parameters': args
        })

    # Extract resources
    resource_pattern = r'@mcp\.resource\(["\']([^"\']+)["\']\)'
    resources = re.findall(resource_pattern, content)
    info['resources'] = resources

    # Extract environment variables
    env_pattern = r'os\.getenv\(["\']([^"\']+)["\']\)'
    env_vars = set(re.findall(env_pattern, content))
    info['env_vars'] = list(env_vars)

    return info

def enrich_custom_servers():
    """Enrich custom MCP servers from code"""
    print("="*80)
    print(" "*20 + "ENRICHING CUSTOM MCP SERVERS")
    print("="*80)

    custom_servers = [
        {
            'name': 'Railway PostgreSQL',
            'file': '/Users/yourox/AI-Workspace/mcp-servers/railway-postgres/server.py',
            'author': 'yourox',
            'category': 'database'
        },
        {
            'name': 'Business Intelligence',
            'file': '/Users/yourox/AI-Workspace/mcp-servers/business-intelligence/server.py',
            'author': 'yourox',
            'category': 'ai'
        },
        {
            'name': 'Coding History',
            'file': '/Users/yourox/AI-Workspace/mcp-servers/coding-history/server.py',
            'author': 'yourox',
            'category': 'general'
        },
        {
            'name': 'Cycling Intelligence',
            'file': '/Users/yourox/AI-Workspace/mcp-servers/cycling-intelligence/server.py',
            'author': 'yourox',
            'category': 'ai'
        }
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    total_tools = 0
    total_resources = 0

    for server in custom_servers:
        if not Path(server['file']).exists():
            print(f"⚠️  Skipping {server['name']}: File not found")
            continue

        print(f"\n📦 Processing {server['name']}...")

        # Extract info
        info = extract_server_info(server['file'])

        # Update server record
        cursor.execute("""
            UPDATE mcp_servers SET
                description = %s,
                author = %s,
                tools_count = %s,
                resources_count = %s,
                has_tools = %s,
                has_resources = %s,
                required_env_vars = %s,
                docs_quality_score = %s
            WHERE server_name = %s;
        """, (
            info['description'],
            server['author'],
            len(info['tools']),
            len(info['resources']),
            len(info['tools']) > 0,
            len(info['resources']) > 0,
            info['env_vars'],
            85,  # High quality for our custom servers
            server['name']
        ))

        # Get server ID
        cursor.execute("SELECT id FROM mcp_servers WHERE server_name = %s;", (server['name'],))
        server_id = cursor.fetchone()['id']

        # Insert tools
        for tool in info['tools']:
            # Check if tool exists
            cursor.execute("""
                SELECT id FROM mcp_server_tools
                WHERE server_id = %s AND tool_name = %s;
            """, (server_id, tool['name']))

            if cursor.fetchone():
                # Update
                cursor.execute("""
                    UPDATE mcp_server_tools SET
                        description = %s,
                        required_params = %s
                    WHERE server_id = %s AND tool_name = %s;
                """, (
                    tool['description'],
                    tool['parameters'],
                    server_id,
                    tool['name']
                ))
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO mcp_server_tools (
                        server_id,
                        tool_name,
                        description,
                        required_params
                    ) VALUES (%s, %s, %s, %s);
                """, (
                    server_id,
                    tool['name'],
                    tool['description'],
                    tool['parameters']
                ))

        total_tools += len(info['tools'])
        total_resources += len(info['resources'])

        print(f"   ✅ {len(info['tools'])} tools, {len(info['resources'])} resources")
        print(f"      Description: {info['description'][:60]}...")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n{'='*80}")
    print(f"✅ Custom server enrichment complete!")
    print(f"   Total tools: {total_tools}")
    print(f"   Total resources: {total_resources}")
    print(f"{'='*80}")

def add_basic_use_cases():
    """Add basic use cases for MCP servers"""
    print("\n" + "="*80)
    print(" "*25 + "ADDING USE CASES")
    print("="*80)

    use_cases = [
        {
            'server': 'Railway PostgreSQL',
            'title': 'Search YC Companies for Market Research',
            'description': 'Use Railway PostgreSQL MCP to search and analyze Y Combinator companies with all enrichment data including AI insights',
            'industry': 'research',
            'difficulty': 'beginner',
            'setup_steps': [
                'Ensure Railway PostgreSQL MCP server is running',
                'Use search_yc_companies() tool',
                'Filter by batch, enrichment phase, or keywords'
            ],
            'example_prompts': [
                'Find all YC companies from Summer 2023',
                'Search YC companies with AI insights in fintech',
                'Get Stripe\'s complete enrichment data'
            ],
            'tools_used': ['search_yc_companies', 'get_yc_company_by_slug']
        },
        {
            'server': 'Railway PostgreSQL',
            'title': 'Search Video Transcripts for Learning',
            'description': 'Search across 454 video transcripts to find specific topics, techniques, or information',
            'industry': 'development',
            'difficulty': 'beginner',
            'setup_steps': [
                'Use search_videos() tool',
                'Provide search keywords',
                'Filter by channel or transcript length'
            ],
            'example_prompts': [
                'Find videos about machine learning',
                'Search transcripts mentioning \"AI tools\"',
                'Get full transcript for video ID'
            ],
            'tools_used': ['search_videos', 'get_video_transcript']
        },
        {
            'server': 'Business Intelligence',
            'title': 'Analyze Market Trends and Opportunities',
            'description': 'Use BI MCP to discover market trends, startup ideas, and growth tactics from curated business intelligence',
            'industry': 'business',
            'difficulty': 'intermediate',
            'setup_steps': [
                'Use search_trends() for market signals',
                'Use search_startup_ideas() for opportunities',
                'Use get_meta_trends() for cross-video analysis'
            ],
            'example_prompts': [
                'What are emerging AI trends?',
                'Find validated startup ideas in SaaS',
                'Show me growth tactics for content marketing'
            ],
            'tools_used': ['search_trends', 'search_startup_ideas', 'get_meta_trends']
        },
        {
            'server': 'Business Intelligence',
            'title': 'Product Research and Tool Discovery',
            'description': 'Discover products, tools, and their use cases from analyzed business intelligence',
            'industry': 'development',
            'difficulty': 'beginner',
            'setup_steps': [
                'Use search_products() for tools',
                'Filter by category and sentiment',
                'Check product ecosystem analysis'
            ],
            'example_prompts': [
                'Find AI tools for content creation',
                'Search for recommended SaaS products',
                'What are the most popular developer tools?'
            ],
            'tools_used': ['search_products', 'get_product_ecosystem']
        },
        {
            'server': 'Coding History',
            'title': 'Capture Development Session for Documentation',
            'description': 'Automatically capture terminal commands and output during development to create documentation',
            'industry': 'development',
            'difficulty': 'intermediate',
            'setup_steps': [
                'Start capture with start_capture()',
                'Work on your project normally',
                'Stop capture when done',
                'Review captured history'
            ],
            'example_prompts': [
                'Start capturing my coding session',
                'Show me the recent command history',
                'Stop the current capture'
            ],
            'tools_used': ['start_capture', 'stop_capture', 'capture_command']
        },
        {
            'server': 'Cycling Intelligence',
            'title': 'Research Mountain Bikes and Components',
            'description': 'Search Pinkbike reviews and field tests to find the best mountain bikes and components',
            'industry': 'creative',
            'difficulty': 'beginner',
            'setup_steps': [
                'Use search_mountain_bikes() for bikes',
                'Use search_components() for parts',
                'Check field_tests() for rankings'
            ],
            'example_prompts': [
                'Find the best trail bikes under $5000',
                'Search for reliable suspension forks',
                'What are current mountain bike trends?'
            ],
            'tools_used': ['search_mountain_bikes', 'search_components', 'search_cycling_trends']
        },
        {
            'server': 'Business Intelligence',
            'title': 'YC Company Analysis with Enrichments',
            'description': 'Analyze YC companies with all 8 phases of enrichment including web data, GitHub activity, and AI insights',
            'industry': 'research',
            'difficulty': 'advanced',
            'setup_steps': [
                'Use search_yc_companies() from BI MCP',
                'Filter by batch and enrichment phases',
                'Analyze AI insights and market positioning'
            ],
            'example_prompts': [
                'Find YC companies with Phase 8 AI insights',
                'Analyze companies in AI/ML space',
                'Compare YC batches by enrichment completion'
            ],
            'tools_used': ['search_yc_companies', 'get_database_stats']
        }
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    inserted = 0

    for uc in use_cases:
        # Get server ID
        cursor.execute("SELECT id FROM mcp_servers WHERE server_name = %s;", (uc['server'],))
        result = cursor.fetchone()

        if not result:
            print(f"   ⚠️  Server not found: {uc['server']}")
            continue

        server_id = result['id']

        # Check if use case exists
        cursor.execute("""
            SELECT id FROM mcp_use_cases
            WHERE server_id = %s AND use_case_title = %s;
        """, (server_id, uc['title']))

        if cursor.fetchone():
            print(f"   ⏭️  Use case exists: {uc['title']}")
            continue

        # Insert use case
        cursor.execute("""
            INSERT INTO mcp_use_cases (
                server_id,
                use_case_title,
                use_case_description,
                industry,
                difficulty_level,
                setup_steps,
                example_prompts,
                tools_used,
                verified
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            server_id,
            uc['title'],
            uc['description'],
            uc['industry'],
            uc['difficulty'],
            uc['setup_steps'],
            uc['example_prompts'],
            uc['tools_used'],
            True
        ))

        inserted += 1
        print(f"   ✅ Added: {uc['title']}")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n{'='*80}")
    print(f"✅ Use cases added: {inserted}")
    print(f"{'='*80}")

def show_summary():
    """Show enrichment summary"""
    print("\n" + "="*80)
    print(" "*25 + "ENRICHMENT SUMMARY")
    print("="*80)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get counts
    cursor.execute("SELECT COUNT(*) as count FROM mcp_servers WHERE description IS NOT NULL;")
    servers_with_desc = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM mcp_server_tools;")
    total_tools = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM mcp_use_cases;")
    total_use_cases = cursor.fetchone()['count']

    cursor.execute("""
        SELECT server_name, tools_count
        FROM mcp_servers
        WHERE tools_count > 0
        ORDER BY tools_count DESC;
    """)
    servers_with_tools = cursor.fetchall()

    print(f"\n📊 Database Status:")
    print(f"   Servers with descriptions: {servers_with_desc}/10")
    print(f"   Total tools documented: {total_tools}")
    print(f"   Total use cases: {total_use_cases}")

    print(f"\n🔧 Tools by Server:")
    for server in servers_with_tools:
        print(f"   • {server['server_name']}: {server['tools_count']} tools")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("✅ MCP Database Enrichment Complete!")
    print("="*80)

def main():
    print("\n" + "="*80)
    print(" "*20 + "MCP DATABASE ENRICHMENT")
    print("="*80)

    # Phase 1: Enrich custom servers
    enrich_custom_servers()

    # Phase 2: Add use cases
    add_basic_use_cases()

    # Show summary
    show_summary()

if __name__ == "__main__":
    main()
