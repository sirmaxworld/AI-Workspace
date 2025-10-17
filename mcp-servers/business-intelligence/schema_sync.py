#!/usr/bin/env python3
"""
Schema Synchronization System
Ensures extraction, MCP server, and documentation stay in sync

Run this after making ANY schema changes to:
1. Validate schema consistency
2. Update extractor prompts
3. Update MCP server tools
4. Regenerate documentation
5. Run compatibility tests
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from schema import (
    SCHEMA_VERSION,
    EXTRACTION_SCHEMA,
    MCP_TOOL_MAPPINGS,
    validate_data_structure,
    get_extraction_prompt,
    get_mcp_tool_schema,
    export_schema_markdown
)


class SchemaSyncManager:
    """Manages schema synchronization across all components"""

    def __init__(self):
        self.workspace = Path("/Users/yourox/AI-Workspace")
        self.mcp_dir = self.workspace / "mcp-servers" / "business-intelligence"
        self.scripts_dir = self.workspace / "scripts"
        self.data_dir = self.workspace / "data" / "business_insights"
        self.docs_dir = self.workspace / "docs"

        self.sync_results = {
            "validation": {},
            "updates_needed": [],
            "files_modified": [],
            "errors": []
        }

    def validate_existing_data(self, limit: int = 5) -> Dict[str, Any]:
        """
        Validate existing extracted data against current schema
        Returns validation report
        """
        print(f"\n{'='*70}")
        print("VALIDATING EXISTING DATA AGAINST SCHEMA")
        print(f"{'='*70}\n")

        validation_results = {
            "total_files": 0,
            "valid_files": 0,
            "files_with_warnings": 0,
            "files_with_errors": 0,
            "details": []
        }

        insight_files = list(self.data_dir.glob("*_insights.json"))[:limit]
        validation_results["total_files"] = len(insight_files)

        for insight_file in insight_files:
            try:
                with open(insight_file, 'r') as f:
                    data = json.load(f)

                report = validate_data_structure(data)

                file_result = {
                    "file": insight_file.name,
                    "valid": report["valid"],
                    "errors": report["errors"],
                    "warnings": report["warnings"],
                    "missing_fields": report["missing_fields"],
                    "extra_fields": report["extra_fields"]
                }

                if report["valid"] and not report["errors"]:
                    validation_results["valid_files"] += 1
                    print(f"✅ {insight_file.name}")
                elif report["warnings"]:
                    validation_results["files_with_warnings"] += 1
                    print(f"⚠️  {insight_file.name} - {len(report['warnings'])} warnings")
                    file_result["warning_sample"] = report["warnings"][:3]
                else:
                    validation_results["files_with_errors"] += 1
                    print(f"❌ {insight_file.name} - {len(report['errors'])} errors")
                    file_result["error_sample"] = report["errors"][:3]

                validation_results["details"].append(file_result)

            except Exception as e:
                print(f"❌ {insight_file.name} - Exception: {e}")
                validation_results["files_with_errors"] += 1
                validation_results["details"].append({
                    "file": insight_file.name,
                    "valid": False,
                    "exception": str(e)
                })

        print(f"\n{'='*70}")
        print("VALIDATION SUMMARY")
        print(f"{'='*70}")
        print(f"Total files: {validation_results['total_files']}")
        print(f"✅ Valid: {validation_results['valid_files']}")
        print(f"⚠️  Warnings: {validation_results['files_with_warnings']}")
        print(f"❌ Errors: {validation_results['files_with_errors']}")
        print(f"{'='*70}\n")

        self.sync_results["validation"] = validation_results
        return validation_results

    def check_extractor_sync(self) -> bool:
        """
        Check if business_intelligence_extractor.py is in sync with schema
        """
        print(f"\n{'='*70}")
        print("CHECKING EXTRACTOR SYNC")
        print(f"{'='*70}\n")

        extractor_file = self.scripts_dir / "business_intelligence_extractor.py"

        if not extractor_file.exists():
            print("❌ Extractor file not found")
            self.sync_results["errors"].append("Extractor file not found")
            return False

        with open(extractor_file, 'r') as f:
            extractor_content = f.read()

        # Check for schema version reference
        if SCHEMA_VERSION in extractor_content:
            print(f"✅ Schema version {SCHEMA_VERSION} found")
        else:
            print(f"⚠️  Schema version {SCHEMA_VERSION} not found in extractor")
            self.sync_results["updates_needed"].append(
                "Add schema version reference to extractor"
            )

        # Check if all categories from schema are in extraction prompt
        missing_categories = []
        for category in EXTRACTION_SCHEMA.keys():
            if category == "meta":
                continue
            if f'"{category}"' not in extractor_content:
                missing_categories.append(category)

        if missing_categories:
            print(f"⚠️  Missing categories in extractor: {missing_categories}")
            self.sync_results["updates_needed"].append(
                f"Add categories to extractor: {missing_categories}"
            )
            return False
        else:
            print(f"✅ All schema categories present in extractor")
            return True

    def check_mcp_server_sync(self) -> bool:
        """
        Check if MCP server is in sync with schema
        """
        print(f"\n{'='*70}")
        print("CHECKING MCP SERVER SYNC")
        print(f"{'='*70}\n")

        server_file = self.mcp_dir / "server.py"

        if not server_file.exists():
            print("❌ MCP server file not found")
            self.sync_results["errors"].append("MCP server file not found")
            return False

        with open(server_file, 'r') as f:
            server_content = f.read()

        # Check for schema import
        if "from schema import" in server_content or "import schema" in server_content:
            print("✅ Schema module imported")
        else:
            print("⚠️  Schema module not imported - server should use centralized schema")
            self.sync_results["updates_needed"].append(
                "Import schema module in MCP server"
            )

        # Check if all data categories are being extracted
        all_synced = True
        for category in EXTRACTION_SCHEMA.keys():
            if category == "meta":
                continue

            # Check if category is being loaded
            category_var = f"'{category}'"
            if category_var not in server_content:
                print(f"⚠️  Category '{category}' not found in MCP server")
                self.sync_results["updates_needed"].append(
                    f"Add category '{category}' to MCP server data loading"
                )
                all_synced = False

        if all_synced:
            print("✅ All schema categories present in MCP server")

        # Check if all MCP tools are implemented
        for tool_name in MCP_TOOL_MAPPINGS.keys():
            if f'"{tool_name}"' in server_content or f"'{tool_name}'" in server_content:
                print(f"  ✅ Tool '{tool_name}' implemented")
            else:
                print(f"  ⚠️  Tool '{tool_name}' not found in server")
                self.sync_results["updates_needed"].append(
                    f"Implement tool '{tool_name}' in MCP server"
                )
                all_synced = False

        return all_synced

    def generate_schema_documentation(self) -> str:
        """
        Generate schema documentation
        """
        print(f"\n{'='*70}")
        print("GENERATING SCHEMA DOCUMENTATION")
        print(f"{'='*70}\n")

        doc_content = export_schema_markdown()

        # Add MCP tool mappings section
        doc_content += "\n\n## MCP Tool Mappings\n\n"
        for tool_name, mapping in MCP_TOOL_MAPPINGS.items():
            doc_content += f"### {tool_name}\n"
            doc_content += f"**Data Category:** `{mapping['data_category']}`\n\n"
            doc_content += f"**Description:** {mapping['description']}\n\n"
            doc_content += f"**Filter Fields:** {', '.join(mapping['filter_fields']) if mapping['filter_fields'] else 'None'}\n\n"
            doc_content += f"**Search Fields:** {', '.join(mapping['search_fields'])}\n\n"

        # Save to file
        doc_file = self.docs_dir / "BUSINESS_INTELLIGENCE_SCHEMA.md"
        with open(doc_file, 'w') as f:
            f.write(doc_content)

        print(f"✅ Documentation generated: {doc_file}")
        self.sync_results["files_modified"].append(str(doc_file))

        return doc_content

    def generate_extraction_prompt_update(self) -> str:
        """
        Generate updated extraction prompt from schema
        """
        print(f"\n{'='*70}")
        print("GENERATING EXTRACTION PROMPT")
        print(f"{'='*70}\n")

        prompt = get_extraction_prompt()

        print("✅ Extraction prompt generated from schema")
        print(f"   Categories: {len(EXTRACTION_SCHEMA)}")
        print(f"   Prompt length: {len(prompt)} chars")

        return prompt

    def test_schema_compatibility(self) -> bool:
        """
        Test that schema changes are backward compatible
        """
        print(f"\n{'='*70}")
        print("TESTING SCHEMA COMPATIBILITY")
        print(f"{'='*70}\n")

        # Load a sample existing file
        sample_files = list(self.data_dir.glob("*_insights.json"))[:1]

        if not sample_files:
            print("⚠️  No sample files found for compatibility testing")
            return True

        sample_file = sample_files[0]
        print(f"Testing with: {sample_file.name}")

        try:
            with open(sample_file, 'r') as f:
                data = json.load(f)

            report = validate_data_structure(data)

            if report["valid"]:
                print("✅ Schema is backward compatible")
                return True
            elif report["warnings"] and not report["errors"]:
                print("⚠️  Schema has warnings but is compatible")
                print(f"   Warnings: {len(report['warnings'])}")
                return True
            else:
                print("❌ Schema has breaking changes!")
                print(f"   Errors: {report['errors']}")
                self.sync_results["errors"].append("Breaking schema changes detected")
                return False

        except Exception as e:
            print(f"❌ Compatibility test failed: {e}")
            self.sync_results["errors"].append(f"Compatibility test error: {e}")
            return False

    def generate_migration_guide(self) -> str:
        """
        Generate migration guide for schema changes
        """
        guide = f"""# Schema Migration Guide

