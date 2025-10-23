-- RSS News Database Schema
-- Based on CONTENT_SOURCES_ARCHITECTURE.md

-- External Sources Registry
CREATE TABLE IF NOT EXISTS external_sources (
  source_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  domain TEXT NOT NULL,
  category TEXT NOT NULL,
  source_type TEXT NOT NULL,
  priority TEXT NOT NULL,
  base_weight REAL DEFAULT 0.5,
  domain_authority INTEGER,
  update_frequency TEXT,
  extraction_method TEXT,
  api_endpoint TEXT,
  rss_url TEXT,
  rate_limit_per_day INTEGER,
  is_active BOOLEAN DEFAULT TRUE,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_fetched_at TIMESTAMP,
  total_articles_fetched INTEGER DEFAULT 0,
  metadata JSONB
);

-- External Content (Articles, Posts, News)
CREATE TABLE IF NOT EXISTS external_content (
  content_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT UNIQUE NOT NULL,
  author TEXT,
  author_id TEXT,
  published_at TIMESTAMP,
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  content_type TEXT,
  content_text TEXT,
  content_length INTEGER,

  -- Metadata
  tags JSONB,
  categories JSONB,

  -- Engagement metrics
  views INTEGER,
  upvotes INTEGER,
  comments_count INTEGER,
  shares INTEGER,

  -- Quality signals
  has_code_examples BOOLEAN DEFAULT FALSE,
  has_actionable_advice BOOLEAN DEFAULT FALSE,
  is_tutorial BOOLEAN DEFAULT FALSE,
  is_news BOOLEAN DEFAULT FALSE,
  is_opinion BOOLEAN DEFAULT FALSE,

  -- Scoring
  raw_score REAL,
  final_score REAL,
  relevance_score REAL,
  freshness_score REAL,

  -- Status
  is_processed BOOLEAN DEFAULT FALSE,
  is_indexed BOOLEAN DEFAULT FALSE,

  FOREIGN KEY (source_id) REFERENCES external_sources(source_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ext_content_source ON external_content(source_id);
CREATE INDEX IF NOT EXISTS idx_ext_content_published ON external_content(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_ext_content_score ON external_content(final_score DESC);
CREATE INDEX IF NOT EXISTS idx_ext_content_processed ON external_content(is_processed);
CREATE INDEX IF NOT EXISTS idx_ext_content_fetched ON external_content(fetched_at DESC);

-- Content Authors
CREATE TABLE IF NOT EXISTS content_authors (
  author_id TEXT PRIMARY KEY,
  author_name TEXT NOT NULL,
  author_url TEXT,
  domain TEXT,

  -- Popularity metrics
  total_articles INTEGER DEFAULT 0,
  avg_engagement REAL,
  follower_count INTEGER,

  -- Quality signals
  verified BOOLEAN DEFAULT FALSE,
  expert_in_topics JSONB,
  authority_score REAL,

  first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_active_at TIMESTAMP,

  metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_author_authority ON content_authors(authority_score DESC);

-- Content Insights (Extracted Intelligence)
CREATE TABLE IF NOT EXISTS content_insights (
  insight_id TEXT PRIMARY KEY,
  content_id TEXT NOT NULL,
  source_type TEXT NOT NULL,

  insight_type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  actionability_score REAL,
  confidence REAL,

  extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  tags JSONB,
  metadata JSONB,

  FOREIGN KEY (content_id) REFERENCES external_content(content_id)
);

CREATE INDEX IF NOT EXISTS idx_insights_type ON content_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_insights_actionability ON content_insights(actionability_score DESC);

-- Insert Tier 1 Sources
INSERT INTO external_sources (source_id, name, domain, category, source_type, priority, base_weight, extraction_method, rss_url, rate_limit_per_day, is_active)
VALUES
  ('techcrunch', 'TechCrunch AI', 'techcrunch.com', 'ai_news', 'rss_feed', 'high', 0.6, 'rss', 'https://techcrunch.com/category/artificial-intelligence/feed/', 20, TRUE),
  ('hubspot', 'HubSpot Blog', 'blog.hubspot.com', 'marketing', 'rss_feed', 'high', 0.7, 'rss', 'https://blog.hubspot.com/marketing/rss.xml', 15, TRUE),
  ('smallbiz', 'Small Business Trends', 'smallbiztrends.com', 'sme_news', 'rss_feed', 'medium', 0.5, 'rss', 'https://smallbiztrends.com/feed', 10, TRUE),
  ('socialmedia', 'Social Media Examiner', 'socialmediaexaminer.com', 'social_media', 'rss_feed', 'medium', 0.5, 'rss', 'https://www.socialmediaexaminer.com/feed/', 10, TRUE),
  ('neilpatel', 'Neil Patel Blog', 'neilpatel.com', 'digital_marketing', 'rss_feed', 'medium', 0.6, 'rss', 'https://neilpatel.com/feed/', 10, TRUE),
  ('sethgodin', 'Seth Godin''s Blog', 'seths.blog', 'marketing_philosophy', 'rss_feed', 'high', 0.7, 'rss', 'https://seths.blog/feed/', 5, TRUE),
  ('moz', 'Moz Blog', 'moz.com', 'seo', 'rss_feed', 'medium', 0.6, 'rss', 'https://moz.com/blog/feed', 10, TRUE)
ON CONFLICT (source_id) DO UPDATE SET
  name = EXCLUDED.name,
  rss_url = EXCLUDED.rss_url,
  rate_limit_per_day = EXCLUDED.rate_limit_per_day,
  is_active = EXCLUDED.is_active;
