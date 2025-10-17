# Schema Migration Guide

## Current Version: 1.0.0

### Changes Required

#### Updates Needed:
- Add schema version reference to extractor
- Import schema module in MCP server

#### Files Modified:
- /Users/yourox/AI-Workspace/docs/BUSINESS_INTELLIGENCE_SCHEMA.md


### Migration Steps

1. **Review Schema Changes**
   ```bash
   python3 schema.py
   ```

2. **Validate Existing Data**
   ```bash
   python3 schema_sync.py --validate
   ```

3. **Update Extractor**
   - Import schema module
   - Use `get_extraction_prompt()` for prompts
   - Update category extraction logic

4. **Update MCP Server**
   - Import schema module
   - Use `get_mcp_tool_schema()` for tool definitions
   - Update data loading logic

5. **Run Full Sync**
   ```bash
   python3 schema_sync.py --full-sync
   ```

6. **Test Everything**
   ```bash
   python3 test_server.py
   ```
