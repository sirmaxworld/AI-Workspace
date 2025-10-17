-- ============================================================
-- Railway PostgreSQL Schema with pgvector
-- Architecture: Permanent Videos + Rolling News + Mem0 Collections
-- ============================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- PART 1: PERMANENT VIDEO STORAGE (Never Delete)
-- ============================================================

-- Main videos table with embeddings
CREATE TABLE IF NOT EXISTS videos (
    video_id VARCHAR(20) PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,

    -- Channel info
    channel_name VARCHAR(255),
    channel_id VARCHAR(255),
    channel_url TEXT,

    -- Temporal metadata
    duration_seconds INTEGER,
    published_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Content classification
    content_type VARCHAR(50), -- tutorial, demonstration, theory, case_study, interview, review, news
    expertise_level VARCHAR(20), -- beginner, intermediate, advanced, expert
    primary_discipline VARCHAR(100),
    primary_domain VARCHAR(100),
    sub_domains TEXT[], -- array of sub-domains

    -- Temporal relevance
    is_current BOOLEAN DEFAULT TRUE,
    relevance_period VARCHAR(20), -- evergreen, short_term, medium_term, outdated
    superseded_by VARCHAR(20), -- video_id of newer content

    -- Quality metrics
    views INTEGER,
    likes INTEGER,
    engagement_rate FLOAT,
    production_quality VARCHAR(20), -- low, medium, high, professional

    -- Transcription metadata
    transcription_method VARCHAR(50), -- youtube_captions, whisper_api, whisper_local
    transcription_confidence FLOAT,
    transcription_language VARCHAR(10) DEFAULT 'en',

    -- Processing metadata
    processed_date TIMESTAMP,
    chunk_count INTEGER,
    embedding_model VARCHAR(100),
    llm_analyzer VARCHAR(100),

    -- Vector embeddings (OpenAI text-embedding-3-small = 1536 dimensions)
    title_embedding vector(1536),
    summary_embedding vector(1536),

    -- Metadata as JSONB for flexibility
    metadata JSONB,

    -- CRITICAL: Never allow deletion
    CONSTRAINT never_delete CHECK (true)
);

