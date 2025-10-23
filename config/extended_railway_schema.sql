-- ============================================================================
-- EXTENDED RAILWAY POSTGRESQL SCHEMA
-- Database Improvement Phase: GitHub Intelligence, OSS Repos, MCP Servers
-- ============================================================================

-- ============================================================================
-- PHASE 1: GITHUB CODING INTELLIGENCE
-- Purpose: Extract coding patterns, styles, and best practices from popular repos
-- ============================================================================

-- Popular GitHub Repositories
CREATE TABLE IF NOT EXISTS github_repositories (
    id SERIAL PRIMARY KEY,
    repo_full_name VARCHAR(255) UNIQUE NOT NULL,  -- e.g., "facebook/react"
    owner VARCHAR(255) NOT NULL,
    repo_name VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(100),

    -- Metrics
    stars INTEGER,
    forks INTEGER,
    watchers INTEGER,
    open_issues INTEGER,

    -- Activity
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    pushed_at TIMESTAMP,

    -- URLs
    clone_url TEXT,
    homepage TEXT,

    -- Metadata
    topics TEXT[],  -- Array of topic tags
    license VARCHAR(100),
    has_wiki BOOLEAN DEFAULT FALSE,
    has_pages BOOLEAN DEFAULT FALSE,

    -- Enrichment status
    enriched BOOLEAN DEFAULT FALSE,
    enriched_at TIMESTAMP,

    -- Full data
    repo_data JSONB,

    -- Timestamps
    created_at_db TIMESTAMP DEFAULT NOW(),
    updated_at_db TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

CREATE INDEX IF NOT EXISTS idx_github_repos_name ON github_repositories(repo_full_name);
CREATE INDEX IF NOT EXISTS idx_github_repos_language ON github_repositories(language);
CREATE INDEX IF NOT EXISTS idx_github_repos_stars ON github_repositories(stars DESC);

-- Coding Patterns Extracted from Repos
CREATE TABLE IF NOT EXISTS coding_patterns (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER REFERENCES github_repositories(id),

    -- Pattern identification
    pattern_type VARCHAR(100) NOT NULL,  -- e.g., "error-handling", "state-management", "api-design"
    pattern_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Code examples
    code_example TEXT,
    file_path VARCHAR(500),
    line_start INTEGER,
    line_end INTEGER,

    -- Context
    language VARCHAR(100),
    framework VARCHAR(100),

    -- Quality metrics
    complexity_score INTEGER,  -- 1-100
    readability_score INTEGER,  -- 1-100
    reusability_score INTEGER,  -- 1-100

    -- Usage
    usage_frequency VARCHAR(50),  -- "very-common", "common", "occasional", "rare"

    -- AI analysis
    ai_analysis JSONB,  -- Gemini Flash analysis of pattern

    -- Metadata
    extracted_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

CREATE INDEX IF NOT EXISTS idx_coding_patterns_type ON coding_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_coding_patterns_repo ON coding_patterns(repo_id);
CREATE INDEX IF NOT EXISTS idx_coding_patterns_lang ON coding_patterns(language);

-- Coding Rules/Best Practices
CREATE TABLE IF NOT EXISTS coding_rules (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER REFERENCES github_repositories(id),

    -- Rule identification
    rule_category VARCHAR(100) NOT NULL,  -- "naming", "structure", "testing", "docs", "security"
    rule_title VARCHAR(255) NOT NULL,
    rule_description TEXT,

    -- Examples
    good_example TEXT,
    bad_example TEXT,

    -- Context
    applies_to_languages TEXT[],
    applies_to_frameworks TEXT[],

    -- Validation
    enforced_by_linter BOOLEAN DEFAULT FALSE,
    linter_rule_name VARCHAR(255),

    -- Impact
    impact_level VARCHAR(50),  -- "critical", "high", "medium", "low"

    -- Source
    extracted_from VARCHAR(100),  -- "CONTRIBUTING.md", "style-guide", "linter-config", "code-review"
    confidence_score INTEGER,  -- 1-100

    -- Full data
    rule_data JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

CREATE INDEX IF NOT EXISTS idx_coding_rules_category ON coding_rules(rule_category);
CREATE INDEX IF NOT EXISTS idx_coding_rules_impact ON coding_rules(impact_level);

-- Coding Methods/Functions Database
CREATE TABLE IF NOT EXISTS coding_methods (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER REFERENCES github_repositories(id),

    -- Method identification
    method_name VARCHAR(255) NOT NULL,
    method_signature TEXT,
    method_purpose TEXT,

    -- Implementation
    implementation_code TEXT,
    file_path VARCHAR(500),

    -- Context
    language VARCHAR(100),
    class_name VARCHAR(255),
    module_name VARCHAR(255),

    -- Metrics
    lines_of_code INTEGER,
    cyclomatic_complexity INTEGER,
    parameters_count INTEGER,

    -- Quality
    has_tests BOOLEAN DEFAULT FALSE,
    has_documentation BOOLEAN DEFAULT FALSE,
    test_coverage_percent INTEGER,

    -- Usage patterns
    usage_examples TEXT[],
    common_use_cases TEXT[],

    -- AI analysis
    ai_summary TEXT,
    ai_recommendations TEXT,

    -- Metadata
    extracted_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

CREATE INDEX IF NOT EXISTS idx_coding_methods_name ON coding_methods(method_name);
CREATE INDEX IF NOT EXISTS idx_coding_methods_lang ON coding_methods(language);
CREATE INDEX IF NOT EXISTS idx_coding_methods_repo ON coding_methods(repo_id);


-- ============================================================================
-- PHASE 2: COMMERCIAL-FRIENDLY OPEN SOURCE DATABASE
-- Purpose: Curated list of OSS repos with commercial-friendly licenses
-- ============================================================================

CREATE TABLE IF NOT EXISTS oss_commercial_repos (
    id SERIAL PRIMARY KEY,

    -- Repository info
    repo_full_name VARCHAR(255) UNIQUE NOT NULL,
    owner VARCHAR(255) NOT NULL,
    repo_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Language & Tech
    primary_language VARCHAR(100),
    languages JSONB,  -- All languages with percentages
    frameworks TEXT[],
    tech_stack TEXT[],

    -- License (critical for commercial use)
    license_type VARCHAR(100) NOT NULL,  -- "MIT", "Apache-2.0", "BSD-3-Clause", etc.
    license_file TEXT,
    is_commercial_friendly BOOLEAN DEFAULT TRUE,
    license_restrictions TEXT,

    -- Popularity & Quality
    stars INTEGER,
    forks INTEGER,
    watchers INTEGER,
    contributors_count INTEGER,

    -- Activity & Maintenance
    last_commit_date TIMESTAMP,
    commit_frequency VARCHAR(50),  -- "very-active", "active", "moderate", "slow", "inactive"
    is_actively_maintained BOOLEAN DEFAULT TRUE,
    maintainer_response_time VARCHAR(50),

    -- Documentation Quality
    has_readme BOOLEAN DEFAULT TRUE,
    has_wiki BOOLEAN DEFAULT FALSE,
    has_docs_site BOOLEAN DEFAULT FALSE,
    docs_url TEXT,
    docs_quality_score INTEGER,  -- 1-100

    -- Commercial Use Cases
    commercial_use_cases TEXT[],
    notable_companies_using TEXT[],  -- Companies using this in production

    -- Integration & Deployment
    package_managers TEXT[],  -- "npm", "pip", "maven", etc.
    installation_difficulty VARCHAR(50),  -- "easy", "moderate", "complex"
    deployment_complexity VARCHAR(50),

    -- Dependencies
    dependencies_count INTEGER,
    security_vulnerabilities INTEGER,
    last_security_audit TIMESTAMP,

    -- AI Analysis
    ai_commercial_suitability JSONB,  -- Gemini analysis for commercial use
    ai_integration_guide JSONB,
    ai_risk_assessment JSONB,

    -- URLs
    repo_url TEXT,
    homepage TEXT,
    docs_url_main TEXT,

    -- Metadata
    added_at TIMESTAMP DEFAULT NOW(),
    enriched_at TIMESTAMP,
    verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(255),

    -- Full data
    repo_metadata JSONB,

    CONSTRAINT never_delete CHECK (true)
);

CREATE INDEX IF NOT EXISTS idx_oss_repos_license ON oss_commercial_repos(license_type);
CREATE INDEX IF NOT EXISTS idx_oss_repos_language ON oss_commercial_repos(primary_language);
CREATE INDEX IF NOT EXISTS idx_oss_repos_stars ON oss_commercial_repos(stars DESC);
CREATE INDEX IF NOT EXISTS idx_oss_repos_maintained ON oss_commercial_repos(is_actively_maintained);

-- OSS Repository Categories/Tags
CREATE TABLE IF NOT EXISTS oss_repo_categories (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER REFERENCES oss_commercial_repos(id),

    category VARCHAR(100) NOT NULL,  -- "database", "ml-framework", "ui-library", etc.
    subcategory VARCHAR(100),

    relevance_score INTEGER,  -- How well it fits this category (1-100)

    CONSTRAINT never_delete CHECK (true)
);

CREATE INDEX IF NOT EXISTS idx_oss_categories_cat ON oss_repo_categories(category);
CREATE INDEX IF NOT EXISTS idx_oss_categories_repo ON oss_repo_categories(repo_id);


-- ============================================================================
-- PHASE 3: MCP SERVER INTELLIGENCE DATABASE
-- Purpose: Catalog MCP servers, their tools, use cases, and integration patterns
-- ============================================================================

CREATE TABLE IF NOT EXISTS mcp_servers (
    id SERIAL PRIMARY KEY,

    -- Server identification
    server_name VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    description TEXT,

    -- Source & Installation
    source_type VARCHAR(50) NOT NULL,  -- "npm", "github", "pip", "smithery", "custom"
    source_url TEXT,
    package_name VARCHAR(255),
    install_command TEXT,

    -- Configuration
    config_type VARCHAR(50),  -- "stdio", "http", "sse"
    config_template JSONB,  -- Example configuration
    required_env_vars TEXT[],
    optional_env_vars TEXT[],

    -- Capabilities
    has_tools BOOLEAN DEFAULT FALSE,
    has_resources BOOLEAN DEFAULT FALSE,
    has_prompts BOOLEAN DEFAULT FALSE,

    tools_count INTEGER DEFAULT 0,
    resources_count INTEGER DEFAULT 0,
    prompts_count INTEGER DEFAULT 0,

    -- Categories
    category VARCHAR(100),  -- "database", "search", "automation", "ai", "web", etc.
    subcategories TEXT[],

    -- Quality & Maintenance
    author VARCHAR(255),
    maintainers TEXT[],
    stars INTEGER,
    downloads_count INTEGER,
    last_updated TIMESTAMP,
    is_actively_maintained BOOLEAN DEFAULT TRUE,

    -- Documentation
    documentation_url TEXT,
    docs_quality_score INTEGER,  -- 1-100
    has_examples BOOLEAN DEFAULT FALSE,

    -- Compatibility
    supported_platforms TEXT[],  -- "macos", "linux", "windows"
    min_mcp_version VARCHAR(50),

    -- AI Analysis
    ai_use_case_analysis JSONB,  -- Gemini analysis of use cases
    ai_integration_tips JSONB,

    -- Metadata
    added_at TIMESTAMP DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE,

    -- Full data
    server_metadata JSONB,

    CONSTRAINT never_delete CHECK (true)
);

CREATE INDEX IF NOT EXISTS idx_mcp_servers_name ON mcp_servers(server_name);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_category ON mcp_servers(category);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_source ON mcp_servers(source_type);

-- MCP Server Tools
CREATE TABLE IF NOT EXISTS mcp_server_tools (
    id SERIAL PRIMARY KEY,
    server_id INTEGER REFERENCES mcp_servers(id),

    -- Tool identification
    tool_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    description TEXT,

    -- Parameters
    parameters_schema JSONB,  -- JSON schema for parameters
    required_params TEXT[],
    optional_params TEXT[],

    -- Behavior
    is_async BOOLEAN DEFAULT FALSE,
    estimated_execution_time VARCHAR(50),  -- "instant", "fast", "moderate", "slow"

    -- Use cases
    primary_use_case TEXT,
    example_use_cases TEXT[],
    code_examples JSONB,  -- Example invocations

    -- Integration patterns
    common_workflows TEXT[],  -- Common patterns using this tool
    pairs_well_with TEXT[],  -- Other tools commonly used with this

    -- AI Analysis
    ai_usage_tips TEXT,
    ai_best_practices TEXT[],

    -- Metadata
    added_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

CREATE INDEX IF NOT EXISTS idx_mcp_tools_server ON mcp_server_tools(server_id);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_name ON mcp_server_tools(tool_name);

-- MCP Server Use Cases (Real-world usage patterns)
CREATE TABLE IF NOT EXISTS mcp_use_cases (
    id SERIAL PRIMARY KEY,
    server_id INTEGER REFERENCES mcp_servers(id),

    -- Use case identification
    use_case_title VARCHAR(255) NOT NULL,
    use_case_description TEXT,

    -- Context
    industry VARCHAR(100),  -- "development", "research", "business", "creative"
    difficulty_level VARCHAR(50),  -- "beginner", "intermediate", "advanced"

    -- Implementation
    setup_steps TEXT[],
    example_prompts TEXT[],
    expected_outcomes TEXT[],

    -- Tools involved
    tools_used TEXT[],  -- Which MCP tools are used

    -- Value
    time_saved VARCHAR(100),
    productivity_impact VARCHAR(50),  -- "high", "medium", "low"

    -- Source
    source VARCHAR(100),  -- "documentation", "community", "smithery", "ai-generated"
    verified BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT never_delete CHECK (true)
);

CREATE INDEX IF NOT EXISTS idx_mcp_use_cases_server ON mcp_use_cases(server_id);
CREATE INDEX IF NOT EXISTS idx_mcp_use_cases_industry ON mcp_use_cases(industry);


-- ============================================================================
-- CROSS-REFERENCE TABLES (Link different intelligence sources)
-- ============================================================================

-- Link YC Companies to GitHub Repos
CREATE TABLE IF NOT EXISTS yc_to_github_links (
    id SERIAL PRIMARY KEY,
    yc_company_id INTEGER REFERENCES yc_companies_enriched(id),
    github_repo_id INTEGER REFERENCES github_repositories(id),

    relationship_type VARCHAR(50),  -- "official", "fork", "demo", "community"
    confidence_score INTEGER,  -- 1-100

    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,

    CONSTRAINT never_delete CHECK (true)
);

-- Link OSS Repos to MCP Servers (e.g., MCP server wrapping an OSS tool)
CREATE TABLE IF NOT EXISTS oss_to_mcp_links (
    id SERIAL PRIMARY KEY,
    oss_repo_id INTEGER REFERENCES oss_commercial_repos(id),
    mcp_server_id INTEGER REFERENCES mcp_servers(id),

    integration_type VARCHAR(50),  -- "wrapper", "connector", "extension", "inspiration"

    CONSTRAINT never_delete CHECK (true)
);

-- ============================================================================
-- UTILITY FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at_db = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with updated_at_db column
CREATE TRIGGER update_github_repos_updated_at
    BEFORE UPDATE ON github_repositories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Top Commercial OSS Repos by Category
CREATE OR REPLACE VIEW v_top_oss_by_category AS
SELECT
    c.category,
    r.repo_full_name,
    r.license_type,
    r.stars,
    r.is_actively_maintained,
    r.last_commit_date
FROM oss_commercial_repos r
JOIN oss_repo_categories c ON r.id = c.repo_id
WHERE r.is_commercial_friendly = TRUE
ORDER BY c.category, r.stars DESC;

-- View: MCP Servers by Category with Tool Counts
CREATE OR REPLACE VIEW v_mcp_servers_summary AS
SELECT
    s.server_name,
    s.category,
    s.tools_count,
    s.resources_count,
    s.is_actively_maintained,
    COUNT(DISTINCT u.id) as use_case_count
FROM mcp_servers s
LEFT JOIN mcp_use_cases u ON s.id = u.server_id
GROUP BY s.id, s.server_name, s.category, s.tools_count, s.resources_count, s.is_actively_maintained
ORDER BY s.tools_count DESC, s.server_name;

-- View: GitHub Repos with Most Coding Patterns Extracted
CREATE OR REPLACE VIEW v_repos_pattern_richness AS
SELECT
    r.repo_full_name,
    r.language,
    r.stars,
    COUNT(DISTINCT p.id) as pattern_count,
    COUNT(DISTINCT cr.id) as rule_count,
    COUNT(DISTINCT cm.id) as method_count
FROM github_repositories r
LEFT JOIN coding_patterns p ON r.id = p.repo_id
LEFT JOIN coding_rules cr ON r.id = cr.repo_id
LEFT JOIN coding_methods cm ON r.id = cm.repo_id
WHERE r.enriched = TRUE
GROUP BY r.id, r.repo_full_name, r.language, r.stars
ORDER BY pattern_count DESC, rule_count DESC;

-- ============================================================================
-- END OF EXTENDED RAILWAY POSTGRESQL SCHEMA
-- ============================================================================
