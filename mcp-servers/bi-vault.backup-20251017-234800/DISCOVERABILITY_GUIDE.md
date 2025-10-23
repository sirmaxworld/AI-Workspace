# BI-Vault MCP Server - Discoverability Guide

## 🎯 Making Your MCP Server More Discoverable

This document explains how the BI-Vault MCP server has been optimized for discoverability by agents and Claude Desktop **without** adding excessive logical aggregates.

## ✅ What We've Implemented

### 1. **Enhanced Server Instructions** (Visible on connection)
The server now provides a rich, informative welcome message that agents see immediately upon connection:

```
🗄️ THE INTELLIGENCE VAULT - Your Business Intelligence Database

📊 WHAT'S INSIDE:
• 454 Video Transcripts (full-text searchable via Railway PostgreSQL)
• 5,487 Y Combinator Companies (with AI enrichments)
• 210+ Products & Tools | 82+ Problems & Solutions | 63+ Startup Ideas
...

🎯 QUICK START (Check these resources first):
1. bi://guide - Complete query guide (READ THIS FIRST!)
2. bi://schema - Data structure reference
3. bi://tools-index - All 23 tools with examples
4. bi://stats - Database statistics

💡 COMMON USE CASES:
→ Market Research: get_meta_trends() + search_target_markets()
→ Startup Ideas: search_startup_ideas() + get_opportunity_matrix()
...
```

**Impact**: Agents immediately understand what's available and how to use it.

---

### 2. **Resource-Based Documentation** (Discoverable guides)

We added **4 comprehensive resources** that agents can access anytime:

#### **a) `bi://guide` - Complete Query Guide**
- Quick reference table (goal → recommended tools)
- 5 query patterns (exploratory, keyword search, filtered, quality-filtered, cross-video)
- Data layer explanation (Raw → Enriched → Meta → Comments)
- Common workflows with step-by-step examples
- Pro tips and best practices
- Real query examples

**Why this works**: Agents can reference this guide to understand HOW to query optimally, not just WHAT tools exist.

#### **b) `bi://schema` - Data Structure Reference**
- Complete JSON schema for every data type
- Field-level documentation
- Valid enum values for filters
- Relationship explanations

**Why this works**: Agents know exactly what fields are available for filtering without trial and error.

#### **c) `bi://tools-index` - Complete Tools Catalog**
- All 23 tools categorized by function
- Each tool with description and example
- Tool selection decision tree
- Layered approach guidance (meta → specific → detailed)

**Why this works**: Agents can quickly find the right tool for their task.

#### **d) `bi://examples` - Real-World Query Examples**
- 50+ copy-paste examples for common questions
- Multi-step research workflows
- Advanced techniques (empty queries, progressive filtering, cross-referencing)
- Engagement signal interpretation

**Why this works**: Agents can copy proven patterns instead of experimenting.

---

### 3. **Organized Tool Categories** (Mental model)

All 23 tools are logically grouped:

1. **Basic Search Tools** (7) - Query specific categories
2. **Comment Intelligence Tools** (4) - User validation signals
3. **YC Companies Tools** (1) - Startup database
4. **Enriched Intelligence Tools** (3) - Quality-scored insights
5. **Video Transcript Tools** (2) - Full-text search
6. **Meta-Intelligence Tools** (5) - Cross-video analysis
7. **Utility Tools** (1) - Stats and info

**Why this works**: Agents understand the conceptual hierarchy and can navigate from broad to specific.

---

## 🚀 Best Practices We're Following

### ✅ DO: Use Resources for Documentation
- **Resources** are perfect for static guides, schemas, and examples
- They're discoverable and don't clutter the tool list
- Agents can reference them repeatedly without cost

### ✅ DO: Provide Clear Instructions
- Rich server instructions visible on connection
- Point to resources in the instructions
- Include common use cases right away

### ✅ DO: Show Query Patterns
- Empty query examples (query="")
- Progressive filtering workflows
- Multi-step research patterns