-- Full transcripts (separate table for performance)
CREATE TABLE IF NOT EXISTS video_transcripts (
    video_id VARCHAR(20) PRIMARY KEY REFERENCES videos(video_id),
    transcript_full TEXT NOT NULL,
    transcript_chunks JSONB, -- Array of chunked transcript with timestamps
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

-- Concepts taught in videos
CREATE TABLE IF NOT EXISTS video_concepts (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(20) REFERENCES videos(video_id),
    concept_name VARCHAR(255) NOT NULL,
    confidence FLOAT,
    timestamps_mentioned INTEGER[], -- seconds where mentioned
    definition_available BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

-- Prerequisites and enables (learning path)
CREATE TABLE IF NOT EXISTS video_learning_path (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(20) REFERENCES videos(video_id),
    prerequisite_concepts TEXT[], -- concepts needed before watching
    enables_concepts TEXT[], -- what this helps you learn next
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

-- Entities mentioned (people, tools, companies)
CREATE TABLE IF NOT EXISTS video_entities (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(20) REFERENCES videos(video_id),
    entity_type VARCHAR(20) NOT NULL, -- person, tool, company
    entity_name VARCHAR(255) NOT NULL,
    entity_id VARCHAR(255), -- External ID if available
    timestamps_mentioned INTEGER[],
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

-- Citations and references
CREATE TABLE IF NOT EXISTS video_citations (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(20) REFERENCES videos(video_id),
    citation_type VARCHAR(20) NOT NULL, -- video, paper, article
    citation_id VARCHAR(255), -- e.g., arXiv ID, video ID
    citation_title TEXT,
    citation_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

-- ============================================================
-- PART 2: ROLLING NEWS AGGREGATIONS (TTL-Based Deletion)
-- ============================================================

-- News aggregations with automatic expiration
CREATE TABLE IF NOT EXISTS news_aggregations (
    aggregation_id SERIAL PRIMARY KEY,

    -- Time window
    time_window_start TIMESTAMP NOT NULL,
    time_window_end TIMESTAMP NOT NULL,
    granularity VARCHAR(20) NOT NULL, -- hourly, daily, weekly, monthly

    -- Aggregated content
    summary JSONB NOT NULL, -- Aggregated summary with key topics
    trending_topics TEXT[],
    top_entities JSONB, -- {people: [...], companies: [...], tools: [...]}
    source_count INTEGER, -- How many sources in this aggregation

    -- Vector embedding for semantic search
    summary_embedding vector(1536),

    -- TTL (Time To Live)
    expires_at TIMESTAMP NOT NULL,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    source_type VARCHAR(50) -- e.g., "hackernews", "arxiv", "reddit"
);

-- News sources metadata
CREATE TABLE IF NOT EXISTS news_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_url TEXT,
    source_type VARCHAR(50), -- api, rss, scraper
    last_fetched TIMESTAMP,
    fetch_frequency_minutes INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- PART 3: CROSS-REFERENCE TABLES
-- ============================================================

-- Link videos to research papers
CREATE TABLE IF NOT EXISTS video_to_paper_links (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(20) REFERENCES videos(video_id),
    paper_id VARCHAR(255) NOT NULL, -- arXiv ID or DOI
    link_type VARCHAR(50), -- cites, explains, implements, reviews
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

-- Link videos to YC companies
CREATE TABLE IF NOT EXISTS video_to_company_links (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(20) REFERENCES videos(video_id),
    company_name VARCHAR(255) NOT NULL,
    yc_batch VARCHAR(20), -- e.g., "W21", "S22"
    link_type VARCHAR(50), -- mentions, features, case_study, founder_interview
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

-- ============================================================
-- PART 4: MEM0 PGVECTOR COLLECTIONS
-- ============================================================
-- Note: Mem0 will create these automatically when configured with pgvector
-- These are just for reference - Mem0 manages the schema

-- mem0_claude_memory (managed by Mem0)
-- mem0_yc_companies (managed by Mem0)
-- mem0_video_knowledge (managed by Mem0)
-- mem0_research_papers (managed by Mem0)

-- ============================================================
-- PART 5: INDEXES FOR PERFORMANCE
-- ============================================================

-- Video indexes
CREATE INDEX idx_videos_channel ON videos(channel_id);
CREATE INDEX idx_videos_published ON videos(published_date DESC);
CREATE INDEX idx_videos_domain ON videos(primary_domain);
CREATE INDEX idx_videos_content_type ON videos(content_type);
CREATE INDEX idx_videos_expertise ON videos(expertise_level);

-- Vector similarity indexes (HNSW = Hierarchical Navigable Small World)
CREATE INDEX idx_videos_title_embedding ON videos
    USING hnsw (title_embedding vector_cosine_ops);
CREATE INDEX idx_videos_summary_embedding ON videos
    USING hnsw (summary_embedding vector_cosine_ops);

-- News aggregation indexes
CREATE INDEX idx_news_expires ON news_aggregations(expires_at);
CREATE INDEX idx_news_window ON news_aggregations(time_window_start, granularity);
CREATE INDEX idx_news_summary_embedding ON news_aggregations
    USING hnsw (summary_embedding vector_cosine_ops);

-- Concept indexes
CREATE INDEX idx_concepts_video ON video_concepts(video_id);
CREATE INDEX idx_concepts_name ON video_concepts(concept_name);

-- Entity indexes
CREATE INDEX idx_entities_video ON video_entities(video_id);
CREATE INDEX idx_entities_type ON video_entities(entity_type);
CREATE INDEX idx_entities_name ON video_entities(entity_name);

-- Citation indexes
CREATE INDEX idx_citations_video ON video_citations(video_id);
CREATE INDEX idx_citations_type ON video_citations(citation_type);

-- Cross-reference indexes
CREATE INDEX idx_video_paper_links ON video_to_paper_links(video_id);
CREATE INDEX idx_video_company_links ON video_to_company_links(video_id);

-- ============================================================
-- PART 6: FUNCTIONS & TRIGGERS
-- ============================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-cleanup expired news aggregations
CREATE OR REPLACE FUNCTION cleanup_expired_news()
RETURNS void AS $$
BEGIN
    DELETE FROM news_aggregations WHERE expires_at < NOW();
    RAISE NOTICE 'Cleaned up expired news aggregations';
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- PART 7: RETENTION POLICIES
-- ============================================================

-- Insert default TTL values for news aggregations
-- (Actual cleanup scheduled via pg_cron or external scheduler)

COMMENT ON TABLE videos IS 'PERMANENT: Video metadata and embeddings - NEVER DELETE';
COMMENT ON TABLE video_transcripts IS 'PERMANENT: Full video transcripts - NEVER DELETE';
COMMENT ON TABLE news_aggregations IS 'ROLLING: News summaries with TTL - auto-expires based on expires_at';

COMMENT ON COLUMN news_aggregations.expires_at IS 'TTL: hourly=24h, daily=7d, weekly=3mo, monthly=6mo';

-- ============================================================
-- PART 8: INITIAL DATA & CONFIGURATION
-- ============================================================

-- Insert default news sources
INSERT INTO news_sources (source_name, source_url, source_type, fetch_frequency_minutes, is_active)
VALUES
    ('Hacker News', 'https://news.ycombinator.com', 'api', 60, true),
    ('arXiv CS.AI', 'https://arxiv.org/list/cs.AI/recent', 'api', 1440, true),
    ('Semantic Scholar', 'https://api.semanticscholar.org', 'api', 1440, true)
ON CONFLICT DO NOTHING;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Verify pgvector is installed
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Check tables created
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Check indexes created
SELECT indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY indexname;

COMMENT ON SCHEMA public IS 'Railway PostgreSQL with pgvector - Permanent Videos + Rolling News + Mem0 Collections';

-- ============================================================
-- END OF SCHEMA
-- ============================================================

SELECT 'Schema created successfully! 🎉' AS status;
