#!/usr/bin/env python3
"""
Apply Fast Search Indexes to MCP Servers Database
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def apply_indexes():
    print("="*80)
    print(" "*20 + "CREATING FAST SEARCH INDEXES")
    print("="*80)

    conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
    cursor = conn.cursor()

    indexes = [
        {
            'name': 'Full-Text Search (Names & Descriptions)',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_servers_search ON mcp_servers
                USING GIN(to_tsvector('english',
                    COALESCE(server_name, '') || ' ' ||
                    COALESCE(description, '') || ' ' ||
                    COALESCE(display_name, '')
                ));
            """
        },
        {
            'name': 'Category & Downloads Index',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_servers_category_downloads
                ON mcp_servers(category, downloads_count DESC NULLS LAST);
            """
        },
        {
            'name': 'Source Type Index',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_servers_source
                ON mcp_servers(source_type);
            """
        },
        {
            'name': 'Keywords JSONB Index',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_servers_keywords
                ON mcp_servers USING GIN((server_metadata->'keywords'));
            """
        },
        {
            'name': 'Quality Score Index',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_servers_quality_score
                ON mcp_servers USING btree(
                    ((server_metadata->'score'->'detail'->>'quality')::numeric) DESC NULLS LAST
                );
            """
        },
        {
            'name': 'Maintenance Status Index',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_servers_maintained
                ON mcp_servers(is_actively_maintained)
                WHERE is_actively_maintained = TRUE;
            """
        },
        {
            'name': 'Last Updated Index',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_servers_last_updated
                ON mcp_servers(last_updated DESC NULLS LAST);
            """
        },
        {
            'name': 'Tools Count Index',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_servers_tools_count
                ON mcp_servers(tools_count DESC)
                WHERE tools_count > 0;
            """
        },
        {
            'name': 'Tool Search Index',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_tools_search
                ON mcp_server_tools USING GIN(to_tsvector('english',
                    COALESCE(tool_name, '') || ' ' ||
                    COALESCE(description, '')
                ));
            """
        },
        {
            'name': 'Tool Server Lookup Index',
            'sql': """
                CREATE INDEX IF NOT EXISTS idx_mcp_tools_server
                ON mcp_server_tools(server_id);
            """
        }
    ]

    created = 0
    skipped = 0

    for i, index in enumerate(indexes, 1):
        try:
            print(f"\n[{i}/{len(indexes)}] Creating: {index['name']}")
            cursor.execute(index['sql'])
            conn.commit()
            created += 1
            print(f"   ✅ Success")

        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ⏭️  Already exists")
                skipped += 1
            else:
                print(f"   ⚠️  Error: {e}")
            conn.rollback()

    # Show index statistics
    print(f"\n{'='*80}")
    print("📊 Index Statistics:")
    print(f"{'='*80}")

    cursor.execute("""
        SELECT
            indexname,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
          AND tablename = 'mcp_servers'
        ORDER BY pg_relation_size(indexrelid) DESC;
    """)

    print("\nMCP Servers Table Indexes:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")
    print(f"✅ Index Creation Complete!")
    print(f"   Created: {created}")
    print(f"   Already Existed: {skipped}")
    print(f"   Total: {created + skipped}/{len(indexes)}")
    print(f"{'='*80}")

if __name__ == "__main__":
    apply_indexes()
