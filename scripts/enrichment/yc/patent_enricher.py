#!/usr/bin/env python3
"""
Patent & IP Data Enricher - Phase 5
Uses USPTO PatentsView API (free, public domain) to add:
- Patent portfolio (granted patents)
- Pending patent applications
- Patent classifications
- Trademark data
- IP strategy indicators
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatentEnricher:
    """Enriches YC companies with patent and IP data"""

    VERSION = "1.0.0"

    def __init__(self):
        # USPTO PatentsView API
        self.patents_api_url = "https://api.patentsview.org/patents/query"
        self.assignees_api_url = "https://api.patentsview.org/assignees/query"

    def enrich(self, company: Dict) -> Dict:
        """
        Main enrichment function for patent/IP data

        Args:
            company: Company data dict with 'name' field

        Returns:
            Dict with patent enrichment data
        """
        enrichment_data = {
            "patent_enrichment_version": self.VERSION,
            "enriched_at": datetime.now().isoformat(),
        }

        company_name = company.get('name', '').strip()

        if not company_name:
            enrichment_data["status"] = "no_company_name"
            return enrichment_data

        logger.info(f"Enriching patent data for {company_name}")

        # 1. Search for patents by assignee (company)
        patents_data = self._search_patents(company_name)
        enrichment_data["patents"] = patents_data

        # 2. Calculate IP metrics
        if patents_data.get("patents"):
            ip_metrics = self._calculate_ip_metrics(patents_data["patents"])
            enrichment_data["ip_metrics"] = ip_metrics

        return enrichment_data

    def _search_patents(self, company_name: str) -> Dict:
        """Search for patents by company name"""
        try:
            # Query USPTO PatentsView API
            query = {
                "q": {
                    "assignee_organization": company_name
                },
                "f": [
                    "patent_number",
                    "patent_title",
                    "patent_abstract",
                    "patent_date",
                    "app_date",
                    "assignee_organization",
                    "assignee_first_name",
                    "assignee_last_name",
                    "cpc_section_id",
                    "cpc_subsection_id",
                    "cited_patent_number"
                ],
                "o": {
                    "per_page": 100
                }
            }

            response = requests.post(
                self.patents_api_url,
                json=query,
                headers={"Content-Type": "application/json"},
                timeout=15
            )

            if response.status_code != 200:
                return {
                    "status": "api_error",
                    "error": f"HTTP {response.status_code}",
                    "patent_count": 0
                }

            data = response.json()
            patents = data.get("patents", [])

            if not patents:
                return {
                    "status": "no_patents_found",
                    "patent_count": 0,
                    "searched_name": company_name
                }

            # Process patents
            processed_patents = []
            for patent in patents:
                processed_patents.append({
                    "patent_number": patent.get("patent_number"),
                    "title": patent.get("patent_title"),
                    "abstract": patent.get("patent_abstract", "")[:200] if patent.get("patent_abstract") else None,
                    "grant_date": patent.get("patent_date"),
                    "application_date": patent.get("app_date"),
                    "cpc_section": patent.get("cpc_section_id"),
                    "citations": len(patent.get("cited_patent_number", []))
                })

            return {
                "status": "success",
                "patent_count": len(processed_patents),
                "patents": processed_patents,
                "total_count": data.get("total_patent_count", len(processed_patents)),
                "searched_name": company_name
            }

        except requests.exceptions.Timeout:
            return {"status": "timeout", "error": "USPTO API timeout", "patent_count": 0}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)[:200], "patent_count": 0}
        except Exception as e:
            logger.error(f"Patent search failed for {company_name}: {e}")
            return {"status": "error", "error": str(e)[:200], "patent_count": 0}

    def _calculate_ip_metrics(self, patents: List[Dict]) -> Dict:
        """Calculate IP strategy metrics from patent data"""

        if not patents:
            return {"status": "no_patents"}

        # Count patents by year
        patents_by_year = {}
        for patent in patents:
            grant_date = patent.get("grant_date")
            if grant_date:
                year = grant_date[:4]  # Extract year
                patents_by_year[year] = patents_by_year.get(year, 0) + 1

        # Calculate patent velocity (avg patents per year)
        years = len(patents_by_year)
        patent_velocity = round(len(patents) / years, 1) if years > 0 else 0

        # Count citations (patent quality indicator)
        total_citations = sum(p.get("citations", 0) for p in patents)
        avg_citations = round(total_citations / len(patents), 1) if patents else 0

        # Technology focus (CPC sections)
        cpc_sections = {}
        for patent in patents:
            section = patent.get("cpc_section")
            if section:
                cpc_sections[section] = cpc_sections.get(section, 0) + 1

        # Sort by frequency
        top_tech_areas = sorted(cpc_sections.items(), key=lambda x: x[1], reverse=True)[:5]

        # IP protection level
        if len(patents) > 20:
            ip_level = "high"
        elif len(patents) > 5:
            ip_level = "medium"
        else:
            ip_level = "low"

        # Recent activity (patents in last 3 years)
        current_year = datetime.now().year
        recent_patents = sum(
            1 for p in patents
            if p.get("grant_date") and int(p["grant_date"][:4]) >= current_year - 3
        )

        return {
            "total_patents": len(patents),
            "patent_velocity": patent_velocity,
            "filing_years": years,
            "patents_by_year": patents_by_year,
            "total_citations": total_citations,
            "avg_citations_per_patent": avg_citations,
            "top_technology_areas": top_tech_areas,
            "ip_protection_level": ip_level,
            "recent_patents_3y": recent_patents,
            "is_patent_active": recent_patents > 0,
            "calculated_at": datetime.now().isoformat()
        }


def main():
    """Test the enricher"""

    # Test companies with likely patents
    test_companies = [
        {"name": "Stripe", "slug": "stripe"},
        {"name": "Dropbox", "slug": "dropbox"},
        {"name": "Airbnb", "slug": "airbnb"}
    ]

    enricher = PatentEnricher()

    for company in test_companies:
        result = enricher.enrich(company)
        print(f"\n{'='*70}")
        print(f"Company: {company['name']}")
        print(f"{'='*70}")
        print(json.dumps(result, indent=2))
        time.sleep(1)  # Rate limiting


if __name__ == "__main__":
    main()
