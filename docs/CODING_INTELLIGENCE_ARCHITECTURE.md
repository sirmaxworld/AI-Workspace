# Coding Intelligence System Architecture

**Version:** 1.0
**Date:** 2025-10-17
**Status:** Design Phase

## Executive Summary

Transform our collected GitHub intelligence (1,600 repos, 626 rules, 150 patterns, 451 OSS repos) into an **active coding assistant** that proactively improves code quality, suggests best practices, and recommends commercial-friendly libraries through semantic search and MCP integration.

---

## 🎯 Goals

### Primary Objectives
1. **Context-Aware Assistance** - Proactively suggest patterns/rules based on what you're coding
2. **Instant Access** - Sub-100ms semantic search across all intelligence
3. **Seamless Integration** - Works with Claude Code, CrewAI, Cursor, VSCode via MCP
4. **Zero Friction** - Auto-triggers, no manual lookups needed

### Success Metrics
- **Query Speed:** <100ms for semantic search
- **Relevance:** >90% of suggestions are applicable
- **Adoption:** Used in >50% of coding sessions within 1 month
- **Impact:** Measurable reduction in errors and improved code quality

---

## 🏗️ System Architecture

### Layer 1: Intelligence Data Sources

**Current Assets:**
```
├── GitHub Repositories: 1,600 repos
│   ├── Patterns: 150 (testing, build, project structure)
│   ├── Rules: 626 (best practices, anti-patterns, guidelines)
│   ├── Methods: TBD (function-level intelligence)
│   └── Metadata: Stars, languages, frameworks
│
├── OSS Commercial Database: 451 repos
│   ├── Commercial Scores: 0-100 viability
│   ├── License Info: MIT, Apache, BSD compatibility
│   ├── Maintenance: Activity classification
│   └── Use Cases: Real-world applications
│
└── MCP Servers: 4,113 servers
    ├── Tools: 0+ documented
    ├── Categories: 14 types
    └── Descriptions: 99.9% coverage
```

**Storage:** Railway PostgreSQL
**Schema:** Extended schema with coding_patterns, coding_rules, oss_commercial_repos, mcp_servers

---

### Layer 2: Vector Embedding & Search

**Technology:** PostgreSQL + pgvector extension

**Why pgvector?**
- ✅ Keep everything in Railway PostgreSQL (no new services)
- ✅ ACID transactions for consistency
- ✅ Sub-100ms queries with HNSW indexes
- ✅ Hybrid search (vector + full-text + filters)
- ✅ Scale to millions of vectors

**Embedding Strategy:**

```sql
-- Add pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Embed coding patterns
ALTER TABLE coding_patterns
ADD COLUMN embedding vector(1536);  -- OpenAI text-embedding-3-small

-- Embed coding rules
ALTER TABLE coding_rules
ADD COLUMN embedding vector(1536);

-- Embed OSS repos
ALTER TABLE oss_commercial_repos
ADD COLUMN embedding vector(1536);

-- Embed MCP servers
ALTER TABLE mcp_servers
ADD COLUMN embedding vector(1536);

-- Create HNSW indexes for fast similarity search
CREATE INDEX ON coding_patterns
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX ON coding_rules
USING hnsw (embedding vector_cosine_ops);
```

**Embedding Model:** OpenAI `text-embedding-3-small`
- Dimension: 1536
- Cost: $0.02 / 1M tokens
- Speed: ~1000 embeddings/second
- Quality: State-of-the-art semantic understanding

**Total Embedding Cost:**
```
Patterns: 150 × ~500 tokens × $0.00002 = $0.0015
Rules: 626 × ~300 tokens × $0.00002 = $0.0037
OSS: 451 × ~400 tokens × $0.00002 = $0.0036
MCP: 4,113 × ~200 tokens × $0.00002 = $0.0164
────────────────────────────────────────────
Total: ~$0.03 (one-time cost)
```

**Search Performance:**
- Vector similarity: <50ms (HNSW index)
- Hybrid search: <100ms (vector + filters)
- Concurrent queries: 100+ QPS

