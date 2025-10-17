#!/usr/bin/env python3
"""
Geographic Data Enricher - Phase 2
Uses Google Places API (free tier: 28,000 requests/month) to add:
- Precise coordinates (lat/lng)
- Formatted address, city, state, country
- Timezone
- Google Maps rating & reviews
- Startup ecosystem density (YC companies nearby)
"""

import os
import requests
import json
from typing import Dict, Optional, List
from datetime import datetime
import logging
import time
from pathlib import Path
from geopy.distance import geodesic
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/yourox/AI-Workspace/.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeographicEnricher:
    """Enriches YC companies with geographic data"""

    VERSION = "1.0.0"

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            logger.info("GOOGLE_MAPS_API_KEY not found. Using free Nominatim geocoding (OpenStreetMap).")
            logger.info("To use Google Maps API with richer data:")
            logger.info("  1. Get API key: https://console.cloud.google.com/google/maps-apis")
            logger.info("  2. Enable: Places API, Geocoding API, Time Zone API")
            logger.info("  3. Add to .env: GOOGLE_MAPS_API_KEY=your_key_here")
        else:
            logger.info("✓ Using Google Maps API with enhanced data (ratings, phone, timezone, etc.)")

        self.base_url = "https://maps.googleapis.com/maps/api"

        # Load all company locations for ecosystem density calculation
        self.all_company_locations = []

    def enrich(self, company: Dict, all_companies: Optional[List[Dict]] = None) -> Dict:
        """
        Main enrichment function for geographic data

        Args:
            company: Company data dict
            all_companies: Optional list of all companies for ecosystem density

        Returns:
            Dict with geographic enrichment data
        """
        enrichment_data = {
            "geographic_enrichment_version": self.VERSION,
            "enriched_at": datetime.now().isoformat(),
        }

        # Try to get location from company data
        location_query = self._build_location_query(company)

        if not location_query:
            enrichment_data["status"] = "no_location_data"
            return enrichment_data

        logger.info(f"Enriching geographic data for {company.get('name')}: {location_query}")

        # 1. Get place details from Google Places
        place_data = self._get_place_data(location_query, company.get('name', ''))
        enrichment_data["place_data"] = place_data

        # 2. Calculate startup ecosystem density if we have coordinates
        if place_data.get("coordinates"):
            if all_companies:
                ecosystem_density = self._calculate_ecosystem_density(
                    place_data["coordinates"],
                    all_companies
                )
                enrichment_data["ecosystem_density"] = ecosystem_density

        return enrichment_data

    def _build_location_query(self, company: Dict) -> Optional[str]:
        """Build location query from available company data"""

        # Priority 1: Use all_locations field from YC data
        if company.get('all_locations'):
            return company['all_locations']

        # Priority 2: Use location field if available
        if company.get('location'):
            return company['location']

        # Priority 3: Use city/region
        parts = []
        if company.get('city'):
            parts.append(company['city'])
        if company.get('region'):
            parts.append(company['region'])
        if company.get('country'):
            parts.append(company['country'])

        if parts:
            return ", ".join(parts)

        # Priority 4: Use company name for search
        if company.get('name'):
            return company['name']

        return None

    def _get_place_data(self, query: str, company_name: str = "") -> Dict:
        """Get place data from Google Geocoding API"""

        if not self.api_key:
            return self._basic_geocode(query)

        try:
            # Use Geocoding API (simpler and more reliable for location queries)
            geocode_url = f"{self.base_url}/geocode/json"
            geocode_params = {
                "address": query,
                "key": self.api_key
            }

            response = requests.get(geocode_url, params=geocode_params, timeout=10)
            response.raise_for_status()
            geocode_result = response.json()

            if geocode_result.get("status") != "OK" or not geocode_result.get("results"):
                logger.warning(f"No location found for: {query}")
                return {"status": "not_found", "query": query}

            # Get first result
            result = geocode_result["results"][0]
            location = result["geometry"]["location"]

            # Get timezone
            timezone_data = self._get_timezone(location["lat"], location["lng"])

            return {
                "status": "success",
                "formatted_address": result.get("formatted_address"),
                "coordinates": {
                    "latitude": location["lat"],
                    "longitude": location["lng"]
                },
                "place_types": [t for t in result.get("types", [])],
                "timezone": timezone_data,
                "location_type": result["geometry"].get("location_type"),
                "retrieved_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Google Places API error: {e}")
            return {"status": "error", "error": str(e)[:200]}
        except Exception as e:
            logger.error(f"Unexpected error in place data: {e}")
            return {"status": "error", "error": str(e)[:200]}

    def _get_timezone(self, lat: float, lng: float) -> Dict:
        """Get timezone for coordinates"""

        if not self.api_key:
            return {"status": "no_api_key"}

        try:
            timezone_url = f"{self.base_url}/timezone/json"
            params = {
                "location": f"{lat},{lng}",
                "timestamp": int(time.time()),
                "key": self.api_key
            }

            response = requests.get(timezone_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                return {"status": "error", "error": data.get("status")}

            return {
                "timezone_id": data.get("timeZoneId"),
                "timezone_name": data.get("timeZoneName"),
                "raw_offset": data.get("rawOffset"),
                "dst_offset": data.get("dstOffset")
            }

        except Exception as e:
            logger.warning(f"Timezone lookup failed: {e}")
            return {"status": "error", "error": str(e)[:100]}

    def _basic_geocode(self, query: str) -> Dict:
        """Fallback: Basic geocoding without API key using free service"""
        try:
            # Use Nominatim (OpenStreetMap) as free fallback
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": query,
                "format": "json",
                "limit": 1
            }
            headers = {
                "User-Agent": "YC-Companies-Enricher/1.0"
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            results = response.json()

            if not results:
                return {"status": "not_found", "query": query}

            result = results[0]
            return {
                "status": "success",
                "method": "nominatim_fallback",
                "formatted_address": result.get("display_name"),
                "coordinates": {
                    "latitude": float(result["lat"]),
                    "longitude": float(result["lon"])
                },
                "place_types": [result.get("type")],
                "retrieved_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Basic geocoding failed: {e}")
            return {"status": "error", "error": str(e)[:200]}

    def _calculate_ecosystem_density(self, coordinates: Dict, all_companies: List[Dict]) -> Dict:
        """
        Calculate startup ecosystem density
        Count YC companies within various radii
        """

        lat = coordinates["latitude"]
        lng = coordinates["longitude"]
        origin = (lat, lng)

        # Count companies within different radii
        radii = {
            "1km": 0,
            "5km": 0,
            "10km": 0,
            "25km": 0,
            "50km": 0
        }

        nearby_companies = []

        for other_company in all_companies:
            # Skip if no geographic data
            geo_data = other_company.get('geographic_data', {})
            place_data = geo_data.get('place_data', {})
            other_coords = place_data.get('coordinates')

            if not other_coords:
                continue

            other_lat = other_coords.get('latitude')
            other_lng = other_coords.get('longitude')

            if not other_lat or not other_lng:
                continue

            # Calculate distance
            other_point = (other_lat, other_lng)
            distance_km = geodesic(origin, other_point).kilometers

            # Update radius counts
            if distance_km <= 1:
                radii["1km"] += 1
            if distance_km <= 5:
                radii["5km"] += 1
            if distance_km <= 10:
                radii["10km"] += 1
                nearby_companies.append({
                    "name": other_company.get("name"),
                    "slug": other_company.get("slug"),
                    "batch": other_company.get("batch"),
                    "distance_km": round(distance_km, 2)
                })
            if distance_km <= 25:
                radii["25km"] += 1
            if distance_km <= 50:
                radii["50km"] += 1

        # Sort nearby companies by distance
        nearby_companies.sort(key=lambda x: x["distance_km"])

        return {
            "companies_within": radii,
            "density_score": radii["10km"],  # Simple score: count within 10km
            "nearby_companies": nearby_companies[:20],  # Top 20 closest
            "calculated_at": datetime.now().isoformat()
        }


def main():
    """Test the enricher"""

    # Load companies
    companies_file = Path("/Users/yourox/AI-Workspace/data/yc_companies/all_companies.json")
    with open(companies_file, 'r') as f:
        companies = json.load(f)

    # Test on first 3 companies
    enricher = GeographicEnricher()

    for company in companies[:3]:
        result = enricher.enrich(company, all_companies=companies[:100])
        print(f"\n{'='*70}")
        print(f"Company: {company['name']}")
        print(f"{'='*70}")
        print(json.dumps(result, indent=2))
        print()
        time.sleep(1)  # Rate limiting


if __name__ == "__main__":
    main()
