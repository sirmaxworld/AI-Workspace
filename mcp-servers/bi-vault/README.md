# BI-Vault MCP Server

🗄️ **The Intelligence Vault** - Comprehensive Business Intelligence Database via MCP

Exposes AI-extracted business intelligence from **454 video transcripts**, **5,487 YC companies**, and structured insights through Model Context Protocol (MCP).

## 📊 Data Coverage

### Video & Transcript Data
- **454 Video Transcripts** - Full-text searchable via Railway PostgreSQL
- **210+ Products & Tools** - AI tools, SaaS platforms, physical products with sentiment analysis
- **82+ Problems & Solutions** - Validated problems with step-by-step solutions
- **63+ Startup Ideas** - Business concepts with validation and market data
- **64+ Growth Tactics** - Proven marketing strategies across multiple channels
- **69+ AI Workflows** - Automation workflows with implementation details
- **72+ Target Markets** - Market intelligence with demographics and pain points
- **104+ Trends & Signals** - Market trends with opportunity analysis

### Y Combinator Database
- **5,487 YC Companies** - With AI enrichments, batch info, hiring status, industry data

### Intelligence Layers
- **Comment Intelligence** - User validation, high-engagement signals, real problems
- **Meta-Intelligence** - Cross-video patterns, expert consensus, strategy playbooks
- **Enriched Insights** - Quality-scored by actionability, specificity, evidence strength
- **Video Summaries** - Content profiles, experience levels, key takeaways

## 🚀 Quick Start

### Installation

```bash
cd /Users/yourox/AI-Workspace/mcp-servers/bi-vault
pip install -e .
```

### Configuration

Add to your MCP settings (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "bi-vault": {
      "command": "python",
      "args": [
        "/Users/yourox/AI-Workspace/mcp-servers/bi-vault/server.py"
      ]
    }
  }
}
```

### First Steps After Connection

1. **Read the welcome message** - Provides overview and quick start guide
2. **Check `bi://guide`** - Complete query guide with patterns and workflows
3. **Browse `bi://examples`** - Copy-paste examples for common tasks
4. **Reference `bi://schema`** - Understand data structures and filters

## 📚 Discoverable Resources

The server provides **4 comprehensive resources** for optimal querying:

1. **`bi://guide`** - Complete query guide
   - Quick reference table (goal → tools)
   - 5 query patterns (exploratory, keyword, filtered, quality, cross-video)
   - Data layer explanation
   - Common workflows with examples
   - Pro tips and best practices

2. **`bi://schema`** - Data structure reference
   - JSON schemas for all data types
   - Field documentation
   - Valid filter values
   - Relationship explanations

3. **`bi://tools-index`** - Complete tools catalog
   - All 23 tools categorized
   - Examples for each tool
   - Tool selection guide

4. **`bi://examples`** - Real-world query examples
   - 50+ copy-paste examples
   - Multi-step research workflows
   - Advanced techniques

5. **`bi://stats`** - Database statistics
   - Current data coverage
   - Loaded file counts
   - Connection status

## 🔧 Available Tools (23 Total)

### 📦 Basic Search Tools (7)

### 1. `search_products`
Search 210+ products and tools with filtering by category, sentiment, and metrics.

**Example:**
```json
{
  "query": "ai tools",
  "category": "ai-tool",
  "sentiment": "positive",
  "limit": 10
}
```

### 2. `search_problems`
Find validated problems with solutions, implementation steps, and difficulty levels.

**Example:**
```json
{
  "query": "market research",
  "category": "market-research",
  "difficulty": "beginner",
  "limit": 10
}
```

### 3. `search_startup_ideas`
Discover startup concepts with validation, target markets, and business models.

**Example:**
```json
{
  "query": "saas",
  "business_model": "SaaS",
  "limit": 10
}
```

### 4. `search_growth_tactics`
Find proven growth strategies with implementation steps and expected results.

**Example:**
```json
{
  "query": "viral marketing",
  "channel": "content",
  "limit": 10
}
```

### 5. `search_ai_workflows`
Search AI automation workflows with tools, steps, and use cases.

**Example:**
```json
{
  "query": "youtube transcript",
  "automation_level": "semi-automated",
  "limit": 10
}
```