---

### Layer 3: Coding Intelligence MCP Server

**Location:** `/Users/yourox/AI-Workspace/mcp-servers/coding-intelligence/`

**Server Name:** `coding-intelligence`

**Core Tools (8):**

#### 1. `search_coding_patterns`
Search for coding patterns by semantic query

```typescript
{
  query: string;           // "How to structure Jest tests"
  language?: string;       // "JavaScript", "Python", etc.
  pattern_type?: string;   // "testing", "build", "error-handling"
  limit?: number;          // Default: 10
}
```

**Returns:** Top N patterns with similarity scores, source repos, code examples

#### 2. `get_best_practices`
Get best practices for a specific language/framework

```typescript
{
  language: string;        // "Python", "TypeScript"
  task_type?: string;      // "testing", "api-design", "error-handling"
  framework?: string;      // "React", "FastAPI", "Express"
  limit?: number;
}
```

**Returns:** Curated rules from top repos, confidence scores, examples

#### 3. `check_code_against_rules`
Analyze code snippet against extracted rules

```typescript
{
  code: string;            // Code to analyze
  language: string;        // Language of the code
  check_types?: string[];  // ["anti-pattern", "security", "best-practice"]
}
```

**Returns:** Violations, suggestions, rule references, severity

#### 4. `find_error_solutions`
Search for similar errors and their solutions

```typescript
{
  error_message: string;   // Error text or stack trace
  language?: string;       // Context language
  framework?: string;      // Context framework
  limit?: number;
}
```

**Returns:** Similar errors from 1,600 repos, how they were resolved

#### 5. `recommend_oss_library`
Recommend commercial-friendly OSS libraries

```typescript
{
  requirements: string;    // "Need a date library for JavaScript"
  commercial_only?: boolean; // Default: true
  min_stars?: number;      // Minimum star count
  licenses?: string[];     // ["MIT", "Apache-2.0", "BSD-3-Clause"]
  limit?: number;
}
```

**Returns:** Top libraries with commercial scores, maintenance status, use cases

#### 6. `analyze_code_quality`
Comprehensive code quality analysis

```typescript
{
  code: string;
  language: string;
  context?: string;        // "This is a REST API endpoint"
  check_patterns?: boolean;
  check_rules?: boolean;
  check_complexity?: boolean;
}
```

**Returns:** Quality score, pattern matches, rule violations, suggestions

#### 7. `get_similar_implementations`
Find similar code implementations from top repos

```typescript
{
  description: string;     // "Error handling middleware for Express"
  language: string;
  framework?: string;
  limit?: number;
}
```

**Returns:** Similar implementations from 1,600 repos, stars, patterns used

#### 8. `suggest_improvements`
AI-powered code improvement suggestions

```typescript
{
  code: string;
  language: string;
  goals?: string[];        // ["performance", "readability", "security"]
  context?: string;
}
```

**Returns:** Specific improvements with before/after examples, rationale

---

### Layer 4: Smart Trigger System

**Automatic Context Detection:**

```python
class SmartTriggers:
    """Auto-trigger intelligence lookups based on coding context"""

    def on_file_created(file_path: str, language: str):
        """New file → Suggest project structure patterns"""
        patterns = mcp.search_coding_patterns(
            query=f"project structure for {language}",
            language=language,
            pattern_type="project-structure"
        )
        return suggest_to_user(patterns)

    def on_error_detected(error: str, context: dict):
        """Error in terminal → Search for solutions"""
        solutions = mcp.find_error_solutions(
            error_message=error,
            language=context.get('language'),
            framework=context.get('framework')
        )
        return suggest_to_user(solutions)

    def on_import_added(package: str, language: str):
        """New import → Check OSS commercial viability"""
        recommendations = mcp.recommend_oss_library(
            requirements=f"evaluate {package}",
            commercial_only=True
        )
        return suggest_to_user(recommendations)

    def on_function_written(code: str, language: str):
        """Function completed → Check against rules"""
        analysis = mcp.check_code_against_rules(
            code=code,
            language=language,
            check_types=["anti-pattern", "best-practice"]
        )
        if analysis.has_violations():
            return suggest_to_user(analysis)

    def on_pre_commit():
        """Pre-commit hook → Quality check all changes"""
        changed_files = git.get_changed_files()
        for file in changed_files:
            code = file.read()
            quality = mcp.analyze_code_quality(
                code=code,
                language=detect_language(file),
                check_patterns=True,
                check_rules=True
            )
            if quality.score < 80:
                return block_commit(quality.issues)
```

