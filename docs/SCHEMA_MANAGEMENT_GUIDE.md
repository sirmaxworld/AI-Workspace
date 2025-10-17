# Business Intelligence Schema Management Guide

**Version:** 1.0.0
**Last Updated:** October 15, 2025

---

## 🎯 Overview

This guide explains how the Business Intelligence system maintains data consistency across:
1. **AI Extraction** (`business_intelligence_extractor.py`)
2. **MCP Server** (`server.py`)
3. **Documentation** (Auto-generated)

**Key Principle:** Schema is the single source of truth. All components auto-sync from it.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     schema.py                                │
│              (SINGLE SOURCE OF TRUTH)                        │
│                                                              │
│  - Data structure definitions                                │
│  - Field specifications                                      │
│  - Enum values (categories, sentiments, etc.)               │
│  - Validation rules                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌───────────┐  ┌──────────┐  ┌──────────────┐
│ Extractor │  │   MCP    │  │     Docs     │
│           │  │  Server  │  │ (Generated)  │
│  Uses:    │  │          │  │              │
│  schema   │  │  Uses:   │  │  Uses:       │
│  for AI   │  │  schema  │  │  schema to   │
│  prompts  │  │  for     │  │  create      │
│           │  │  queries │  │  markdown    │
└───────────┘  └──────────┘  └──────────────┘
```

---

## 🔄 How Schema Sync Works

### 1. When You ADD a New Data Category

**Example:** Adding "competitive_intelligence" category

```python
# In schema.py - ADD TO EXTRACTION_SCHEMA
"competitive_intelligence": {
    "fields": ["competitor", "strength", "weakness", "market_share"],
    "description": "Competitive intelligence analysis"
}
```

**What Happens Automatically:**
1. ✅ Extraction prompt includes new category
2. ✅ MCP server loads the new category
3. ✅ Documentation updates automatically
4. ✅ Validation accepts the new fields

**Manual Steps Required:**
1. Update extractor to extract this category
2. Add MCP tool if needed (e.g., `search_competitive_intel`)
3. Run: `python3 schema_sync.py --full-sync`

---

### 2. When You ADD a New Field

**Example:** Adding "roi" field to products_tools

```python
# In schema.py
"products_tools": {
    "fields": ["name", "category", "use_case", "sentiment",
               "pricing", "metrics", "roi"],  # <-- NEW FIELD
    ...
}
```

**What Happens Automatically:**
1. ✅ Validation accepts new field
2. ✅ Extraction prompt includes it
3. ✅ Backward compatible (old data still valid)

**Manual Steps:**
1. Update extractor AI prompt to extract "roi"
2. Run: `python3 schema_sync.py --full-sync`

---

### 3. When You CHANGE Enum Values

**Example:** Adding new category "ml-platform"

```python
# In schema.py
"products_tools": {
    "categories": ["saas", "ai-tool", ..., "ml-platform"],  # <-- NEW
    ...
}
```

**What Happens Automatically:**
1. ✅ MCP tools accept new category in filters
2. ✅ Validation allows new category
3. ✅ Documentation updates

**Manual Steps:**
1. None! Schema is flexible
2. Run: `python3 schema_sync.py --full-sync` to verify

---

## 🛠️ Tools & Commands

### Schema Sync Manager

```bash
# Full sync (recommended)
python3 schema_sync.py --full-sync

# Validate existing data only
python3 schema_sync.py --validate

# Check if extractor is in sync
python3 schema_sync.py --check-extractor

# Check if MCP server is in sync
python3 schema_sync.py --check-mcp

# Generate documentation only
python3 schema_sync.py --docs
```

### Schema Module Functions

```python
from schema import (
    SCHEMA_VERSION,
    EXTRACTION_SCHEMA,
    MCP_TOOL_MAPPINGS,
    validate_data_structure,
    get_extraction_prompt,
    get_mcp_tool_schema,
    export_schema_markdown
)

# Validate extracted data
with open('video_insights.json') as f:
    data = json.load(f)

report = validate_data_structure(data)
if report['valid']:
    print("✅ Data is valid")
else:
    print(f"❌ Errors: {report['errors']}")

# Get extraction prompt (always in sync)
prompt = get_extraction_prompt()

# Get MCP tool schema (always in sync)
tool_schema = get_mcp_tool_schema("search_products")

