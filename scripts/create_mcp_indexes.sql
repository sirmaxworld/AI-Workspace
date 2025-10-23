-- ============================================================================
-- FAST SEARCH INDEXES FOR MCP SERVERS DATABASE
-- Optimizes search performance for 4,113 MCP servers
-- ============================================================================

-- 1. Full-Text Search on Server Names and Descriptions
-- Enables fast text search across all server metadata
CREATE INDEX IF NOT EXISTS idx_mcp_servers_search ON mcp_servers
USING GIN(to_tsvector('english',
    COALESCE(server_name, '') || ' ' ||
    COALESCE(description, '') || ' ' ||
    COALESCE(display_name, '')
));

-- 2. Category and Popularity Combined Index
-- Optimizes category filtering with popularity sorting
CREATE INDEX IF NOT EXISTS idx_mcp_servers_category_downloads
ON mcp_servers(category, downloads_count DESC NULLS LAST);

-- 3. Source Type Index
-- Fast filtering by source (npm, custom, smithery, http)
CREATE INDEX IF NOT EXISTS idx_mcp_servers_source
ON mcp_servers(source_type);

-- 4. JSONB Keywords Index
-- Enables fast keyword search within server_metadata
CREATE INDEX IF NOT EXISTS idx_mcp_servers_keywords
ON mcp_servers USING GIN((server_metadata->'keywords'));

-- 5. JSONB Quality Score Index
-- Supports sorting by npm quality scores
CREATE INDEX IF NOT EXISTS idx_mcp_servers_quality_score
ON mcp_servers USING btree(
    ((server_metadata->'score'->'detail'->>'quality')::numeric) DESC NULLS LAST
);

-- 6. Maintenance Status Index
-- Fast filtering for actively maintained servers
CREATE INDEX IF NOT EXISTS idx_mcp_servers_maintained
ON mcp_servers(is_actively_maintained)
WHERE is_actively_maintained = TRUE;

-- 7. Last Updated Index
-- Enables sorting by freshness
CREATE INDEX IF NOT EXISTS idx_mcp_servers_last_updated
ON mcp_servers(last_updated DESC NULLS LAST);

-- 8. Tools Count Index
-- Fast filtering for servers with documented tools
CREATE INDEX IF NOT EXISTS idx_mcp_servers_tools_count
ON mcp_servers(tools_count DESC)
WHERE tools_count > 0;

-- ============================================================================
-- TOOL SEARCH INDEXES
-- ============================================================================

-- 9. Tool Name Full-Text Search
CREATE INDEX IF NOT EXISTS idx_mcp_tools_search
ON mcp_server_tools USING GIN(to_tsvector('english',
    COALESCE(tool_name, '') || ' ' ||
    COALESCE(description, '')
));

-- 10. Tool Server Lookup
CREATE INDEX IF NOT EXISTS idx_mcp_tools_server
ON mcp_server_tools(server_id);

-- ============================================================================
-- MATERIALIZED VIEW FOR FAST DISCOVERY
-- Pre-computed view for most common search queries
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_mcp_discovery AS
SELECT
    s.id,
    s.server_name,
    s.display_name,
    s.description,
    s.category,
    s.source_type,
    s.tools_count,
    s.downloads_count,
    s.last_updated,
    s.is_actively_maintained,
    (s.server_metadata->'score'->'detail'->>'quality')::numeric as quality_score,
    (s.server_metadata->'score'->'detail'->>'popularity')::numeric as popularity_score,
    (s.server_metadata->'keywords') as keywords,
    COALESCE(array_agg(DISTINCT t.tool_name) FILTER (WHERE t.tool_name IS NOT NULL), ARRAY[]::text[]) as tool_names
FROM mcp_servers s
LEFT JOIN mcp_server_tools t ON s.id = t.server_id
GROUP BY s.id, s.server_name, s.display_name, s.description, s.category,
         s.source_type, s.tools_count, s.downloads_count, s.last_updated,
         s.is_actively_maintained, s.server_metadata
ORDER BY s.downloads_count DESC NULLS LAST, quality_score DESC NULLS LAST;

-- Indexes on materialized view
CREATE INDEX IF NOT EXISTS idx_mv_mcp_discovery_category
ON mv_mcp_discovery(category);

CREATE INDEX IF NOT EXISTS idx_mv_mcp_discovery_search
ON mv_mcp_discovery USING GIN(to_tsvector('english',
    COALESCE(server_name, '') || ' ' ||
    COALESCE(description, '')
));

CREATE INDEX IF NOT EXISTS idx_mv_mcp_discovery_quality
ON mv_mcp_discovery(quality_score DESC NULLS LAST);

-- ============================================================================
-- REFRESH FUNCTION FOR MATERIALIZED VIEW
-- ============================================================================

CREATE OR REPLACE FUNCTION refresh_mcp_discovery()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_mcp_discovery;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STATISTICS AND VERIFICATION
-- ============================================================================

-- Show index sizes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND (tablename = 'mcp_servers' OR tablename = 'mcp_server_tools')
ORDER BY pg_relation_size(indexrelid) DESC;