**Integration Points:**
- **Coding Brain MCP** - Hook into terminal output capture
- **File Watcher** - Monitor workspace for new files/changes
- **Git Hooks** - Pre-commit quality checks
- **LSP Integration** - Real-time suggestions in editor

---

### Layer 5: Consumer Applications

#### A. Claude Code (Terminal)
**Current:** You (me) via MCP protocol
**Enhancement:** Add `coding-intelligence` to MCP config

```json
{
  "mcpServers": {
    "coding-intelligence": {
      "command": "python3",
      "args": [
        "/Users/yourox/AI-Workspace/mcp-servers/coding-intelligence/server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "RAILWAY_DATABASE_URL": "${RAILWAY_DATABASE_URL}"
      }
    }
  }
}
```

**Usage:** I can now call intelligence tools directly during our conversations

#### B. CrewAI Agents
**Specialized Agents:**

```python
from crewai import Agent, Task, Crew

# Code Review Agent
code_reviewer = Agent(
    role="Senior Code Reviewer",
    goal="Review code for quality, patterns, and best practices",
    tools=[
        mcp.check_code_against_rules,
        mcp.analyze_code_quality,
        mcp.suggest_improvements
    ],
    backstory="Expert reviewer trained on 1,600 top GitHub repos"
)

# Architecture Agent
architect = Agent(
    role="Software Architect",
    goal="Design optimal system architecture using proven patterns",
    tools=[
        mcp.search_coding_patterns,
        mcp.get_similar_implementations,
        mcp.recommend_oss_library
    ],
    backstory="Architect with knowledge of patterns from elite repos"
)

# Library Selection Agent
librarian = Agent(
    role="Technology Evaluator",
    goal="Recommend commercial-friendly OSS libraries",
    tools=[
        mcp.recommend_oss_library
    ],
    backstory="Expert at evaluating OSS for commercial use"
)

# Security Agent
security_expert = Agent(
    role="Security Specialist",
    goal="Identify security issues and suggest fixes",
    tools=[
        mcp.check_code_against_rules,
        mcp.get_best_practices
    ],
    backstory="Security expert trained on security rules from 1,600 repos"
)

# Create crew
crew = Crew(
    agents=[code_reviewer, architect, librarian, security_expert],
    tasks=[review_task, architecture_task, library_task, security_task]
)
```

#### C. Cursor / VSCode Extension
**Via MCP Protocol** - Works natively with Cursor

```typescript
// Extension auto-suggests as you code
editor.onDidChangeTextDocument(async (event) => {
  const language = detectLanguage(event.document);
  const code = event.document.getText();

  // Real-time pattern matching
  const patterns = await mcp.search_coding_patterns({
    query: extractContext(code),
    language: language,
    limit: 3
  });

  // Show inline suggestions
  showInlineSuggestions(patterns);
});
```

#### D. API Webhooks
**REST API for CI/CD Integration:**

```bash
# Pre-commit quality check
curl -X POST https://api.coding-intelligence.ai/check \
  -H "Content-Type: application/json" \
  -d '{
    "code": "...",
    "language": "python",
    "min_quality_score": 80
  }'

# Library recommendation
curl -X POST https://api.coding-intelligence.ai/recommend \
  -d '{
    "requirements": "Need OAuth2 library for Python",
    "commercial_only": true
  }'
```

---

## 📊 Data Flow Examples

### Example 1: Writing a New Python Function

