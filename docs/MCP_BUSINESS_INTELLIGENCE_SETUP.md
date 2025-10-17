# Business Intelligence MCP Server Setup Guide

## 🎯 Overview

This MCP server exposes your entire business intelligence database (49+ YouTube videos, 700+ insights) to any AI agent through the Model Context Protocol.

**What this enables:**
- CrewAI agents can query your BI data during research
- Claude Desktop can access market insights directly
- Other AI applications can leverage your business intelligence
- Automated market research using existing validated data

---

## 📦 Installation

### Step 1: Install MCP Package

```bash
cd /Users/yourox/AI-Workspace/mcp-servers/business-intelligence
pip install -e .
```

This installs the MCP server in editable mode so updates are reflected immediately.

### Step 2: Verify Installation

```bash
python server.py
```

The server should start without errors. Press Ctrl+C to stop.

---

## ⚙️ Configuration

### For Claude Desktop

Edit your Claude Desktop configuration file:

**macOS:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Add this configuration:**
```json
{
  "mcpServers": {
    "business-intelligence": {
      "command": "python",
      "args": [
        "/Users/yourox/AI-Workspace/mcp-servers/business-intelligence/server.py"
      ]
    }
  }
}
```

**Restart Claude Desktop** to load the new MCP server.

### For CrewAI Agents

Add to your CrewAI agent tools:

```python
from crewai_tools import MCPTool

# Initialize MCP tool
bi_mcp = MCPTool(
    server_name="business-intelligence",
    server_path="/Users/yourox/AI-Workspace/mcp-servers/business-intelligence/server.py"
)

# Add to agent
agent = Agent(
    role='Market Researcher',
    tools=[bi_mcp],
    # ... other config
)
```

### For Other Applications

