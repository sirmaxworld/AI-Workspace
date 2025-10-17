#!/usr/bin/env python3
"""
Network & Relationship Enricher - Phase 4
Pure computation from existing YC data - no external APIs needed.
Analyzes relationships and connections between companies:
- YC batch connections
- Investor networks (when data available)
- Technology stack overlaps
- Market/industry overlaps
- Geographic clusters
"""

import json
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging
from pathlib import Path
from collections import defaultdict, Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetworkEnricher:
    """Enriches YC companies with network and relationship data"""

    VERSION = "1.0.0"

    def __init__(self, all_companies: List[Dict]):
        """
        Initialize with full company dataset for network analysis

        Args:
            all_companies: List of all YC companies with enrichment data
        """
        self.all_companies = all_companies
        self.companies_by_batch = self._index_by_batch()
        self.companies_by_industry = self._index_by_industry()
        self.companies_by_location = self._index_by_location()

        logger.info(f"NetworkEnricher initialized with {len(all_companies)} companies")

    def _index_by_batch(self) -> Dict[str, List[Dict]]:
        """Index companies by YC batch"""
        index = defaultdict(list)
        for company in self.all_companies:
            batch = company.get('batch')
            if batch:
                index[batch].append(company)
        return dict(index)

    def _index_by_industry(self) -> Dict[str, List[Dict]]:
        """Index companies by industry"""
        index = defaultdict(list)
        for company in self.all_companies:
            industries = company.get('industries', [])
            for industry in industries:
                index[industry].append(company)
        return dict(index)

    def _index_by_location(self) -> Dict[str, List[Dict]]:
        """Index companies by location (city-level)"""
        index = defaultdict(list)
        for company in self.all_companies:
            location = company.get('all_locations', '')
            if location:
                # Extract city (first part before comma)
                city = location.split(',')[0].strip()
                if city:
                    index[city].append(company)
        return dict(index)

    def enrich(self, company: Dict) -> Dict:
        """
        Main enrichment function for network data

        Args:
            company: Company data dict

        Returns:
            Dict with network enrichment data
        """
        enrichment_data = {
            "network_enrichment_version": self.VERSION,
            "enriched_at": datetime.now().isoformat(),
        }

        company_slug = company.get('slug')
        logger.info(f"Enriching network data for {company.get('name')}")

        # 1. Batch network
        batch_network = self._analyze_batch_network(company)
        enrichment_data["batch_network"] = batch_network

        # 2. Industry network
        industry_network = self._analyze_industry_network(company)
        enrichment_data["industry_network"] = industry_network

        # 3. Geographic network
        geo_network = self._analyze_geographic_network(company)
        enrichment_data["geographic_network"] = geo_network

        # 4. Technology stack overlap (if GitHub data available)
        tech_network = self._analyze_tech_network(company)
        enrichment_data["tech_network"] = tech_network

        # 5. Similar companies (综合相似度)
        similar_companies = self._find_similar_companies(company)
        enrichment_data["similar_companies"] = similar_companies

        # 6. Network metrics
        metrics = self._calculate_network_metrics(company, enrichment_data)
        enrichment_data["network_metrics"] = metrics

        return enrichment_data

    def _analyze_batch_network(self, company: Dict) -> Dict:
        """Analyze connections within the same YC batch"""
        batch = company.get('batch')

        if not batch or batch not in self.companies_by_batch:
            return {"status": "no_batch_data"}

        batch_companies = self.companies_by_batch[batch]
        company_slug = company.get('slug')

        # Filter out self
        batch_mates = [c for c in batch_companies if c.get('slug') != company_slug]

        # Count active vs inactive
        active_count = sum(1 for c in batch_mates if c.get('status') == 'Active')

        # Find notable batch-mates (top companies, acquired, etc.)
        notable = [
            {
                "name": c.get('name'),
                "slug": c.get('slug'),
                "status": c.get('status'),
                "top_company": c.get('top_company', False),
                "one_liner": c.get('one_liner')
            }
            for c in batch_mates
            if c.get('top_company') or c.get('status') in ['Acquired', 'Public']
        ][:10]

        return {
            "batch": batch,
            "total_batch_mates": len(batch_mates),
            "active_batch_mates": active_count,
            "batch_success_rate": round(active_count / len(batch_mates) * 100, 1) if batch_mates else 0,
            "notable_batch_mates": notable,
            "batch_size": len(batch_companies)
        }

    def _analyze_industry_network(self, company: Dict) -> Dict:
        """Analyze connections within the same industry"""
        industries = company.get('industries', [])

        if not industries:
            return {"status": "no_industry_data"}

        company_slug = company.get('slug')
        industry_peers = set()

        # Find all companies in same industries
        for industry in industries:
            if industry in self.companies_by_industry:
                for peer in self.companies_by_industry[industry]:
                    if peer.get('slug') != company_slug:
                        industry_peers.add(peer.get('slug'))

        # Get full peer data
        peers = [
            c for c in self.all_companies
            if c.get('slug') in industry_peers
        ]

        # Find direct competitors (same subindustry)
        subindustry = company.get('subindustry')
        direct_competitors = []

        if subindustry:
            direct_competitors = [
                {
                    "name": c.get('name'),
                    "slug": c.get('slug'),
                    "status": c.get('status'),
                    "batch": c.get('batch'),
                    "one_liner": c.get('one_liner')
                }
                for c in peers
                if c.get('subindustry') == subindustry
            ][:10]

        return {
            "industries": industries,
            "total_industry_peers": len(peers),
            "active_industry_peers": sum(1 for c in peers if c.get('status') == 'Active'),
            "direct_competitors": direct_competitors,
            "competitor_count": len(direct_competitors)
        }

    def _analyze_geographic_network(self, company: Dict) -> Dict:
        """Analyze geographic clustering with other YC companies"""
        location = company.get('all_locations', '')

        if not location:
            return {"status": "no_location_data"}

        # Extract city
        city = location.split(',')[0].strip()

        if not city or city not in self.companies_by_location:
            return {"status": "location_not_found", "location": location}

        company_slug = company.get('slug')
        city_companies = [c for c in self.companies_by_location[city] if c.get('slug') != company_slug]

        # Get nearby companies (same city)
        nearby = [
            {
                "name": c.get('name'),
                "slug": c.get('slug'),
                "batch": c.get('batch'),
                "industry": c.get('industry'),
                "status": c.get('status')
            }
            for c in city_companies[:20]  # Top 20
        ]

        return {
            "city": city,
            "location": location,
            "companies_in_city": len(city_companies),
            "active_in_city": sum(1 for c in city_companies if c.get('status') == 'Active'),
            "nearby_companies": nearby,
            "ecosystem_density": "high" if len(city_companies) > 100 else "medium" if len(city_companies) > 20 else "low"
        }

    def _analyze_tech_network(self, company: Dict) -> Dict:
        """Analyze technology stack overlap with other companies"""
        # Get GitHub data from Phase 3
        github_data = company.get('github_data', {})
        tech_stack = github_data.get('tech_stack', {})
        primary_language = tech_stack.get('primary_language')

        if not primary_language:
            return {"status": "no_tech_data"}

        company_slug = company.get('slug')

        # Find companies using same primary language
        same_tech_companies = []
        for other in self.all_companies:
            if other.get('slug') == company_slug:
                continue

            other_github = other.get('github_data', {})
            other_tech = other_github.get('tech_stack', {})
            other_language = other_tech.get('primary_language')

            if other_language == primary_language:
                same_tech_companies.append({
                    "name": other.get('name'),
                    "slug": other.get('slug'),
                    "batch": other.get('batch'),
                    "industry": other.get('industry')
                })

        return {
            "primary_language": primary_language,
            "companies_using_same_tech": len(same_tech_companies),
            "same_tech_companies": same_tech_companies[:15],
            "potential_integration_partners": same_tech_companies[:5]
        }

    def _find_similar_companies(self, company: Dict) -> List[Dict]:
        """Find most similar companies based on multiple factors"""
        company_slug = company.get('slug')
        batch = company.get('batch')
        industries = set(company.get('industries', []))
        location = company.get('all_locations', '')
        city = location.split(',')[0].strip() if location else ''

        # Score each company by similarity
        similarity_scores = []

        for other in self.all_companies:
            if other.get('slug') == company_slug:
                continue

            score = 0
            reasons = []

            # Same batch (+3 points)
            if other.get('batch') == batch:
                score += 3
                reasons.append("same_batch")

            # Industry overlap (+2 points per shared industry)
            other_industries = set(other.get('industries', []))
            shared_industries = industries & other_industries
            if shared_industries:
                score += len(shared_industries) * 2
                reasons.append(f"shared_industries:{len(shared_industries)}")

            # Same city (+2 points)
            other_location = other.get('all_locations', '')
            other_city = other_location.split(',')[0].strip() if other_location else ''
            if city and city == other_city:
                score += 2
                reasons.append("same_city")

            # Same tech stack (+1 point)
            github_data = company.get('github_data', {})
            other_github = other.get('github_data', {})
            if github_data.get('tech_stack', {}).get('primary_language') == other_github.get('tech_stack', {}).get('primary_language'):
                score += 1
                reasons.append("same_tech")

            if score > 0:
                similarity_scores.append({
                    "name": other.get('name'),
                    "slug": other.get('slug'),
                    "batch": other.get('batch'),
                    "industry": other.get('industry'),
                    "status": other.get('status'),
                    "similarity_score": score,
                    "similarity_reasons": reasons
                })

        # Sort by score
        similarity_scores.sort(key=lambda x: x['similarity_score'], reverse=True)

        return similarity_scores[:10]  # Top 10 most similar

    def _calculate_network_metrics(self, company: Dict, enrichment_data: Dict) -> Dict:
        """Calculate overall network metrics"""

        # Total connections
        total_connections = 0
        batch_network = enrichment_data.get('batch_network', {})
        industry_network = enrichment_data.get('industry_network', {})
        geo_network = enrichment_data.get('geographic_network', {})

        total_connections += batch_network.get('total_batch_mates', 0)
        total_connections += industry_network.get('total_industry_peers', 0)
        total_connections += geo_network.get('companies_in_city', 0)

        # Network density score (0-100)
        # Based on batch, industry, and geographic connections
        density_score = min(100, (
            (batch_network.get('total_batch_mates', 0) / 100 * 20) +
            (min(industry_network.get('total_industry_peers', 0), 500) / 500 * 40) +
            (min(geo_network.get('companies_in_city', 0), 200) / 200 * 40)
        ))

        return {
            "total_yc_connections": total_connections,
            "network_density_score": round(density_score, 1),
            "has_strong_batch_network": batch_network.get('total_batch_mates', 0) > 30,
            "has_strong_industry_network": industry_network.get('total_industry_peers', 0) > 50,
            "has_strong_geo_network": geo_network.get('companies_in_city', 0) > 20,
            "calculated_at": datetime.now().isoformat()
        }


def main():
    """Test the enricher"""

    # Load all companies
    companies_file = Path("/Users/yourox/AI-Workspace/data/yc_companies/all_companies.json")
    with open(companies_file, 'r') as f:
        companies = json.load(f)

    # Initialize enricher
    enricher = NetworkEnricher(companies)

    # Test on first company
    result = enricher.enrich(companies[0])

    print(f"\n{'='*70}")
    print(f"Company: {companies[0]['name']}")
    print(f"{'='*70}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
