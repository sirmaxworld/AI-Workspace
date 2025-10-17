# Y Combinator Companies Database Setup

Complete guide to adding 5,490+ Y Combinator companies to your database with full metadata.

## Overview

This feature adds comprehensive Y Combinator company data including:
- **5,490 companies** across 45 batches (Summer 2005 - Winter 2025)
- Company info: name, description, website, logo
- Classification: batch, industry, status, stage
- Metadata: founders, team size, tags, regions
- Flags: hiring status, top company designation
- Semantic search with vector embeddings

## Quick Start

### 1. Install Dependencies

```bash
pip install supabase flask flask-cors
```

Or update all dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure Supabase

Make sure your `.env` file has Supabase credentials:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key  # For embeddings (optional)
```

### 3. Run Database Migration

Apply the migration to create the `yc_companies` table:

```bash
# If using Supabase CLI
supabase db push

# Or manually run the migration SQL in Supabase dashboard:
# bi-hub-frontend/supabase/migrations/20251016100000_add_yc_companies.sql
```

### 4. Fetch and Import Data

```bash
# Fetch data (cached locally)
python3 scripts/yc_companies_extractor.py --analyze

# Upload to Supabase (without embeddings)
python3 scripts/yc_companies_extractor.py --upload

# Upload with semantic search embeddings (takes longer)
python3 scripts/yc_companies_extractor.py --upload --embeddings
```

### 5. Enable MCP Server (Optional)

To access YC companies data in Claude Desktop:

```bash
python3 enable_yc_companies_mcp.py
```

Then restart Claude Desktop.

## Usage

### Python Script (Direct)

```python
from scripts.yc_companies_extractor import YCCompaniesExtractor

extractor = YCCompaniesExtractor()

# Fetch companies
companies = extractor.fetch_companies()

# Analyze dataset
extractor.analyze_dataset(companies)

# Upload to Supabase
extractor.insert_to_supabase(companies, generate_embeddings=True)
```

### API Server

Start the API server:

```bash
python3 api_server.py
```

Available endpoints:

#### Get Companies (with filters)
```bash
# All companies
curl "http://localhost:5001/api/yc-companies?limit=10"

# Search by name
curl "http://localhost:5001/api/yc-companies?q=stripe"

# Filter by batch
curl "http://localhost:5001/api/yc-companies?batch=W21"

# Filter by industry
curl "http://localhost:5001/api/yc-companies?industry=Fintech"

# Only hiring companies
curl "http://localhost:5001/api/yc-companies?is_hiring=true"

# Only top companies
curl "http://localhost:5001/api/yc-companies?top_company=true"
```

#### Get Company Details
```bash
curl "http://localhost:5001/api/yc-companies/stripe"
```

#### Get Statistics
```bash
curl "http://localhost:5001/api/yc-companies/stats/overview"
```

#### Get Batches
```bash
curl "http://localhost:5001/api/yc-companies/batches"
```

#### Get Industries
```bash
curl "http://localhost:5001/api/yc-companies/industries"
```

#### Semantic Search (requires embeddings)
```bash
curl "http://localhost:5001/api/yc-companies/search/semantic?q=AI+companies+in+healthcare"
```

### MCP Server (Claude Desktop)

Once enabled, you can use these commands in Claude Desktop:

#### Resources
- `yc://stats` - Get YC companies statistics
- `yc://recent` - View recently added companies
- `yc://hiring` - View companies currently hiring

#### Tools
- `search_companies` - Search with filters
- `get_company_by_slug` - Get company details
- `get_companies_by_batch` - Companies from specific batch
- `get_companies_by_industry` - Companies in industry
- `get_top_companies` - YC top companies
- `get_batches` - List all batches
- `get_industries` - List all industries
- `search_similar_companies` - Semantic search

Example queries:
```
"Show me YC companies that are hiring in AI"
"Find YC companies from W21 batch"
"What are the top YC companies?"
"Search for companies similar to Stripe"
```

## Data Structure

### Database Schema

