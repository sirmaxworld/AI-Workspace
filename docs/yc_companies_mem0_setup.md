# Y Combinator Companies → Mem0 Integration

Complete guide for adding 5,490+ YC companies to your local Mem0 vector database for semantic search.

## Overview

This integration adds Y Combinator company data to your existing Mem0 (memory) system, enabling:
- **Semantic search** across all YC companies using natural language
- **AI-powered retrieval** in Claude conversations
- **Unified knowledge base** alongside your business intelligence data
- **Local storage** using Qdrant vector database

## Architecture

```
YC API (5,490 companies)
    ↓
JSON Cache (local)
    ↓
Mem0 Ingestion Script
    ↓
Qdrant Vector Store (local)
    ├─ yc_companies collection
    ├─ claude_memory collection
    └─ research_papers collection
    ↓
Query via:
  1. Python script (search_companies)
  2. Business Intelligence MCP Server
  3. Claude Desktop (if MCP enabled)
```

## Quick Start

### 1. Prerequisites

```bash
# Install dependencies
pip install mem0ai qdrant-client openai anthropic

# Ensure you have cached YC companies data
python3 scripts/yc_companies_extractor.py --analyze
```

### 2. Ingest to Mem0

```bash
# Test with 10 companies
python3 scripts/yc_companies_to_mem0.py --max 10

# Ingest all 5,490 companies (takes ~20-30 minutes)
python3 scripts/yc_companies_to_mem0.py

# Custom batch size for faster/slower ingestion
python3 scripts/yc_companies_to_mem0.py --batch-size 100
```

### 3. Search Companies

```bash
# Natural language search
python3 scripts/yc_companies_to_mem0.py --search "AI companies in healthcare"

# Search for specific company
python3 scripts/yc_companies_to_mem0.py --search "Stripe"

# Search for hiring companies
python3 scripts/yc_companies_to_mem0.py --search "companies hiring developers"
```

## Mem0 Configuration

The YC companies collection uses the same configuration as your other collections:

```python
# From config/mem0_collections.py

{
    "llm": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514"
    },
    "embedder": {
        "provider": "openai",
        "model": "text-embedding-3-small"
    },
    "vector_store": {
        "provider": "qdrant",
        "collection_name": "yc_companies",
        "path": "/Users/yourox/AI-Workspace/data/qdrant"
    }
}
```

## Data Format in Mem0

Each company is stored as rich text with metadata:

**Text Format:**
```markdown
# Company Name
Batch: W21 | Status: Active

Brief description of what the company does.

## Description
Full description of the company, its mission, and products.

## Classification
Industry: B2B
Sub-industry: Developer Tools
Stage: Growth

## Team
Team Size: 50
🟢 Currently Hiring
⭐ YC Top Company

## Tags
artificial-intelligence, developer-tools, saas

## Links
Website: https://company.com
YC Profile: https://www.ycombinator.com/companies/company
```

**Metadata:**
```json
{
    "company_id": 123,
    "name": "Company Name",
    "slug": "company-slug",
    "batch": "W21",
    "status": "Active",
    "industry": "B2B",
    "team_size": 50,
    "is_hiring": true,
    "top_company": true,
    "website": "https://company.com",
    "source": "yc_companies",
    "ingested_at": "2025-01-15T10:30:00"
}
```

## Usage

### Python API

```python
from scripts.yc_companies_to_mem0 import YCCompaniesToMem0

# Initialize
ingestor = YCCompaniesToMem0(collection_name="yc_companies")

# Search
results = ingestor.search_companies("AI in healthcare", limit=10)

for result in results:
    metadata = result['metadata']
    print(f"{metadata['name']} - {metadata['batch']}")
    print(f"  {metadata.get('industry', 'N/A')}")
    if metadata.get('is_hiring'):
        print("  🟢 Hiring")
```

### Business Intelligence MCP Server

The companies are automatically loaded in the BI MCP server:

```python
# Available in Claude Desktop via MCP
@mcp.tool()
def search_yc_companies(
    query: str,
    batch: str = None,
    industry: str = None,
    status: str = None,
    is_hiring: bool = None,
    limit: int = 20
)
```

Example queries in Claude Desktop:
- "Show me YC companies in healthcare"
- "Find AI companies from W21 batch that are hiring"
- "What are the top YC fintech companies?"

### Search Examples

**By Industry:**
```bash
python3 scripts/yc_companies_to_mem0.py --search "B2B SaaS companies"
```

**By Technology:**
```bash
python3 scripts/yc_companies_to_mem0.py --search "machine learning and NLP"
```

**By Stage:**
```bash
python3 scripts/yc_companies_to_mem0.py --search "early stage startups"
```