# Export schema documentation
markdown = export_schema_markdown()
```

---

## ✅ Workflow: Adding New Data Type

### Step 1: Update Schema

```python
# In schema.py
EXTRACTION_SCHEMA["new_category"] = {
    "fields": ["field1", "field2", "field3"],
    "description": "Description of new category"
}
```

### Step 2: Run Sync Check

```bash
python3 schema_sync.py --full-sync
```

This will:
- ✅ Validate backward compatibility
- ✅ Generate updated documentation
- ✅ Check all components
- ⚠️  Show what needs manual updating

### Step 3: Update Extractor (if needed)

```python
# In business_intelligence_extractor.py
# The prompt is auto-generated from schema, but you may need
# to add extraction logic for complex nested structures
```

### Step 4: Update MCP Server (if needed)

```python
# In server.py
# Add data loading in __init__:
def _extract_new_category(self, data: dict, meta: dict):
    for item in data.get('new_category', []):
        self.all_data['new_category'].append({**item, **meta})

# Call it in load_all_insights():
self._extract_new_category(data, meta)
```

### Step 5: Add MCP Tool (optional)

```python
# In schema.py - MCP_TOOL_MAPPINGS
"search_new_category": {
    "data_category": "new_category",
    "filter_fields": [],
    "search_fields": ["field1", "field2"],
    "description": "Search new category data"
}

# In server.py - Add @server.list_tools() entry
# In server.py - Add @server.call_tool() handler
```

### Step 6: Test Everything

```bash
# Test MCP server
python3 test_server.py

# Validate existing data
python3 schema_sync.py --validate

# Test extraction
python3 business_intelligence_extractor.py VIDEO_ID
```

---

## 🚨 Breaking Changes Detection

The system automatically detects breaking changes:

### ❌ Breaking Changes

1. **Removing a field**
   ```python
   # BEFORE
   "fields": ["name", "category", "use_case"]

   # AFTER (BREAKING!)
   "fields": ["name", "category"]  # <-- removed "use_case"
   ```

2. **Removing a category**
   ```python
   # BEFORE
   EXTRACTION_SCHEMA["old_category"] = {...}

   # AFTER (BREAKING!)
   # Deleted entirely
   ```

3. **Changing field types** (requires data migration)

### ✅ Non-Breaking Changes

1. **Adding new fields** (backward compatible)
2. **Adding new enum values** (backward compatible)
3. **Adding new categories** (backward compatible)
4. **Relaxing validation** (backward compatible)

---

## 🔒 Pre-Commit Hook (Automatic Validation)

Install the pre-commit hook to auto-check schema changes:

```bash
# Link the hook
ln -s /Users/yourox/AI-Workspace/mcp-servers/business-intelligence/pre_commit_schema_check.sh \
      .git/hooks/pre-commit

# Now every commit with schema changes triggers validation!
```

**What it does:**
- Detects changes to `schema.py`, `business_intelligence_extractor.py`, or `server.py`
- Runs `schema_sync.py --full-sync`
- Warns about breaking changes
- Prevents commit if validation fails

---

## 📊 Schema Version Management

### Current Version: 1.0.0

```python
# In schema.py
SCHEMA_VERSION = "1.0.0"
LAST_UPDATED = "2025-10-15"
```

### Version Increment Rules

- **Patch (1.0.X)**: Non-breaking changes (new fields, new categories)
- **Minor (1.X.0)**: New features (new MCP tools, major categories)
- **Major (X.0.0)**: Breaking changes (removed fields, changed types)

### Migration Between Versions

```bash
# Check what changed
python3 -c "from schema import detect_schema_changes; \
            print(detect_schema_changes('0.9.0'))"

# Generate migration guide
python3 schema_sync.py --full-sync
cat docs/SCHEMA_MIGRATION_GUIDE.md
```

---

## 🎓 Best Practices

### 1. Always Run Sync After Schema Changes

```bash
# After editing schema.py:
python3 schema_sync.py --full-sync
```

### 2. Use Soft Validation for Enums

The schema uses **soft validation** for enum fields:
- Suggested values in schema (for documentation)
- But allows ANY string value (for flexibility)
- This prevents breaking when AI extracts unexpected categories

```python
# Schema suggests these categories:
"categories": ["saas", "ai-tool", "platform"]