```
1. User writes: def process_user_data(data):
2. Smart Trigger detects: New function in Python
3. MCP Tool Called: get_best_practices(language="Python", task_type="data-processing")
4. Vector Search: Finds relevant patterns from scikit-learn, pandas, FastAPI
5. Response: "Consider using type hints (PEP 484), add docstring, validate input"
6. User sees: Inline suggestions in editor / Claude Code response
```

### Example 2: Error in Terminal

```
1. Coding Brain captures: ModuleNotFoundError: No module named 'requests'
2. Smart Trigger detects: Python import error
3. MCP Tool Called: find_error_solutions(error_message="...", language="Python")
4. Vector Search: Finds 50 similar errors from 1,600 repos
5. Response: "Install with: pip install requests. Used in 847/1,600 repos."
6. Also suggests: Alternative libraries (httpx, aiohttp) with commercial scores
```

### Example 3: Choosing a Library

```
1. User asks: "Need a date library for JavaScript"
2. Claude Code calls: recommend_oss_library(requirements="...", commercial_only=True)
3. Hybrid Search: Vector similarity + commercial score filter + star count
4. Response ranked by:
   - Commercial viability: 94/100 (dayjs), 89/100 (date-fns)
   - Maintenance: Very active
   - License: MIT
   - Stars: 48K, 34K
5. Recommendation: "Use dayjs - MIT license, actively maintained, 48K stars"
```

---

## 🛠️ Implementation Roadmap

### Phase 1: Vector Foundation (Week 1)
**Goal:** Enable semantic search

- [ ] Add pgvector extension to Railway PostgreSQL
- [ ] Write embedding generation script
- [ ] Embed all 150 patterns, 626 rules, 451 OSS repos, 4113 MCP servers
- [ ] Create HNSW indexes
- [ ] Benchmark query performance (<100ms target)
- [ ] Build basic search API

**Deliverables:**
- `scripts/generate_embeddings.py`
- `scripts/test_vector_search.py`
- SQL migration for vector columns + indexes

### Phase 2: MCP Server (Week 2)
**Goal:** Build coding intelligence MCP

- [ ] Create mcp-servers/coding-intelligence/ directory
- [ ] Implement 8 core tools
- [ ] Add caching layer (Redis or in-memory)
- [ ] Write comprehensive tests
- [ ] Add to MCP config for Claude Code
- [ ] Documentation & examples

**Deliverables:**
- `mcp-servers/coding-intelligence/server.py`
- `mcp-servers/coding-intelligence/README.md`
- `mcp-servers/coding-intelligence/tests/`

### Phase 3: Smart Triggers (Week 3)
**Goal:** Proactive assistance

- [ ] Integrate with Coding Brain MCP
- [ ] Add file system watcher
- [ ] Implement trigger logic for 5 events
- [ ] Add configurable sensitivity settings
- [ ] User preference system (opt-in/out per trigger)

**Deliverables:**
- `scripts/smart_triggers.py`
- `.claude-code/triggers.json` config file

### Phase 4: CrewAI Integration (Week 4)
**Goal:** AI agent access

- [ ] Create 4 specialized agents
- [ ] Define agent tasks & workflows
- [ ] Build example crews for common scenarios
- [ ] Performance optimization
- [ ] Documentation

**Deliverables:**
- `crews/code_review_crew.py`
- `crews/architecture_crew.py`
- `crews/library_selection_crew.py`
- `crews/security_review_crew.py`

### Phase 5: Polish & Scale (Week 5+)
**Goal:** Production ready

- [ ] Performance optimization (<100ms all queries)
- [ ] API rate limiting
- [ ] Usage analytics
- [ ] A/B testing framework
- [ ] User feedback collection
- [ ] Continuous embedding updates

---

## 📈 Expected Impact

### Quantitative Benefits
| Metric | Baseline | Target | Method |
|--------|----------|--------|--------|
| Code Review Time | 30 min | 15 min | Automated suggestions |
| Error Resolution | 15 min | 5 min | Similar error search |
| Library Selection | 2 hours | 10 min | OSS recommendations |
| Pattern Discovery | Manual | Instant | Semantic search |
| Code Quality Score | N/A | >80/100 | Automated checks |

