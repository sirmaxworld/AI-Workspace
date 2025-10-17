#!/usr/bin/env python3
"""
Verify YC Enrichment Completion and Database Transfer Readiness
================================================================
Validates all enriched data and generates manifest for postgres + pgvector + mem0 migration
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnrichmentVerifier:
    """Verify enrichment completion and prepare for database migration"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.enriched_dir = self.workspace_dir / "data" / "yc_enriched"
        self.companies_file = self.workspace_dir / "data" / "yc_companies" / "all_companies.json"
        self.output_dir = self.workspace_dir / "data" / "migration_ready"
        self.output_dir.mkdir(exist_ok=True)

        self.stats = {
            "total_files": 0,
            "phase8_complete": 0,
            "phase8_incomplete": 0,
            "invalid_json": 0,
            "missing_required_fields": 0,
            "models_used": Counter(),
            "phases_complete": {f"phase{i}_complete": 0 for i in range(1, 9)}
        }

        self.required_fields = [
            "slug", "name", "yc_id", "batch", "website",
            "ai_insights", "enrichment_version", "enriched_at"
        ]

        self.ai_insights_schema = [
            "market_analysis", "competitive_positioning", "business_model",
            "growth_assessment", "risk_analysis", "investment_thesis",
            "recommendations"
        ]

    def load_all_companies(self) -> Dict[str, Dict]:
        """Load source company data"""
        with open(self.companies_file, 'r') as f:
            companies = json.load(f)
        return {c['slug']: c for c in companies}

    def validate_file(self, file_path: Path) -> Dict:
        """Validate a single enriched file"""
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "slug": None,
            "phase8_complete": False,
            "model_used": None
        }

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            result["slug"] = data.get("slug", "unknown")

            # Check required fields
            missing_fields = [f for f in self.required_fields if f not in data]
            if missing_fields:
                result["errors"].append(f"Missing required fields: {missing_fields}")
                result["valid"] = False

            # Check phase8 completion
            result["phase8_complete"] = data.get("phase8_complete", False)

            # Validate AI insights structure
            if "ai_insights" in data:
                ai_insights = data["ai_insights"]
                result["model_used"] = ai_insights.get("model_used", "unknown")

                if ai_insights.get("status") != "success":
                    result["warnings"].append(f"AI insights status: {ai_insights.get('status')}")

                missing_insights = [f for f in self.ai_insights_schema if f not in ai_insights]
                if missing_insights:
                    result["warnings"].append(f"Missing AI insight sections: {missing_insights}")

            # Check all phases
            for i in range(1, 9):
                phase_key = f"phase{i}_complete"
                if data.get(phase_key, False):
                    self.stats["phases_complete"][phase_key] += 1

        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"Invalid JSON: {str(e)}")
            self.stats["invalid_json"] += 1
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")

        return result

    def verify_all(self) -> Dict:
        """Verify all enriched files"""
        logger.info("Starting enrichment verification...")

        all_companies = self.load_all_companies()
        enriched_files = list(self.enriched_dir.glob("*_enriched.json"))

        self.stats["total_files"] = len(enriched_files)

        ready_for_migration = []
        failed_validation = []
        incomplete_enrichment = []

        for file_path in enriched_files:
            validation = self.validate_file(file_path)

            if validation["valid"]:
                if validation["phase8_complete"]:
                    ready_for_migration.append({
                        "slug": validation["slug"],
                        "file": str(file_path),
                        "model_used": validation["model_used"]
                    })
                    self.stats["phase8_complete"] += 1
                    if validation["model_used"]:
                        self.stats["models_used"][validation["model_used"]] += 1
                else:
                    incomplete_enrichment.append({
                        "slug": validation["slug"],
                        "file": str(file_path),
                        "warnings": validation["warnings"]
                    })
                    self.stats["phase8_incomplete"] += 1
            else:
                failed_validation.append({
                    "slug": validation["slug"],
                    "file": str(file_path),
                    "errors": validation["errors"]
                })
                if validation["errors"]:
                    self.stats["missing_required_fields"] += 1

        return {
            "ready_for_migration": ready_for_migration,
            "incomplete_enrichment": incomplete_enrichment,
            "failed_validation": failed_validation
        }

    def generate_manifest(self, verification_results: Dict):
        """Generate migration manifest"""
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "source_directory": str(self.enriched_dir),
            "target_architecture": "postgres + pgvector + mem0",
            "statistics": {
                "total_companies": self.stats["total_files"],
                "ready_for_migration": self.stats["phase8_complete"],
                "incomplete": self.stats["phase8_incomplete"],
                "failed": self.stats["invalid_json"] + self.stats["missing_required_fields"],
                "success_rate": f"{(self.stats['phase8_complete'] / self.stats['total_files'] * 100):.2f}%"
            },
            "models_used": dict(self.stats["models_used"]),
            "phase_completion": self.stats["phases_complete"],
            "companies": verification_results["ready_for_migration"]
        }

        manifest_file = self.output_dir / "migration_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"✓ Manifest saved to: {manifest_file}")
        return manifest

    def generate_schema_documentation(self):
        """Generate schema documentation for database migration"""
        schema_doc = {
            "database_architecture": {
                "database": "PostgreSQL",
                "vector_extension": "pgvector",
                "memory_system": "mem0 (local)",
                "purpose": "YC company enrichment data with vector embeddings for semantic search"
            },
            "tables": {
                "companies": {
                    "description": "Core company information from Y Combinator",
                    "primary_key": "slug",
                    "fields": {
                        "slug": "TEXT PRIMARY KEY",
                        "name": "TEXT NOT NULL",
                        "yc_id": "INTEGER",
                        "batch": "TEXT",
                        "website": "TEXT",
                        "one_liner": "TEXT",
                        "long_description": "TEXT",
                        "industry": "TEXT",
                        "team_size": "INTEGER",
                        "status": "TEXT",
                        "enrichment_version": "TEXT",
                        "enriched_at": "TIMESTAMP"
                    }
                },
                "web_data": {
                    "description": "Web enrichment data (Phase 1)",
                    "foreign_key": "company_slug -> companies.slug",
                    "fields": {
                        "company_slug": "TEXT REFERENCES companies(slug)",
                        "website_status": "JSONB",
                        "domain_info": "JSONB",
                        "social_links": "JSONB",
                        "security_headers": "JSONB",
                        "enriched_at": "TIMESTAMP"
                    }
                },
                "github_data": {
                    "description": "GitHub enrichment data (Phase 2-4)",
                    "foreign_key": "company_slug -> companies.slug",
                    "fields": {
                        "company_slug": "TEXT REFERENCES companies(slug)",
                        "repositories": "JSONB",
                        "total_stars": "INTEGER",
                        "total_repos": "INTEGER",
                        "enriched_at": "TIMESTAMP"
                    }
                },
                "ai_insights": {
                    "description": "AI-generated strategic insights (Phase 8)",
                    "foreign_key": "company_slug -> companies.slug",
                    "fields": {
                        "company_slug": "TEXT REFERENCES companies(slug)",
                        "model_used": "TEXT",
                        "market_analysis": "JSONB",
                        "competitive_positioning": "JSONB",
                        "business_model": "JSONB",
                        "growth_assessment": "JSONB",
                        "risk_analysis": "JSONB",
                        "investment_thesis": "JSONB",
                        "recommendations": "JSONB",
                        "tokens_used": "JSONB",
                        "enriched_at": "TIMESTAMP"
                    }
                },
                "company_embeddings": {
                    "description": "Vector embeddings for semantic search",
                    "extension_required": "pgvector",
                    "fields": {
                        "company_slug": "TEXT REFERENCES companies(slug)",
                        "embedding_type": "TEXT (description/insights/combined)",
                        "embedding": "vector(1536)",
                        "model_used": "TEXT",
                        "created_at": "TIMESTAMP"
                    },
                    "indexes": [
                        "CREATE INDEX ON company_embeddings USING ivfflat (embedding vector_cosine_ops)"
                    ]
                }
            },
            "data_format": {
                "source_files": "*_enriched.json",
                "structure": {
                    "root_level": ["slug", "name", "yc_id", "batch", "website"],
                    "web_data": "JSONB nested object",
                    "github_data": "JSONB nested object",
                    "ai_insights": "JSONB nested object with 7 sections"
                }
            },
            "migration_notes": {
                "embedding_generation": "Use OpenAI text-embedding-3-small for company descriptions and AI insights",
                "mem0_integration": "Store conversation history and user preferences locally",
                "vector_search": "Enable similarity search across company descriptions and insights",
                "indexing_strategy": "Use IVFFlat index for vector columns (rebuild after bulk insert)"
            }
        }

        schema_file = self.output_dir / "database_schema.json"
        with open(schema_file, 'w') as f:
            json.dump(schema_doc, f, indent=2)

        logger.info(f"✓ Schema documentation saved to: {schema_file}")
        return schema_doc

    def generate_migration_guide(self):
        """Generate step-by-step migration guide"""
        guide = """# YC Enrichment Data Migration Guide
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

"""

        guide_file = self.output_dir / "MIGRATION_GUIDE.md"
        with open(guide_file, 'w') as f:
            f.write(guide)

        logger.info(f"✓ Migration guide saved to: {guide_file}")

    def run(self):
        """Run complete verification"""
        logger.info("\n" + "="*70)
        logger.info("YC ENRICHMENT VERIFICATION & MIGRATION PREP")
        logger.info("="*70 + "\n")

        # Verify all files
        verification_results = self.verify_all()

        # Generate manifest
        manifest = self.generate_manifest(verification_results)

        # Generate schema documentation
        self.generate_schema_documentation()

        # Generate migration guide
        self.generate_migration_guide()

        # Save detailed reports
        if verification_results["failed_validation"]:
            failed_file = self.output_dir / "failed_validation.json"
            with open(failed_file, 'w') as f:
                json.dump(verification_results["failed_validation"], f, indent=2)
            logger.info(f"✓ Failed validation report: {failed_file}")

        if verification_results["incomplete_enrichment"]:
            incomplete_file = self.output_dir / "incomplete_enrichment.json"
            with open(incomplete_file, 'w') as f:
                json.dump(verification_results["incomplete_enrichment"], f, indent=2)
            logger.info(f"✓ Incomplete enrichment report: {incomplete_file}")

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("VERIFICATION SUMMARY")
        logger.info("="*70)
        logger.info(f"Total files: {self.stats['total_files']}")
        logger.info(f"Ready for migration: {self.stats['phase8_complete']} ({self.stats['phase8_complete']/self.stats['total_files']*100:.2f}%)")
        logger.info(f"Incomplete enrichment: {self.stats['phase8_incomplete']}")
        logger.info(f"Failed validation: {self.stats['invalid_json'] + self.stats['missing_required_fields']}")
        logger.info(f"\nModels used:")
        for model, count in self.stats['models_used'].items():
            logger.info(f"  - {model}: {count} companies")
        logger.info(f"\nPhase completion:")
        for phase, count in sorted(self.stats['phases_complete'].items()):
            logger.info(f"  - {phase}: {count}/{self.stats['total_files']}")

        logger.info("\n" + "="*70)
        logger.info("MIGRATION READINESS")
        logger.info("="*70)
        logger.info(f"✅ {self.stats['phase8_complete']} companies ready for database transfer")
        logger.info(f"📊 Migration manifest: {self.output_dir / 'migration_manifest.json'}")
        logger.info(f"📋 Database schema: {self.output_dir / 'database_schema.json'}")
        logger.info(f"📖 Migration guide: {self.output_dir / 'MIGRATION_GUIDE.md'}")
        logger.info("\n⚠️  DO NOT POPULATE DATABASE YET - Architecture setup required")
        logger.info("="*70 + "\n")


if __name__ == "__main__":
    verifier = EnrichmentVerifier()
    verifier.run()