## Current Version: {SCHEMA_VERSION}

### Changes Required

"""
        if self.sync_results["updates_needed"]:
            guide += "#### Updates Needed:\n"
            for update in self.sync_results["updates_needed"]:
                guide += f"- {update}\n"
            guide += "\n"

        if self.sync_results["errors"]:
            guide += "#### Errors to Fix:\n"
            for error in self.sync_results["errors"]:
                guide += f"- ❌ {error}\n"
            guide += "\n"

        if self.sync_results["files_modified"]:
            guide += "#### Files Modified:\n"
            for file in self.sync_results["files_modified"]:
                guide += f"- {file}\n"
            guide += "\n"

        guide += """
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
"""

        return guide

    def run_full_sync(self) -> Dict[str, Any]:
        """
        Run complete schema synchronization
        """
        print(f"\n{'='*70}")
        print(f"SCHEMA SYNCHRONIZATION v{SCHEMA_VERSION}")
        print(f"{'='*70}\n")

        # Step 1: Validate existing data
        self.validate_existing_data(limit=10)

        # Step 2: Check extractor sync
        extractor_synced = self.check_extractor_sync()

        # Step 3: Check MCP server sync
        mcp_synced = self.check_mcp_server_sync()

        # Step 4: Test compatibility
        compatible = self.test_schema_compatibility()

        # Step 5: Generate documentation
        self.generate_schema_documentation()

        # Step 6: Generate extraction prompt
        self.generate_extraction_prompt_update()

        # Step 7: Generate migration guide
        migration_guide = self.generate_migration_guide()

        # Save migration guide
        guide_file = self.docs_dir / "SCHEMA_MIGRATION_GUIDE.md"
        with open(guide_file, 'w') as f:
            f.write(migration_guide)
        self.sync_results["files_modified"].append(str(guide_file))

        # Final report
        print(f"\n{'='*70}")
        print("SYNC SUMMARY")
        print(f"{'='*70}")
        print(f"Schema Version: {SCHEMA_VERSION}")
        print(f"Extractor Synced: {'✅' if extractor_synced else '⚠️'}")
        print(f"MCP Server Synced: {'✅' if mcp_synced else '⚠️'}")
        print(f"Backward Compatible: {'✅' if compatible else '❌'}")
        print(f"Updates Needed: {len(self.sync_results['updates_needed'])}")
        print(f"Errors: {len(self.sync_results['errors'])}")
        print(f"Files Modified: {len(self.sync_results['files_modified'])}")
        print(f"{'='*70}\n")

        if self.sync_results["updates_needed"]:
            print("⚠️  UPDATES NEEDED:")
            for update in self.sync_results["updates_needed"]:
                print(f"  - {update}")
            print()

        if self.sync_results["errors"]:
            print("❌ ERRORS:")
            for error in self.sync_results["errors"]:
                print(f"  - {error}")
            print()

        print(f"📄 Migration guide: {guide_file}\n")

        return self.sync_results


def main():
    """Run schema synchronization"""
    import sys

    manager = SchemaSyncManager()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--validate":
            manager.validate_existing_data(limit=50)
        elif command == "--full-sync":
            manager.run_full_sync()
        elif command == "--check-extractor":
            manager.check_extractor_sync()
        elif command == "--check-mcp":
            manager.check_mcp_server_sync()
        elif command == "--docs":
            manager.generate_schema_documentation()
        else:
            print("Unknown command")
    else:
        # Run full sync by default
        manager.run_full_sync()


if __name__ == "__main__":
    main()