# But also accepts:
"category": "automation-platform"  # ✅ Valid!
"category": "ml-tool"              # ✅ Valid!
```

### 3. Keep Schema Simple

```python
# ✅ GOOD: Simple, clear fields
"fields": ["name", "category", "description"]

# ❌ BAD: Overly complex nested structures
"fields": {
    "name": {"type": "string", "max_length": 100},
    "metadata": {
        "created": {"type": "datetime"},
        ...
    }
}
```

### 4. Document WHY, Not Just WHAT

```python
# ✅ GOOD
"description": "Products mentioned with sentiment analysis (for recommendation filtering)"

# ❌ BAD
"description": "Products and tools"
```

### 5. Test with Real Data

```bash
# Always validate against existing data
python3 schema_sync.py --validate

# Test extraction with real video
python3 business_intelligence_extractor.py VIDEO_ID

# Test MCP server
python3 test_server.py
```

---

## 🐛 Troubleshooting

### Issue: "Schema validation failed"

```bash
# Check what's wrong
python3 schema_sync.py --full-sync

# Look at detailed errors
python3 -c "from schema import validate_data_structure; \
            import json; \
            data = json.load(open('data/business_insights/VIDEO_ID_insights.json')); \
            report = validate_data_structure(data); \
            print(json.dumps(report, indent=2))"
```

### Issue: "MCP server not loading new category"

1. Check schema has the category:
   ```bash
   python3 -c "from schema import EXTRACTION_SCHEMA; \
               print(list(EXTRACTION_SCHEMA.keys()))"
   ```

2. Check MCP server is importing schema:
   ```bash
   grep "from schema import" server.py
   ```

3. Check data loading function exists:
   ```bash
   grep "_extract_YOUR_CATEGORY" server.py
   ```

### Issue: "Extractor not extracting new field"

1. Check if field is in schema:
   ```bash
   python3 -c "from schema import EXTRACTION_SCHEMA; \
               print(EXTRACTION_SCHEMA['category_name']['fields'])"
   ```

2. Check if AI prompt includes it:
   ```bash
   python3 -c "from schema import get_extraction_prompt; \
               prompt = get_extraction_prompt(); \
               print('YOUR_FIELD' in prompt)"
   ```

3. Update extractor to use schema-generated prompt

---

## 📈 Monitoring Schema Health

### Weekly Health Check

```bash
# Validate all data
python3 schema_sync.py --validate

# Check sync status
python3 schema_sync.py --full-sync

# Review warnings
grep "⚠️" docs/SCHEMA_MIGRATION_GUIDE.md
```

### Metrics to Track

```bash
# Total data files
ls -1 data/business_insights/*_insights.json | wc -l

# Valid files
python3 schema_sync.py --validate | grep "✅ Valid:"

# Schema categories
python3 -c "from schema import EXTRACTION_SCHEMA; \
            print(f'Categories: {len(EXTRACTION_SCHEMA)}')"

# MCP tools
python3 -c "from schema import MCP_TOOL_MAPPINGS; \
            print(f'Tools: {len(MCP_TOOL_MAPPINGS)}')"
```

---

## 🎯 Summary

### ✅ What Happens Automatically

- Extraction prompts stay in sync with schema
- MCP tool schemas stay in sync
- Documentation regenerates
- Validation uses latest schema
- Backward compatibility checked

### 📝 What Requires Manual Work

- Implementing new extraction logic
- Creating new MCP tools
- Adding data loading functions
- Updating business logic

### 🔄 Recommended Workflow

1. **Change schema.py** (single source of truth)
2. **Run `schema_sync.py --full-sync`** (validate)
3. **Update components** (extractor, MCP, if needed)
4. **Test** (`test_server.py`, validate data)
5. **Commit** (pre-commit hook validates)

---

## 🚀 Next Steps

1. ✅ Schema system is installed and working
2. ✅ All existing data validates successfully
3. ✅ MCP server and extractor are in sync
4. ✅ Documentation is auto-generated

**When you want to add new data:**
1. Edit `schema.py`
2. Run `schema_sync.py --full-sync`
3. Follow the migration guide
4. Test and commit

**Your schema is now the single source of truth for the entire system!** 🎉

---

**For questions or issues, run:** `python3 schema_sync.py --full-sync`