### Qualitative Benefits
- **Confidence:** Know you're using commercial-friendly libraries
- **Speed:** Instant access to 1,600 repos of best practices
- **Learning:** Discover patterns from elite repositories
- **Consistency:** Standardized coding practices across projects
- **Security:** Automated security rule checking

---

## 🔒 Security & Privacy

### Data Protection
- All data stored in Railway PostgreSQL (encrypted at rest)
- No code leaves your workspace
- Embeddings don't contain raw code
- API keys managed via environment variables

### Access Control
- MCP tools run locally (no external API calls except OpenAI for embeddings)
- Optional cloud deployment behind authentication
- Audit logging for sensitive operations

---

## 💰 Cost Analysis

### One-Time Costs
```
Embedding Generation:     $0.03
Development Time:         5 weeks
Testing & QA:            1 week
Documentation:           0.5 week
───────────────────────────────
Total:                   ~6.5 weeks + $0.03
```

### Ongoing Costs
```
Railway PostgreSQL:       $20/month (current plan)
Embedding Updates:        $0.01/month (incremental)
API Hosting (optional):   $0-50/month
───────────────────────────────
Total:                   ~$20-70/month
```

### ROI Calculation
```
Time Saved per Week:     10 hours (conservative)
Hourly Value:           $100
Weekly Savings:         $1,000
Annual Savings:         $52,000
───────────────────────────────
Break-even:             < 1 week
```

---

## 🎓 Alternative Architectures Considered

### Option 1: Separate Vector Database (e.g., Pinecone)
**Pros:** Specialized for vectors, built-in monitoring
**Cons:** Additional service, higher cost, data sync complexity
**Decision:** Rejected - pgvector sufficient for our scale

### Option 2: Local-only (no embeddings)
**Pros:** No cost, no external dependencies
**Cons:** No semantic search, keyword-only, poor relevance
**Decision:** Rejected - semantic search is core value prop

### Option 3: AI-powered (no database)
**Pros:** Most flexible, evolves over time
**Cons:** High latency, high cost, non-deterministic
**Decision:** Hybrid approach - use both

---

## 🚀 Getting Started (Quick Start)

### Step 1: Install pgvector
```bash
# Connect to Railway PostgreSQL
psql $RAILWAY_DATABASE_URL

# Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Step 2: Generate Embeddings
```bash
cd /Users/yourox/AI-Workspace
python3 scripts/generate_embeddings.py
```

### Step 3: Install MCP Server
```bash
cd mcp-servers/coding-intelligence
pip3 install -r requirements.txt
```

### Step 4: Test It
```bash
# Start server
python3 server.py

# Test search
curl http://localhost:3000/search_patterns \
  -d '{"query": "Jest testing patterns", "language": "JavaScript"}'
```

### Step 5: Add to Claude Code
```json
// Add to ~/.cursor/mcp.json or equivalent
{
  "mcpServers": {
    "coding-intelligence": {
      "command": "python3",
      "args": ["mcp-servers/coding-intelligence/server.py"]
    }
  }
}
```

---

## 📚 References & Resources

### Technical Documentation
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [CrewAI Documentation](https://docs.crewai.com/)

### Inspirations
- GitHub Copilot (code suggestions)
- Sourcegraph Cody (code intelligence)
- Phind (semantic code search)
- Cursor (AI-powered editor)

### Similar Systems
- TabNine (AI completions)
- Kite (Python code intelligence - discontinued)
- Amazon CodeWhisperer (AWS-focused suggestions)

---

## 🤝 Contributing & Feedback

This is a living architecture document. As we implement and learn, we'll update this design.

**Feedback Channels:**
- Technical discussions: In conversation with Claude Code
- Feature requests: Add to docs/FEATURE_REQUESTS.md
- Bug reports: Add to docs/BUGS.md

---

**Document Version:** 1.0
**Last Updated:** 2025-10-17
**Next Review:** After Phase 1 completion
**Owner:** Claude Code + User (yourox)
