# YC Companies Enrichment Setup Guide

## Quick Start

### 1. Add API Keys to `.env`

Copy the example and add your keys:

```bash
cp /Users/yourox/AI-Workspace/.env.example /Users/yourox/AI-Workspace/.env
```

Then edit `.env` and add your keys (see instructions below).

---

## API Key Setup Instructions

### Required: OpenAI API Key (Already configured ✓)
- Used for: AI insights enrichment (Phase 8)
- Cost: ~$5 for all 5,490 companies

---

### Optional: Google Maps API Key (Recommended for Phase 2)

**Without API key:** Uses free Nominatim (OpenStreetMap) - basic lat/lng only
**With API key:** Google Places data - ratings, phone, timezone, business hours, etc.

#### Setup Steps:

1. **Get API Key:**
   - Go to: https://console.cloud.google.com/google/maps-apis
   - Create project (or select existing)
   - Enable billing (free tier: 28,000 requests/month = $0 for us)
   - Go to "Credentials" → "Create Credentials" → "API Key"

2. **Enable Required APIs:**
   - Places API (New): https://console.cloud.google.com/apis/library/places-backend.googleapis.com
   - Geocoding API: https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com
   - Time Zone API: https://console.cloud.google.com/apis/library/timezone-backend.googleapis.com

3. **Add to `.env`:**
   ```bash
   GOOGLE_MAPS_API_KEY=AIzaSyC...your_key_here
   ```

**Cost:** FREE (5,490 companies well under 28K/month free tier)

---

### Optional: GitHub Token (Recommended for Phase 3)

**Without token:** 60 requests/hour (not enough - will take days)
**With token:** 5,000 requests/hour (completes in ~1 hour)

#### Setup Steps:

1. **Generate Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes:
     - `public_repo` (read public repository data)
     - `read:org` (read organization data)
   - Click "Generate token"
   - **Copy the token immediately** (you can't see it again!)

2. **Add to `.env`:**
   ```bash
   GITHUB_TOKEN=ghp_your_token_here
   ```

**Cost:** FREE

---

## Running Enrichment

### Test First (Recommended)

Test all enrichers on 3 sample companies:

```bash
cd /Users/yourox/AI-Workspace/scripts/enrichment/yc
python3 enrichment_coordinator.py test-all
```

### Run All Enrichments

Run all phases (2-8) on all 5,490 companies:

```bash
python3 enrichment_coordinator.py run-all
```

Or run individual phases:

```bash
# Phase 2: Geographic data (~1 hour)
python3 enrichment_coordinator.py phase2

# Phase 3: GitHub/Technical data (~1 hour with token)
python3 enrichment_coordinator.py phase3

# Phase 4: Network/Relationships (~30 mins)
python3 enrichment_coordinator.py phase4

# Phase 5: Patents/IP (~1 hour)
python3 enrichment_coordinator.py phase5

# Phase 6: Customer reviews (~3 hours)
python3 enrichment_coordinator.py phase6

# Phase 7: Hiring/Talent data (~3 hours)
python3 enrichment_coordinator.py phase7

# Phase 8: AI insights (~2 hours, costs $5)
python3 enrichment_coordinator.py phase8
```

---

## Summary

| Phase | Data Source | API Key Required? | Cost | Time |
|-------|-------------|-------------------|------|------|
| 1 ✅ | Web data | None | $0 | Done (1.2 hrs) |
| 2 | Geographic | Optional (Google) | $0 | ~1 hour |
| 3 | GitHub/Tech | Optional (GitHub) | $0 | ~1 hour |
| 4 | Network | None | $0 | ~30 mins |
| 5 | Patents/IP | None | $0 | ~1 hour |
| 6 | Reviews | None | $0 | ~3 hours |
| 7 | Hiring | None | $0 | ~3 hours |
| 8 | AI Insights | OpenAI ✓ | $5 | ~2 hours |

**Total Time:** ~10-12 hours
**Total Cost:** $5

**Recommendation:** Get Google Maps API key and GitHub token for best results!

---

## Checking Your Setup

Run this to verify your API keys:

```bash
cd /Users/yourox/AI-Workspace/scripts/enrichment/yc
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('/Users/yourox/AI-Workspace/.env')

print('API Key Status:')
print('✓ OpenAI API Key:', 'Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing')
print('✓ Google Maps API Key:', 'Set' if os.getenv('GOOGLE_MAPS_API_KEY') else '⚠️  Optional (using free fallback)')
print('✓ GitHub Token:', 'Set' if os.getenv('GITHUB_TOKEN') else '⚠️  Optional (60 req/hr limit)')
"
```

---

## Need Help?

- Google Maps API: https://developers.google.com/maps/documentation/places/web-service/get-api-key
- GitHub Token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- Issues: File at https://github.com/anthropics/claude-code/issues