```sql
CREATE TABLE yc_companies (
  id uuid PRIMARY KEY,
  yc_id integer UNIQUE NOT NULL,
  name text NOT NULL,
  slug text UNIQUE NOT NULL,
  one_liner text NOT NULL,
  long_description text,
  batch text NOT NULL,
  status text NOT NULL,
  industry text,
  team_size integer,
  is_hiring boolean,
  top_company boolean,
  website text,
  logo_url text,
  tags text[],
  regions text[],
  embedding vector(1536),  -- For semantic search
  created_at timestamptz,
  updated_at timestamptz
);
```

### Available Filters

- **batch**: YC batch (e.g., "W21", "S20", "F25")
- **industry**: Industry category (B2B, Healthcare, Fintech, etc.)
- **status**: Company status (Active, Acquired, Public, Inactive)
- **stage**: Company stage
- **is_hiring**: Currently hiring (true/false)
- **top_company**: Top YC company (true/false)
- **nonprofit**: Non-profit organization (true/false)

## Data Source

Data is fetched from the unofficial YC Companies API:
- API: `https://yc-oss.github.io/api/companies/all.json`
- Updated: Daily via GitHub Actions
- Maintained by: yc-oss community

## Features

### 1. Fast Search & Filtering
- Indexed database for quick queries
- Multiple filter combinations
- Full-text search on company names and descriptions

### 2. Semantic Search
- Vector embeddings using OpenAI
- Natural language queries
- Find similar companies by description

### 3. Real-time Stats
- Company counts by batch, industry, status
- Hiring trends
- Top companies analysis

### 4. MCP Integration
- Native access in Claude Desktop
- No API calls needed
- Direct database queries

## Updating Data

To refresh the data with latest YC companies:

```bash
# Force refresh from API
python3 scripts/yc_companies_extractor.py --refresh --upload
```

This will:
1. Fetch latest data from YC API
2. Update cache
3. Upsert new/updated companies to database

## File Structure

```
AI-Workspace/
├── scripts/
│   └── yc_companies_extractor.py    # Main extractor script
├── mcp_servers/
│   └── yc_companies_mcp.py          # MCP server for Claude Desktop
├── bi-hub-frontend/supabase/migrations/
│   └── 20251016100000_add_yc_companies.sql  # Database schema
├── api_server.py                     # REST API with YC endpoints
├── enable_yc_companies_mcp.py       # MCP enabler script
└── data/yc_companies/               # Local cache
    ├── all_companies.json           # Cached company data
    └── metadata.json                # Fetch metadata
```

## Troubleshooting

### "Supabase not configured"
Ensure `.env` has `SUPABASE_URL` and `SUPABASE_ANON_KEY`

### "supabase-py not installed"
Run: `pip install supabase`

### "Table does not exist"
Run the database migration first

### MCP server not appearing
1. Ensure Python path is correct in config
2. Restart Claude Desktop completely (Cmd+Q)
3. Check `~/Library/Application Support/Claude/claude_desktop_config.json`

## Examples

### Find AI Companies Hiring
```bash
curl "http://localhost:5001/api/yc-companies?industry=B2B&is_hiring=true&q=AI"
```

### Get All W21 Companies
```bash
curl "http://localhost:5001/api/yc-companies?batch=W21&limit=100"
```

### Semantic Search
```bash
curl "http://localhost:5001/api/yc-companies/search/semantic?q=developer+tools+for+startups"
```

## Performance

- **Data Fetch**: ~2 seconds (cached after first fetch)
- **Upload to Supabase**: ~2-3 minutes (5,490 companies)
- **With Embeddings**: ~20-30 minutes (OpenAI API calls)
- **API Response**: <100ms (indexed queries)
- **Semantic Search**: ~200-300ms

## Next Steps

1. Build frontend UI in bi-hub-frontend
2. Add more filters (team size, regions)
3. Track company updates over time
4. Add founder information
5. Integration with job boards

## Support

For issues or questions:
- Check logs in terminal output
- Verify Supabase connection
- Ensure all migrations are applied
- Test with sample queries first
