# YC Enrichment Data Migration Guide
## Target: PostgreSQL + pgvector + mem0

### Prerequisites
```bash
# Install PostgreSQL with pgvector extension
brew install postgresql@15
brew install pgvector

# Install Python dependencies
pip install psycopg2-binary pgvector mem0ai openai
```

### Step 1: Database Setup
```sql
-- Create database
CREATE DATABASE yc_enrichment;

-- Enable pgvector extension
CREATE EXTENSION vector;

-- Create tables (see database_schema.json for full schema)
CREATE TABLE companies (
    slug TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    yc_id INTEGER,
    batch TEXT,
    website TEXT,
    -- ... (see schema)
);

CREATE TABLE ai_insights (
    company_slug TEXT REFERENCES companies(slug),
    model_used TEXT,
    market_analysis JSONB,
    -- ... (see schema)
);

CREATE TABLE company_embeddings (
    company_slug TEXT REFERENCES companies(slug),
    embedding_type TEXT,
    embedding vector(1536),
    model_used TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_companies_batch ON companies(batch);
CREATE INDEX idx_ai_insights_model ON ai_insights(model_used);
CREATE INDEX ON company_embeddings USING ivfflat (embedding vector_cosine_ops);
```

### Step 2: Data Migration
```python
# Use migration_manifest.json to load all ready companies
# Parse JSON files and insert into PostgreSQL
# Generate embeddings for descriptions and insights
# Store embeddings in company_embeddings table
```

### Step 3: mem0 Setup
```python
from mem0 import Memory

# Initialize local mem0
config = {
    "vector_store": {
        "provider": "pgvector",
        "config": {
            "host": "localhost",
            "port": 5432,
            "database": "yc_enrichment",
            "user": "yourox",
            "password": "your_password"
        }
    }
}

memory = Memory.from_config(config)
```

### Step 4: Vector Search Setup
```python
# Query similar companies
query_embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input="AI-powered legal tech startups"
).data[0].embedding

# Find similar companies
cursor.execute('''
    SELECT company_slug,
           1 - (embedding <=> %s::vector) as similarity
    FROM company_embeddings
    WHERE embedding_type = 'combined'
    ORDER BY embedding <=> %s::vector
    LIMIT 10
''', (query_embedding, query_embedding))
```

### Migration Checklist
- [ ] PostgreSQL 15+ installed with pgvector extension
- [ ] Database and tables created
- [ ] Indexes created (but not built yet for performance)
- [ ] Python migration script prepared
- [ ] Test migration with 10 companies
- [ ] Full migration of all 5,405 companies
- [ ] Generate embeddings for all companies
- [ ] Build vector indexes after bulk insert
- [ ] Configure mem0 with pgvector backend
- [ ] Test vector similarity search
- [ ] Verify data integrity

### Performance Optimization
- Use COPY command for bulk inserts (much faster than INSERT)
- Create indexes AFTER bulk data load
- Use connection pooling for embedding generation
- Batch embedding generation (100 companies at a time)

### Cost Estimate
- Embeddings: 5,405 companies × 2 embeddings (description + insights) = 10,810 embeddings
- Using text-embedding-3-small: ~$0.02 per 1M tokens
- Estimated total: ~$0.50 for all embeddings