### ✅ DO: Organize by Conceptual Layers
```
Meta-intelligence (Cross-video patterns)
    ↓
Enriched data (Quality scores)
    ↓
Raw insights (Individual items)
    ↓
Transcripts (Source material)
```

### ❌ DON'T: Add Too Many Tools
- 23 tools is reasonable for a comprehensive BI vault
- More tools = harder to discover the right one
- Instead: Better documentation + examples

### ❌ DON'T: Hide Important Info
- Server instructions should highlight key resources
- Don't make agents guess what's available
- Be explicit about data coverage and limitations

---

## 📊 Why This Approach Works

### 1. **Immediate Context on Connection**
Agents see exactly what's available and where to start in the server instructions.

### 2. **Progressive Disclosure**
- Instructions → Point to resources
- Resources → Provide deep documentation
- Tools → Do the actual work

### 3. **Multiple Learning Paths**
- **By Goal**: Use the quick reference table in `bi://guide`
- **By Data Type**: Use `bi://schema`
- **By Example**: Use `bi://examples`
- **By Tool**: Use `bi://tools-index`

### 4. **No Cognitive Overload**
Instead of 50+ tools to choose from, we have:
- 23 well-documented tools
- 4 reference resources
- Clear categorization
- Concrete examples

---

## 🎪 How Agents Should Use This

### **First Connection**
1. Read server instructions (automatic)
2. Check `bi://guide` for overview
3. Browse `bi://examples` for common tasks

### **During Research**
1. Use `bi://guide` quick reference to pick tools
2. Check `bi://schema` if unsure about filters
3. Copy examples from `bi://examples`

### **For Complex Workflows**
1. Follow multi-step workflows in `bi://examples`
2. Combine meta-intelligence → specific searches
3. Use engagement signals for validation

---

## 🔧 Technical Implementation

### Resources in FastMCP
```python
@mcp.resource("bi://guide")
def get_query_guide() -> str:
    """
    Complete query guide and best practices.
    Read this first to understand how to query optimally.
    """
    return """..."""
```

### Enhanced Instructions
```python
mcp = FastMCP(
    "BI-Vault",
    instructions="""🗄️ THE INTELLIGENCE VAULT

    📊 WHAT'S INSIDE:
    ...

    🎯 QUICK START (Check these resources first):
    1. bi://guide - Complete query guide
    ...
    """
)
```

---

## 📈 Measuring Success

### **Good Indicators:**
✅ Agents check resources before querying
✅ Agents use meta-intelligence tools first (validated patterns)
✅ Agents leverage quality filters (enrichment scores)
✅ Agents cross-reference multiple data sources
✅ Query patterns match the recommended workflows

### **Bad Indicators:**
❌ Agents make random tool calls without pattern
❌ Agents ignore quality filters
❌ Agents don't use meta-intelligence
❌ Agents ask "what tools are available?"

---

## 🎯 Key Takeaways

1. **Resources > More Tools**: Documentation resources are more valuable than dozens of aggregate tools
2. **Instructions Matter**: Rich server instructions guide agents immediately
3. **Examples > Descriptions**: Concrete examples are more useful than abstract descriptions
4. **Layered Architecture**: Meta → Enriched → Raw → Source gives agents a mental model
5. **Progressive Disclosure**: Start simple (instructions) → Deep dive (resources) → Execute (tools)

---

## 🚀 Next Steps (Optional Enhancements)

If you want to go even further:

1. **Add MCP Prompts** (pre-configured workflows agents can invoke)
2. **Add bi://changelog** resource (track updates)
3. **Add bi://tips** resource (advanced power-user tips)
4. **Enhance tool descriptions** with mini-examples in docstrings
5. **Add semantic tags** to tools for better discovery

---

## 📚 References

- [MCP Resources Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- MCP Best Practices (see Claude Code docs)

---

**Bottom Line**: We've made your BI-Vault server highly discoverable through **structured documentation resources** rather than tool proliferation. Agents now have clear guidance on how to query effectively from the moment they connect.
