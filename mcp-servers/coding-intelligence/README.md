# Coding Intelligence MCP Server

Semantic search for coding patterns, best practices, libraries, and tools using natural language queries.

## 🎯 What This Does

Provides 8 intelligent coding assistance tools powered by vector embeddings:

1. **search_patterns** - Find coding patterns by description
2. **get_best_practices** - Get best practices for specific use cases
3. **suggest_library** - Find suitable OSS libraries
4. **find_mcp_tool** - Discover MCP servers
5. **analyze_security** - Get security recommendations
6. **get_architecture_advice** - Architecture guidance
7. **discover_similar** - Find similar items
8. **check_code** - Validate code against best practices

## 📊 Intelligence Database

- **248** coding patterns
- **1,001** best practices and rules
- **451** production-ready OSS libraries
- **4,113** MCP servers
- **5,813** total intelligence records

All with 100% embedding coverage for semantic search.

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip3 install sentence-transformers psycopg2-binary python-dotenv mcp

# Set environment variable
export RAILWAY_DATABASE_URL="your_database_url"
```

### Run the Server

```bash
python3 server.py
```

### Test the Server

```bash
python3 ../../scripts/test_mcp_server.py
```

## 🔧 Integration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coding-intelligence": {
      "command": "python3",
      "args": [
        "/Users/yourox/AI-Workspace/mcp-servers/coding-intelligence/server.py"
      ],
      "env": {
        "RAILWAY_DATABASE_URL": "your_database_url"
      }
    }
  }
}
```

### Cursor IDE

Add to Cursor MCP settings:

```json
{
  "coding-intelligence": {
    "command": "python3",
    "args": ["/path/to/server.py"],
    "env": {
      "RAILWAY_DATABASE_URL": "your_database_url"
    }
  }
}
```

## 📖 Tool Examples

### Search Patterns

```python
search_patterns("testing framework for JavaScript")
# Returns: Jest, Mocha, etc. with similarity scores
```

### Suggest Library

```python
suggest_library("lightweight date library for JavaScript")
# Returns: dayjs (0.658), date-fns (0.676)
```

### Find MCP Tool

```python
find_mcp_tool("database integration and SQL queries")
# Returns: Database MCP servers with install commands
```

### Analyze Security

```python
analyze_security("prevent SQL injection attacks")
# Returns: Security best practices and patterns
```

### Check Code

```python
check_code("storing user passwords in database")
# Returns: Relevant security and storage best practices
```

## 🎨 Resources

The server also exposes two resources:

### intelligence://stats
Get database statistics and embedding coverage

### intelligence://languages
Get list of supported programming languages

## ⚡ Performance

- **Query latency**: ~323ms average
- **Embedding dimensions**: 384
- **Model**: all-MiniLM-L6-v2 (local, FREE)
- **Search type**: Semantic vector search with cosine similarity

## 🔒 Privacy

- **100% local embeddings** - No external API calls
- **No data leaves your system** - All processing is local
- **FREE to use** - No API costs

## 📁 Architecture

```
Layer 1: Railway PostgreSQL (pgvector)
         ↓
Layer 2: Sentence-Transformers (384d embeddings)
         ↓
Layer 3: Vector Search API (cosine similarity)
         ↓
Layer 4: FastMCP Server (8 tools)
         ↓
Layer 5: AI Consumers (Claude, Cursor, CrewAI)
```

## 🐛 Debugging

### Check Database Connection

```python
python3 -c "
import os
from dotenv import load_dotenv
import psycopg2
load_dotenv('/Users/yourox/AI-Workspace/.env')
conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
print('✅ Database connected')
conn.close()
"
```

### Test Embedding Model

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("test query")
print(f"✅ Model working: {len(embedding)} dimensions")
```

### Test Vector Search

```bash
python3 ../../scripts/test_vector_search.py
```

## 📊 Monitoring

### Check Embedding Coverage

```sql
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE embedding IS NOT NULL) as embedded,
    ROUND(COUNT(*) FILTER (WHERE embedding IS NOT NULL)::NUMERIC / COUNT(*) * 100, 2) as percentage
FROM coding_patterns;
```

### Check Search Performance

```sql
EXPLAIN ANALYZE
SELECT 1 - (embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM coding_patterns
WHERE embedding IS NOT NULL
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

## 🎯 Use Cases

### Code Review Agent
Use `check_code` and `get_best_practices` to validate code against rules

### Architecture Assistant
Use `get_architecture_advice` and `search_patterns` for design guidance

### Library Recommendation
Use `suggest_library` to find suitable OSS packages

### Security Auditor
Use `analyze_security` to identify security concerns

### Learning Assistant
Use `search_patterns` and `discover_similar` to learn new patterns

## 🔮 Future Enhancements

- [ ] Smart triggers for proactive assistance
- [ ] CrewAI agent integration
- [ ] Real-time pattern updates
- [ ] Community feedback integration
- [ ] Multi-agent collaboration

## 📝 Technical Details

### Embedding Model
- **Name**: all-MiniLM-L6-v2
- **Type**: Sentence-Transformers
- **Dimensions**: 384
- **Speed**: ~20 embeddings/second
- **Provider**: Local (HuggingFace)

### Vector Index
- **Type**: HNSW (Hierarchical Navigable Small World)
- **Distance**: Cosine
- **Dimensions**: 384

### Database
- **Type**: PostgreSQL 16.10
- **Extension**: pgvector 0.8.1
- **Host**: Railway

## 🙏 Credits

- **Sentence-Transformers** for local embedding models
- **pgvector** for PostgreSQL vector extension
- **FastMCP** for MCP server framework

## 📞 Support

For issues or questions:
1. Check logs in `/tmp/intelligence_logs/`
2. Run test suite: `python3 ../../scripts/test_mcp_server.py`
3. Verify database connection
4. Check embedding model installation

## 📄 License

Part of AI-Workspace - Private project

---

**Status**: ✅ FULLY OPERATIONAL

**Last Updated**: October 17, 2025

**Version**: 1.0.0