Use the MCP SDK to connect:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to server
server_params = StdioServerParameters(
    command="python",
    args=["/Users/yourox/AI-Workspace/mcp-servers/business-intelligence/server.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()

        # List available tools
        tools = await session.list_tools()

        # Call a tool
        result = await session.call_tool(
            "search_products",
            arguments={"query": "ai tools", "limit": 10}
        )
```

---

## 🔍 Usage Examples

### Example 1: Market Research Agent

```python
# Agent searches for growing market opportunities
result = mcp.call_tool(
    "get_market_opportunities",
    {
        "min_growth_stage": "growing",
        "limit": 10
    }
)

# Returns:
# - Growing trends with opportunity analysis
# - Related validated problems
# - Target markets with pain points
# - Supporting evidence from 49+ videos
```

### Example 2: Product Discovery Agent

```python
# Find AI tools with positive sentiment
products = mcp.call_tool(
    "search_products",
    {
        "query": "chatgpt",
        "category": "ai-tool",
        "sentiment": "positive",
        "limit": 20
    }
)

# Returns:
# - Product name, category, use case
# - Pricing information
# - Performance metrics
# - Source video metadata
```

### Example 3: Strategy Research Agent

```python
# Get branding strategies
strategies = mcp.call_tool(
    "search_business_strategies",
    {
        "query": "identity",
        "strategy_type": "branding",
        "limit": 10
    }
)

# Returns:
# - Strategy descriptions
# - Implementation steps
# - Expected results
# - Real case studies
```

### Example 4: Problem-Solving Agent

```python
# Find beginner-friendly market research problems
problems = mcp.call_tool(
    "search_problems",
    {
        "query": "market validation",
        "category": "market-research",
        "difficulty": "beginner",
        "limit": 5
    }
)

# Returns:
# - Problem description
# - Step-by-step solutions
# - Tools needed
# - Time estimates
```

### Example 5: Get Database Overview

```python
# Get comprehensive statistics
stats = mcp.call_tool("get_database_stats", {})

# Returns:
# {
#   "total_files": 49,
#   "total_products": 210,
#   "total_problems": 82,
#   "total_startup_ideas": 63,
#   "total_growth_tactics": 64,
#   "total_ai_workflows": 69,
#   "total_target_markets": 72,
#   "total_trends": 104,
#   ...
# }
```

---

## 🤖 Integration with Your AI Business Crew

### Update ai_business_crew.py

Add MCP tools to your agents:

```python
from crewai_tools import MCPTool

class AIBusinessCrew:
    def __init__(self):
        # Initialize MCP tool
        self.bi_mcp = MCPTool(
            server_name="business-intelligence",
            server_path="/Users/yourox/AI-Workspace/mcp-servers/business-intelligence/server.py"
        )

    def create_market_trend_analyzer(self):
        return Agent(
            role='Market Research Specialist',
            goal='Identify growing markets with high CAGR and low brand saturation',
            backstory="""Expert in market analysis with access to business intelligence
            database from 49+ analyzed videos.""",
            tools=[
                self.bi_mcp,  # Access to BI database
                search_tool,
                scrape_tool
            ],
            llm='anthropic/claude-sonnet-4-20250514'
        )

    def create_market_discovery_task(self, agent):
        return Task(
            description="""
            Use the business intelligence MCP to:
            1. Search for growing trends (stage: "growing" or "emerging")
            2. Find validated problems in those markets
            3. Identify target markets with clear pain points
            4. Cross-reference with Google Trends data
            5. Return top 5 market opportunities with supporting evidence

            Use tools:
            - search_trends(query="", stage="growing")
            - get_market_opportunities(min_growth_stage="growing")
            - search_target_markets(query="[market keyword]")
            - search_problems(query="[market keyword]")
            """,
            agent=agent,
            expected_output="Ranked list of 5 market opportunities with validation data"
        )
```

### Example: Market Discovery with BI Data

```python
crew = AIBusinessCrew()

# Agent 1: Market Trend Analyzer (with BI access)
market_agent = crew.create_market_trend_analyzer()
market_task = crew.create_market_discovery_task(market_agent)

# Agent 2: Product Discovery (with BI access)
product_agent = crew.create_product_discovery_agent()
product_task = Task(
    description="""
    Using the market from previous agent:
    1. Use BI MCP to find similar successful products
    2. Search AI workflows for product discovery methods
    3. Get actionable quotes about product validation

    Tools to use:
    - search_products(query="[market keyword]")
    - search_ai_workflows(query="product discovery")
    - get_actionable_quotes(category="strategy")
    """,
    agent=product_agent,
    context=[market_task]
)

# Run with BI intelligence
crew = Crew(
    agents=[market_agent, product_agent],
    tasks=[market_task, product_task],
    process=Process.sequential
)

result = crew.kickoff()
```

---

## 📊 What Each Tool Returns

### Search Tools Return Format

```json
{
  "query": "search term",
  "filters": {"category": "ai-tool"},
  "count": 15,
  "results": [
    {
      // Data fields specific to category
      "video_id": "5FokzkHTpc0",
      "video_title": "how I built a $2.7M brand using a.i",
      "source_file": "/path/to/insights.json"
    }
  ]
}
```

### Market Opportunities Return Format

```json
{
  "min_growth_stage": "growing",
  "count": 10,
  "opportunities": [
    {
      "trend": {
        "trend": "AI-powered market research",
        "stage": "early",
        "opportunity": "Use AI before competition"
      },
      "related_problems": [
        {
          "problem": "Finding untapped products",
          "solution": "AI-powered YouTube analysis"
        }
      ],
      "related_markets": [
        {
          "market_description": "E-commerce entrepreneurs",
          "pain_points": ["Product discovery difficulty"]
        }
      ]
    }
  ]
}
```

---

## 🔄 Updating the Database

The MCP server automatically loads all files from:
```
/Users/yourox/AI-Workspace/data/business_insights/*_insights.json
```

**To add new videos:**

1. Extract transcript:
```bash
python scripts/browserbase_transcript_extractor.py VIDEO_ID
```

2. Extract business intelligence:
```bash
python scripts/business_intelligence_extractor.py VIDEO_ID
```

3. Restart MCP server (or Claude Desktop)

The new data is automatically included!

---

## 🎓 Best Practices

### 1. Use Specific Queries
```python
# ❌ Too broad
search_products(query="", category="all")

# ✅ Specific
search_products(query="chatgpt youtube", category="ai-tool", sentiment="positive")
```

### 2. Combine Multiple Tools
```python
# Get comprehensive market view
trends = search_trends(query="fitness", stage="growing")
markets = search_target_markets(query="fitness")
problems = search_problems(query="fitness", category="market-research")
```

### 3. Use Filters Effectively
```python
# Filter by difficulty for beginner agents
search_problems(query="validation", difficulty="beginner")

# Filter by stage for emerging opportunities
search_trends(query="", stage="emerging")
```

### 4. Check Database Stats First
```python
# Understand what's available
stats = get_database_stats()
print(f"Available: {stats['total_products']} products, {stats['total_trends']} trends")
```

---

## 🚀 Advanced Usage

### Chaining Queries for Deep Research

```python
# Step 1: Find growing trends
trends = search_trends(stage="growing", limit=5)

# Step 2: For each trend, find problems
for trend in trends['results']:
    keyword = trend['trend'].split()[0]
    problems = search_problems(query=keyword)

# Step 3: Get relevant strategies
strategies = search_business_strategies(query=keyword)

# Step 4: Find successful case studies
quotes = get_actionable_quotes(category="strategy")
```

### Building Market Intelligence Reports

```python
def create_market_report(market_keyword):
    """Generate comprehensive market intelligence report"""

    report = {
        'trends': search_trends(query=market_keyword, stage="all"),
        'target_markets': search_target_markets(query=market_keyword),
        'problems': search_problems(query=market_keyword),
        'products': search_products(query=market_keyword),
        'growth_tactics': search_growth_tactics(query=market_keyword),
        'strategies': search_business_strategies(query=market_keyword),
        'opportunities': get_market_opportunities(min_growth_stage="emerging"),
        'key_metrics': get_key_metrics(query=market_keyword),
        'mistakes': get_mistakes_to_avoid(query=market_keyword)
    }

    return report

# Use in agent
market_report = create_market_report("pilates")
```

---

## 🐛 Troubleshooting

### MCP Server Not Starting

```bash
# Check Python version (must be 3.10+)
python --version

# Reinstall dependencies
pip install -e . --force-reinstall

# Check data directory exists
ls /Users/yourox/AI-Workspace/data/business_insights/
```

### No Results Returned

```python
# Check database loaded correctly
stats = get_database_stats()
print(stats)  # Should show counts > 0

# Try broader query
search_products(query="", category="all", limit=100)
```

### Claude Desktop Not Showing Tools

1. Verify config file location:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Check JSON syntax is valid

3. Restart Claude Desktop completely

4. Check Claude Desktop logs for errors

---

## 📈 Performance Tips

1. **Use limits wisely**: Default is 20, but you can increase for comprehensive searches
2. **Cache common queries**: Store frequently used results in agent memory
3. **Use specific categories**: Filtering by category is faster than searching all
4. **Start broad, then narrow**: Get overview with stats, then specific searches

---

## 🎯 Next Steps

1. ✅ Install and configure MCP server
2. ✅ Test with Claude Desktop
3. ✅ Integrate with CrewAI agents
4. ✅ Add MCP tools to your AI Business Crew
5. ✅ Run end-to-end workflow with BI intelligence
6. ✅ Monitor results and optimize queries

---

## 💡 Key Benefits

**For Agents:**
- Access to 700+ validated insights instantly
- No need to re-research common problems
- Learn from 49+ successful case studies
- Faster decision-making with proven data

**For You:**
- Maximize ROI on your BI database
- Reusable intelligence across projects
- Compound value from each video analyzed
- Automated market research at scale

---

**Your business intelligence is now an AI-accessible knowledge base!** 🚀
