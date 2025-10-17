#!/usr/bin/env python3
"""
Y Combinator Companies Extractor
Fetch and store YC company data from the public API
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')


class YCCompaniesExtractor:
    """Extract Y Combinator company data from public API"""

    def __init__(self):
        self.workspace_dir = Path("/Users/yourox/AI-Workspace")
        self.cache_dir = self.workspace_dir / "data" / "yc_companies"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # YC API endpoints
        self.base_url = "https://yc-oss.github.io/api"
        self.all_companies_url = f"{self.base_url}/companies/all.json"

        # Supabase configuration
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")

        # OpenAI for embeddings (optional)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def fetch_companies(self, force_refresh: bool = False) -> List[Dict]:
        """
        Fetch all YC companies from the API
        Uses cached data if available and not forcing refresh
        """
        cache_file = self.cache_dir / "all_companies.json"

        # Check cache
        if cache_file.exists() and not force_refresh:
            print("📦 Using cached company data")
            with open(cache_file, 'r') as f:
                return json.load(f)

        print(f"🌐 Fetching companies from YC API...")
        try:
            response = requests.get(self.all_companies_url, timeout=30)
            response.raise_for_status()
            companies = response.json()

            print(f"✅ Fetched {len(companies)} companies")

            # Cache the data
            with open(cache_file, 'w') as f:
                json.dump(companies, f, indent=2)

            # Save metadata
            metadata = {
                "fetched_at": datetime.now().isoformat(),
                "total_companies": len(companies),
                "source": self.all_companies_url
            }
            with open(self.cache_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)

            return companies

        except Exception as e:
            print(f"❌ Error fetching companies: {e}")
            # Try to use cache as fallback
            if cache_file.exists():
                print("📦 Using cached data as fallback")
                with open(cache_file, 'r') as f:
                    return json.load(f)
            raise

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate OpenAI embedding for text"""
        if not self.openai_api_key:
            return None

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"  ⚠️  Embedding error: {e}")
            return None

    def transform_company(self, company: Dict) -> Dict:
        """Transform API company data to database schema"""
        return {
            "yc_id": company.get("id"),
            "name": company.get("name"),
            "slug": company.get("slug"),
            "former_names": company.get("former_names", []),
            "website": company.get("website"),
            "logo_url": company.get("small_logo_thumb_url"),
            "one_liner": company.get("one_liner", ""),
            "long_description": company.get("long_description"),
            "batch": company.get("batch"),
            "status": company.get("status"),
            "stage": company.get("stage"),
            "industry": company.get("industry"),
            "subindustry": company.get("subindustry"),
            "industries": company.get("industries", []),
            "regions": company.get("regions", []),
            "tags": company.get("tags", []),
            "team_size": company.get("team_size"),
            "all_locations": company.get("all_locations"),
            "launched_at": company.get("launched_at"),
            "is_hiring": company.get("isHiring", False),
            "top_company": company.get("top_company", False),
            "nonprofit": company.get("nonprofit", False),
            "app_video_public": company.get("app_video_public", False),
            "demo_day_video_public": company.get("demo_day_video_public", False),
            "api_url": company.get("api"),
            "yc_url": company.get("url"),
        }

    def insert_to_supabase(self, companies: List[Dict], generate_embeddings: bool = False):
        """Insert companies into Supabase"""
        if not self.supabase_url or not self.supabase_key:
            print("⚠️  Supabase credentials not configured")
            print("   Companies data cached locally at:", self.cache_dir)
            return

        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)

            print(f"\n{'='*70}")
            print(f"📤 UPLOADING TO SUPABASE")
            print(f"{'='*70}\n")
            print(f"Total companies: {len(companies)}")

            if generate_embeddings:
                print(f"🧠 Generating embeddings (this will take a while)...")

            # Transform and insert companies
            batch_size = 100
            success_count = 0
            error_count = 0

            for i in range(0, len(companies), batch_size):
                batch = companies[i:i + batch_size]
                transformed_batch = []

                for company in batch:
                    try:
                        transformed = self.transform_company(company)

                        # Generate embedding if requested
                        if generate_embeddings:
                            text = f"{transformed['name']} {transformed['one_liner']} {transformed.get('long_description', '')}"
                            embedding = self.generate_embedding(text[:8000])
                            if embedding:
                                transformed['embedding'] = embedding

                        transformed_batch.append(transformed)
                    except Exception as e:
                        print(f"  ⚠️  Error transforming company {company.get('name', 'unknown')}: {e}")
                        error_count += 1

                # Insert batch
                try:
                    # Use upsert to handle duplicates
                    result = supabase.table('yc_companies').upsert(
                        transformed_batch,
                        on_conflict='slug'
                    ).execute()

                    success_count += len(transformed_batch)
                    progress = (i + len(batch)) / len(companies) * 100
                    print(f"  ✅ Batch {i//batch_size + 1}: {len(transformed_batch)} companies ({progress:.1f}%)")

                except Exception as e:
                    print(f"  ❌ Error inserting batch: {e}")
                    error_count += len(transformed_batch)

            print(f"\n{'='*70}")
            print(f"✅ UPLOAD COMPLETE")
            print(f"{'='*70}")
            print(f"Success: {success_count}")
            print(f"Errors: {error_count}")
            print(f"{'='*70}\n")

        except ImportError:
            print("❌ supabase-py not installed. Install with: pip install supabase")
        except Exception as e:
            print(f"❌ Error connecting to Supabase: {e}")

    def analyze_dataset(self, companies: List[Dict]):
        """Analyze and print statistics about the dataset"""
        print(f"\n{'='*70}")
        print(f"📊 YC COMPANIES DATASET ANALYSIS")
        print(f"{'='*70}\n")

        print(f"Total companies: {len(companies)}")

        # Status breakdown
        statuses = {}
        for company in companies:
            status = company.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1

        print(f"\n📍 By Status:")
        for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
            print(f"  {status}: {count}")

        # Top industries
        industries = {}
        for company in companies:
            industry = company.get('industry', 'unknown')
            industries[industry] = industries.get(industry, 0) + 1

        print(f"\n🏢 Top Industries:")
        for industry, count in sorted(industries.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {industry}: {count}")

        # Hiring companies
        hiring = sum(1 for c in companies if c.get('isHiring'))
        top = sum(1 for c in companies if c.get('top_company'))
        nonprofit = sum(1 for c in companies if c.get('nonprofit'))

        print(f"\n🎯 Special Categories:")
        print(f"  Hiring: {hiring}")
        print(f"  Top Companies: {top}")
        print(f"  Non-profit: {nonprofit}")

        # Recent batches
        batches = {}
        for company in companies:
            batch = company.get('batch', 'unknown')
            batches[batch] = batches.get(batch, 0) + 1

        print(f"\n📅 Recent Batches:")
        for batch, count in sorted(batches.items(), reverse=True)[:5]:
            print(f"  {batch}: {count}")

        print(f"\n{'='*70}\n")

    def export_to_json(self, companies: List[Dict], filename: str = "yc_companies_export.json"):
        """Export companies to a JSON file"""
        output_file = self.cache_dir / filename

        transformed = [self.transform_company(c) for c in companies]

        with open(output_file, 'w') as f:
            json.dump(transformed, f, indent=2)

        print(f"📄 Exported to: {output_file}")


def main():
    import sys

    extractor = YCCompaniesExtractor()

    # Parse command line arguments
    force_refresh = '--refresh' in sys.argv
    generate_embeddings = '--embeddings' in sys.argv
    analyze_only = '--analyze' in sys.argv
    export_only = '--export' in sys.argv

    # Fetch companies
    companies = extractor.fetch_companies(force_refresh=force_refresh)

    # Analyze dataset
    if analyze_only:
        extractor.analyze_dataset(companies)
        return

    # Export to JSON
    if export_only:
        extractor.export_to_json(companies)
        return

    # Show analysis
    extractor.analyze_dataset(companies)

    # Insert to Supabase
    if '--upload' in sys.argv:
        print("\n🚀 Starting upload to Supabase...")
        extractor.insert_to_supabase(companies, generate_embeddings=generate_embeddings)
    else:
        print("\n💡 To upload to Supabase, run with --upload flag")
        print("   Example: python3 yc_companies_extractor.py --upload")
        print("\n💡 To generate embeddings, add --embeddings flag (takes longer)")
        print("   Example: python3 yc_companies_extractor.py --upload --embeddings")

    print(f"\n✅ Data cached at: {extractor.cache_dir}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║          Y Combinator Companies Extractor                    ║
║          Fetch 5,490+ YC companies with metadata            ║
╚══════════════════════════════════════════════════════════════╝
""")

    main()