**By Problem Space:**
```bash
python3 scripts/yc_companies_to_mem0.py --search "solving climate change"
```

## Benefits of Mem0 Integration

### 1. Semantic Search
Unlike keyword matching, Mem0 understands context:
- Query: "developer tools for startups" → Finds relevant companies even without exact keywords
- Query: "companies like Stripe" → Finds similar payment/fintech companies
- Query: "AI for doctors" → Matches healthcare + AI companies

### 2. Unified Knowledge Base
Your business intelligence data and YC companies live together:
```
Qdrant Collections:
├── yc_companies (5,490 companies)
├── claude_memory (conversation history)
└── research_papers (future)
```

### 3. AI-Powered Insights
Mem0 uses Claude to:
- Understand natural language queries
- Extract relevant context
- Rank results by relevance
- Provide semantic similarity

### 4. Fast Local Search
- All data stored locally (no API calls for search)
- Sub-second query times
- Works offline
- Privacy-preserving

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Fetch from API | ~2 seconds | Cached after first run |
| Ingest 100 companies | ~1-2 minutes | With OpenAI embeddings |
| Ingest all 5,490 | ~20-30 minutes | One-time setup |
| Search query | <1 second | Local vector search |

## Updating Data

To refresh with latest YC companies:

```bash
# 1. Fetch latest data
python3 scripts/yc_companies_extractor.py --refresh

# 2. Re-ingest to Mem0
python3 scripts/yc_companies_to_mem0.py
```

Mem0 will handle updates intelligently - existing entries are preserved, new companies are added.

## Advanced Usage

### Custom Collection Name

```bash
python3 scripts/yc_companies_to_mem0.py --collection yc_companies_2025
```

### Batch Processing

```python
from scripts.yc_companies_to_mem0 import YCCompaniesToMem0

ingestor = YCCompaniesToMem0()

# Ingest specific batches
companies = ingestor.load_companies()
w21_companies = [c for c in companies if c.get('batch') == 'W21']

# Process with custom logic
for company in w21_companies:
    text = ingestor.format_company_for_mem0(company)
    # Custom processing...
```

### Integration with Existing Workflows

```python
# In your scripts
from scripts.yc_companies_to_mem0 import YCCompaniesToMem0

ingestor = YCCompaniesToMem0()

# Find similar companies
def find_similar_companies(company_name: str, limit: int = 5):
    results = ingestor.search_companies(company_name, limit=limit)
    return [r['metadata'] for r in results]

# Get hiring companies
def get_hiring_in_industry(industry: str):
    query = f"{industry} companies currently hiring"
    results = ingestor.search_companies(query, limit=20)
    return [r for r in results if r['metadata'].get('is_hiring')]
```

## Troubleshooting

### "Mem0 not initialized"
- Check: `pip list | grep mem0ai`
- Install: `pip install mem0ai`

### "Companies cache not found"
- Run: `python3 scripts/yc_companies_extractor.py --analyze`
- Verify: `ls data/yc_companies/all_companies.json`

### "Search error: user_id required"
- Fixed in latest version
- Update script if needed

### Slow ingestion
- Reduce batch size: `--batch-size 25`
- Test with fewer companies: `--max 100`
- Check OpenAI API rate limits

### Empty search results
- Ensure companies are ingested first
- Check collection name matches
- Verify Qdrant path exists

## File Structure

```
AI-Workspace/
├── config/
│   └── mem0_collections.py          # Collection configurations
├── scripts/
│   ├── yc_companies_extractor.py    # Fetch and cache YC data
│   └── yc_companies_to_mem0.py      # Ingest to Mem0
├── mcp-servers/business-intelligence/
│   └── server.py                     # MCP server with YC search
├── data/
│   ├── yc_companies/
│   │   └── all_companies.json       # Cached YC data (5,490 companies)
│   └── qdrant/
│       └── yc_companies/            # Vector database storage
└── docs/
    └── yc_companies_mem0_setup.md   # This file
```

## Next Steps

1. **Ingest Data**: Run the full ingestion (20-30 min one-time setup)
   ```bash
   python3 scripts/yc_companies_to_mem0.py
   ```

2. **Test Search**: Try semantic queries
   ```bash
   python3 scripts/yc_companies_to_mem0.py --search "your query"
   ```

3. **Integrate with MCP**: YC companies already available in BI MCP server

4. **Build Custom Tools**: Use the Python API in your workflows

## Resources

- **Mem0 Docs**: https://docs.mem0.ai/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **YC Companies API**: https://github.com/yc-oss/api
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings

## Support

For issues:
1. Check logs in terminal output
2. Verify all dependencies installed
3. Ensure YC data is cached
4. Test with small batch first (`--max 10`)
