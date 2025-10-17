# Y Combinator Companies Data Enrichment System

**Version 1.0.0** - Multi-phase enrichment pipeline for 5,490+ YC companies

## Overview

This system enriches Y Combinator company data across 5 phases, adding 10 categories of intelligence:

### Phase 1 (Implemented ✅): Free Public Data
- **Web Data**: Website status, SSL, domain age, social links, security headers
- **Geographic Data**: (Coming soon) Location, timezone, startup density

### Phase 2-5 (Planned):
- Phase 2: Founder intelligence & funding data
- Phase 3: Competitive intelligence & hiring data
- Phase 4: Customer reviews & technical data
- Phase 5: AI insights & network analysis

## Quick Start

### Test on 10 Companies
```bash
cd /Users/yourox/AI-Workspace/scripts/enrichment/yc
python3 enrichment_coordinator.py test
```

### Run Phase 1 on All 5,490 Companies (~2.8 hours)
```bash
python3 enrichment_coordinator.py phase1
```

### Run with Custom Settings
```bash
# Limit to 100 companies
python3 enrichment_coordinator.py phase1 --limit 100

# Use 10 parallel workers (faster)
python3 enrichment_coordinator.py phase1 --workers 10

# Force re-enrichment (ignore cache)
python3 enrichment_coordinator.py phase1 --force
```

### Check Statistics
```bash
python3 enrichment_coordinator.py stats
```

## Data Enriched

Each company gets enriched with:

### 1. Website Status
- HTTP status code
- Response time (ms)
- Redirect information
- Reachability

### 2. SSL Security
- Certificate validity
- Issuer information
- Expiration date
- Days until expiry

### 3. Domain Information (WHOIS)
- Domain registrar
- Creation date
- Expiration date
- **Domain age** (days & years)
- Name servers

### 4. Social Media Links
Automatically extracted from website:
- Twitter/X
- LinkedIn
- GitHub
- Facebook
- Instagram
- YouTube

### 5. Security Headers Analysis
- Strict-Transport-Security (HSTS)
- Content-Security-Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy
- **Security score (0-100)**

## Output Structure

Enriched data saved to: `/Users/yourox/AI-Workspace/data/yc_enriched/`

### File Format: `{slug}_enriched.json`

```json
{
  "slug": "circuithub",
  "name": "CircuitHub",
  "yc_id": 5,
  "batch": "Winter 2012",
  "website": "https://circuithub.com",
  "web_data": {
    "website_status": {
      "reachable": true,
      "status_code": 200,
      "response_time_ms": 581.68
    },
    "domain_info": {
      "domain_age_years": 17.5,
      "registrar": "Amazon Registrar, Inc."
    },
    "social_links": {
      "twitter": "https://twitter.com/circuithub",
      "linkedin": "https://www.linkedin.com/company/circuithub"
    },
    "security_headers": {
      "security_score": 16
    }
  },
  "enrichment_version": "1.0.0",
  "enriched_at": "2025-10-17T00:23:45",
  "phase1_complete": true
}
```

## Performance

**Tested on 10 companies:**
- Time: 18.6 seconds
- Rate: 0.54 companies/second
- Errors: 0

**Estimated for all 5,490 companies:**
- Time: ~2.8 hours
- With 10 workers: ~1.5 hours

## Architecture

### Directory Structure
```
scripts/enrichment/yc/
├── __init__.py
├── enrichment_coordinator.py    # Main orchestrator
├── web_data_enricher.py          # Phase 1: Web enrichment
└── README.md                     # This file

data/yc_enriched/                 # Output directory
├── {slug}_enriched.json          # One file per company
└── ...
```

### Enrichment Flow
1. **Load** all companies from `/data/yc_companies/all_companies.json`
2. **Check cache** - skip already enriched (unless `--force`)
3. **Enrich** in parallel batches with rate limiting
4. **Save** to individual JSON files
5. **Report** statistics and completion

### Features
- ✅ **Parallel processing** with ThreadPoolExecutor
- ✅ **Rate limiting** to avoid overwhelming servers
- ✅ **Caching** - only enriches new/changed companies
- ✅ **Error handling** - continues on failures
- ✅ **Progress tracking** - real-time updates
- ✅ **Versioning** - tracks enrichment version

## Dependencies

```bash
pip3 install requests beautifulsoup4 python-whois
```

All dependencies are already installed.

## Usage Examples

### Example 1: Enrich First 100 Companies
```bash
python3 enrichment_coordinator.py phase1 --limit 100
```

### Example 2: Fast Enrichment (10 Workers)
```bash
python3 enrichment_coordinator.py phase1 --workers 10
```

### Example 3: Re-enrich All Companies
```bash
python3 enrichment_coordinator.py phase1 --force
```

### Example 4: Check Progress
```bash
python3 enrichment_coordinator.py stats
```

Output:
```
📊 YC COMPANIES ENRICHMENT STATISTICS
======================================================================
total_companies               : 5,490
total_enriched               : 10
phase1_complete              : 10
with_website                 : 10
with_social_links            : 9
with_domain_info             : 10
```

## Next Steps

1. **Run Phase 1** on all 5,490 companies (~2.8 hours)
2. **Add to Supabase** (database migration + upload script)
3. **Implement Phase 2** (Founders + Funding)
4. **Add MCP tools** for enriched data search
5. **Build dashboard** to visualize enrichment data

## API

### Python Usage

```python
from enrichment_coordinator import YCEnrichmentCoordinator

# Initialize
coordinator = YCEnrichmentCoordinator()

# Enrich all companies
coordinator.enrich_all_phase1(workers=10)

# Get statistics
stats = coordinator.get_enrichment_stats()
print(f"Enriched {stats['phase1_complete']} companies")
```

## Troubleshooting

### SSL Verification Errors
Some companies may have SSL verification issues. This is expected and logged as warnings. The enrichment continues with other data.

### WHOIS Lookup Failures
Some domains may not respond to WHOIS queries. This is normal and the enrichment continues.

### Rate Limiting
If you encounter rate limiting, reduce `--workers` or increase the rate limit delay in the code.

## Cost

**Phase 1: $0** - Uses only free/public APIs:
- HTTP requests
- WHOIS lookups
- SSL certificate checks
- HTML parsing

**Future Phases:** See main enrichment plan for cost estimates.

---

Built with ❤️  for comprehensive YC company intelligence
