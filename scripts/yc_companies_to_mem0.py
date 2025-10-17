#!/usr/bin/env python3
"""
Y Combinator Companies to Mem0
Ingest YC company data into mem0 for semantic search and AI retrieval
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

# Add config directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "config"))

from mem0_collections import get_mem0_config


class YCCompaniesToMem0:
    """Ingest Y Combinator companies into Mem0"""

    def __init__(self, collection_name: str = "yc_companies"):
        """
        Initialize with mem0 configuration

        Args:
            collection_name: Name for the YC companies collection
        """
        self.collection_name = collection_name
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.cache_dir = self.workspace_dir / "data" / "yc_companies"

        # Initialize mem0 with collection config
        try:
            from mem0 import Memory
            config = get_mem0_config(collection_name)
            self.memory = Memory.from_config(config)
            print(f"✅ Initialized Mem0 with collection: {collection_name}")
        except ImportError:
            raise ImportError("mem0ai not installed. Install with: pip install mem0ai")
        except Exception as e:
            print(f"⚠️  Error initializing Mem0: {e}")
            self.memory = None

    def load_companies(self) -> List[Dict]:
        """Load YC companies from cached JSON"""
        cache_file = self.cache_dir / "all_companies.json"

        if not cache_file.exists():
            print(f"❌ Companies cache not found at: {cache_file}")
            print("   Run: python3 scripts/yc_companies_extractor.py --analyze")
            return []

        with open(cache_file, 'r') as f:
            companies = json.load(f)

        print(f"📦 Loaded {len(companies)} companies from cache")
        return companies

    def format_company_for_mem0(self, company: Dict) -> str:
        """
        Format company data as rich text for mem0 storage

        Args:
            company: Company data dictionary

        Returns:
            Formatted text representation
        """
        # Build comprehensive text representation
        parts = []

        # Header
        parts.append(f"# {company.get('name', 'Unknown Company')}")

        # Batch and status
        batch = company.get('batch', 'N/A')
        status = company.get('status', 'N/A')
        parts.append(f"Batch: {batch} | Status: {status}")

        # One-liner
        if company.get('one_liner'):
            parts.append(f"\n{company['one_liner']}")

        # Long description
        if company.get('long_description'):
            parts.append(f"\n## Description\n{company['long_description']}")

        # Classification
        parts.append("\n## Classification")
        if company.get('industry'):
            parts.append(f"Industry: {company['industry']}")
        if company.get('subindustry'):
            parts.append(f"Sub-industry: {company['subindustry']}")
        if company.get('stage'):
            parts.append(f"Stage: {company['stage']}")

        # Team and hiring
        parts.append("\n## Team")
        if company.get('team_size'):
            parts.append(f"Team Size: {company['team_size']}")
        if company.get('isHiring'):
            parts.append("🟢 Currently Hiring")
        if company.get('top_company'):
            parts.append("⭐ YC Top Company")
        if company.get('nonprofit'):
            parts.append("💙 Non-profit")

        # Tags and regions
        if company.get('tags'):
            tags = ", ".join(company['tags'][:10])  # Limit to first 10 tags
            parts.append(f"\n## Tags\n{tags}")

        if company.get('regions'):
            regions = ", ".join(company['regions'])
            parts.append(f"\n## Regions\n{regions}")

        # Industries list
        if company.get('industries'):
            industries = ", ".join(company['industries'])
            parts.append(f"\n## Industries\n{industries}")

        # Location
        if company.get('all_locations'):
            parts.append(f"\n## Location\n{company['all_locations']}")

        # Links
        parts.append("\n## Links")
        if company.get('website'):
            parts.append(f"Website: {company['website']}")
        if company.get('url'):
            parts.append(f"YC Profile: {company['url']}")

        # Former names
        if company.get('former_names') and company['former_names']:
            former = ", ".join(company['former_names'])
            parts.append(f"\nFormer Names: {former}")

        return "\n".join(parts)

    def ingest_companies(self, batch_size: int = 50, max_companies: Optional[int] = None):
        """
        Ingest companies into mem0

        Args:
            batch_size: Number of companies to process in each batch
            max_companies: Maximum companies to ingest (None for all)
        """
        if not self.memory:
            print("❌ Mem0 not initialized")
            return

        companies = self.load_companies()

        if not companies:
            return

        if max_companies:
            companies = companies[:max_companies]

        print(f"\n{'='*70}")
        print(f"🚀 INGESTING YC COMPANIES TO MEM0")
        print(f"{'='*70}\n")
        print(f"Collection: {self.collection_name}")
        print(f"Total companies: {len(companies)}")
        print(f"Batch size: {batch_size}\n")

        success_count = 0
        error_count = 0

        for i in range(0, len(companies), batch_size):
            batch = companies[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(companies) + batch_size - 1) // batch_size

            print(f"📦 Batch {batch_num}/{total_batches} ({len(batch)} companies)")

            for company in batch:
                try:
                    # Format company data
                    text = self.format_company_for_mem0(company)

                    # Create metadata
                    metadata = {
                        "company_id": company.get('id'),
                        "name": company.get('name', ''),
                        "slug": company.get('slug', ''),
                        "batch": company.get('batch', ''),
                        "status": company.get('status', ''),
                        "industry": company.get('industry', ''),
                        "team_size": company.get('team_size', 0),
                        "is_hiring": company.get('isHiring', False),
                        "top_company": company.get('top_company', False),
                        "website": company.get('website', ''),
                        "source": "yc_companies",
                        "ingested_at": datetime.now().isoformat()
                    }

                    # Add to mem0
                    # Using consistent user_id for searchability
                    self.memory.add(
                        text,
                        user_id="yc_all",  # Use consistent ID for all companies
                        metadata=metadata
                    )

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    company_name = company.get('name', 'Unknown')
                    print(f"  ⚠️  Error with {company_name}: {e}")

            # Progress update
            progress = (i + len(batch)) / len(companies) * 100
            print(f"  ✅ Progress: {progress:.1f}% | Success: {success_count} | Errors: {error_count}\n")

        # Summary
        print(f"{'='*70}")
        print(f"✅ INGESTION COMPLETE")
        print(f"{'='*70}")
        print(f"Success: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Total: {len(companies)}")
        print(f"Collection: {self.collection_name}")
        print(f"{'='*70}\n")

    def search_companies(self, query: str, limit: int = 10):
        """
        Search YC companies in mem0

        Args:
            query: Natural language query
            limit: Maximum results

        Returns:
            Search results from mem0
        """
        if not self.memory:
            print("❌ Mem0 not initialized")
            return []

        try:
            # Search with a batch user_id (or try without if that fails)
            results = self.memory.search(
                query,
                user_id="yc_all",  # General search user_id
                limit=limit
            )
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            # Try getting all memories if search fails
            try:
                all_memories = self.memory.get_all(user_id="yc_all", limit=limit)
                return all_memories.get('results', [])
            except:
                return []

    def get_company_by_name(self, name: str):
        """Get specific company by name"""
        results = self.search_companies(f"company name {name}", limit=5)

        # Filter for exact or close matches
        for result in results:
            metadata = result.get('metadata', {})
            if metadata.get('name', '').lower() == name.lower():
                return result

        # Return best match if no exact match
        return results[0] if results else None


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Ingest YC companies to Mem0')
    parser.add_argument('--collection', default='yc_companies', help='Mem0 collection name')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for ingestion')
    parser.add_argument('--max', type=int, help='Maximum companies to ingest (for testing)')
    parser.add_argument('--search', help='Search query to test')

    args = parser.parse_args()

    ingestor = YCCompaniesToMem0(collection_name=args.collection)

    if args.search:
        # Search mode
        print(f"\n🔍 Searching for: {args.search}\n")
        results = ingestor.search_companies(args.search, limit=10)

        if results:
            print(f"Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                # Handle different result formats from Mem0
                if isinstance(result, dict):
                    metadata = result.get('metadata', {})
                    memory = result.get('memory', '')
                elif isinstance(result, str):
                    # Result is just the text
                    memory = result
                    metadata = {}
                else:
                    continue

                print(f"{i}. {metadata.get('name', 'Unknown Company')}")
                if metadata:
                    print(f"   Batch: {metadata.get('batch', 'N/A')} | Status: {metadata.get('status', 'N/A')}")
                    print(f"   Industry: {metadata.get('industry', 'N/A')}")
                    if metadata.get('is_hiring'):
                        print(f"   🟢 Hiring")
                print(f"   Preview: {memory[:200]}...")
                print()
        else:
            print("No results found")

    else:
        # Ingest mode
        ingestor.ingest_companies(
            batch_size=args.batch_size,
            max_companies=args.max
        )

        # Show search example
        print("🔍 To search companies:")
        print(f"   python3 scripts/yc_companies_to_mem0.py --search 'your query'")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║       Y Combinator Companies → Mem0 Ingestion                ║
║       Semantic search for 5,490+ YC companies                ║
╚══════════════════════════════════════════════════════════════╝
""")

    main()