### 6. `search_target_markets`
Get market intelligence with demographics, pain points, and opportunities.

**Example:**
```json
{
  "query": "fitness",
  "limit": 10
}
```

### 7. `search_trends`
Find market trends with stage analysis and opportunity insights.

**Example:**
```json
{
  "query": "ai",
  "stage": "growing",
  "category": "technology",
  "limit": 10
}
```

### 8. `search_business_strategies`
Discover proven strategies with implementation details and case studies.

**Example:**
```json
{
  "query": "branding",
  "strategy_type": "branding",
  "limit": 10
}
```

### 9. `get_market_opportunities`
Analyze and rank market opportunities based on trends, problems, and markets.

**Example:**
```json
{
  "min_growth_stage": "growing",
  "limit": 10
}
```

### 10. `get_actionable_quotes`
Get high-value quotes categorized by strategy, branding, operations, etc.

**Example:**
```json
{
  "category": "strategy",
  "limit": 20
}
```

### 11. `get_key_metrics`
Retrieve KPIs, benchmarks, and optimization tips.

**Example:**
```json
{
  "query": "conversion",
  "limit": 10
}
```

### 12. `get_mistakes_to_avoid`
Learn from common mistakes with prevention strategies and examples.

**Example:**
```json
{
  "query": "market validation",
  "limit": 10
}
```

### 13. `get_database_stats`
Get comprehensive database statistics and coverage.

**Example:**
```json
{}
```

## 💡 Use Cases

### For Market Research Agents
```python
# Find growing markets
search_trends(query="", stage="growing", category="all")

# Get target market intelligence
search_target_markets(query="fitness enthusiasts")

# Analyze opportunities
get_market_opportunities(min_growth_stage="growing", limit=10)
```

### For Product Discovery Agents
```python
# Find product ideas
search_products(query="saas", category="saas", sentiment="positive")

# Get validation data
search_startup_ideas(query="ai", business_model="SaaS")

# Learn from successful products
get_key_metrics(query="revenue")
```

### For Strategy Agents
```python
# Get proven strategies
search_business_strategies(query="branding", strategy_type="branding")

# Find growth tactics
search_growth_tactics(query="viral", channel="content")

# Get actionable insights
get_actionable_quotes(category="strategy")
```

### For Problem-Solving Agents
```python
# Find problems to solve
search_problems(query="market research", difficulty="beginner")

# Get implementation workflows
search_ai_workflows(query="automation", automation_level="semi-automated")

# Avoid mistakes
get_mistakes_to_avoid(query="validation")
```

## 🎯 Integration with CrewAI

Use this MCP server with your CrewAI agents:

```python
from crewai import Agent, Task, Crew
from crewai_tools import MCPTool

# Create MCP tool
bi_tool = MCPTool(server="business-intelligence")

# Create agent with BI access
market_researcher = Agent(
    role='Market Research Specialist',
    goal='Find high-potential market opportunities',
    tools=[bi_tool],
    backstory='Expert at analyzing business intelligence data'
)

# Create task
research_task = Task(
    description="""
    Use the business intelligence MCP to:
    1. Search for growing trends in technology
    2. Find validated problems in that market
    3. Identify target markets with pain points
    4. Recommend top 3 opportunities
    """,
    agent=market_researcher
)

# Run
crew = Crew(agents=[market_researcher], tasks=[research_task])
result = crew.kickoff()
```

## 📈 Data Sources

All data extracted from 49+ YouTube videos using:
- Claude Sonnet 4.5 for AI extraction
- Browserbase for web scraping
- Structured business intelligence schema
- Vector database for semantic search (Qdrant)

**Videos include:**
- Greg Isenberg (48 videos): Startup ideas, market trends, growth tactics
- Seena Rez (1 video): $2.7M brand building strategy, AI workflows

## 🔄 Updates

The database automatically loads all `*_insights.json` files from:
```
/Users/yourox/AI-Workspace/data/business_insights/
```

To add new videos:
1. Extract transcript using `browserbase_transcript_extractor.py`
2. Extract insights using `business_intelligence_extractor.py`
3. Restart MCP server to reload data

## 🤝 Support

For issues or questions, refer to the main AI-Workspace documentation.

## 📝 License

MIT License - See main repository for details.
