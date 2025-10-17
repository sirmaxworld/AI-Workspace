#!/usr/bin/env python3
"""
Enhanced Geographic Data Enricher - Phase 2 v2.0
Multi-source geocoding with smart fallbacks:
1. Static city database (instant, 100% success for common cities)
2. Nominatim/OpenStreetMap (free, 1 req/sec)
3. GeoNames.org (free, 30k req/day, no key needed)
4. Google Maps (if API enabled)
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
import re

# Load environment variables
load_dotenv('/Users/yourox/AI-Workspace/.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Static city database for common YC locations (instant geocoding, no API needed)
CITY_COORDINATES = {
    # California
    "san francisco": {"lat": 37.7749, "lng": -122.4194, "tz": "America/Los_Angeles", "formatted": "San Francisco, CA, USA"},
    "palo alto": {"lat": 37.4419, "lng": -122.1430, "tz": "America/Los_Angeles", "formatted": "Palo Alto, CA, USA"},
    "mountain view": {"lat": 37.3861, "lng": -122.0839, "tz": "America/Los_Angeles", "formatted": "Mountain View, CA, USA"},
    "menlo park": {"lat": 37.4530, "lng": -122.1817, "tz": "America/Los_Angeles", "formatted": "Menlo Park, CA, USA"},
    "redwood city": {"lat": 37.4852, "lng": -122.2364, "tz": "America/Los_Angeles", "formatted": "Redwood City, CA, USA"},
    "san mateo": {"lat": 37.5630, "lng": -122.3255, "tz": "America/Los_Angeles", "formatted": "San Mateo, CA, USA"},
    "berkeley": {"lat": 37.8715, "lng": -122.2730, "tz": "America/Los_Angeles", "formatted": "Berkeley, CA, USA"},
    "oakland": {"lat": 37.8044, "lng": -122.2712, "tz": "America/Los_Angeles", "formatted": "Oakland, CA, USA"},
    "san jose": {"lat": 37.3382, "lng": -121.8863, "tz": "America/Los_Angeles", "formatted": "San Jose, CA, USA"},
    "los angeles": {"lat": 34.0522, "lng": -118.2437, "tz": "America/Los_Angeles", "formatted": "Los Angeles, CA, USA"},
    "santa monica": {"lat": 34.0195, "lng": -118.4912, "tz": "America/Los_Angeles", "formatted": "Santa Monica, CA, USA"},
    "san diego": {"lat": 32.7157, "lng": -117.1611, "tz": "America/Los_Angeles", "formatted": "San Diego, CA, USA"},
    "santa clara": {"lat": 37.3541, "lng": -121.9552, "tz": "America/Los_Angeles", "formatted": "Santa Clara, CA, USA"},
    "sunnyvale": {"lat": 37.3688, "lng": -122.0363, "tz": "America/Los_Angeles", "formatted": "Sunnyvale, CA, USA"},
    "cupertino": {"lat": 37.3230, "lng": -122.0322, "tz": "America/Los_Angeles", "formatted": "Cupertino, CA, USA"},
    "pleasanton": {"lat": 37.6624, "lng": -121.8747, "tz": "America/Los_Angeles", "formatted": "Pleasanton, CA, USA"},
    "los gatos": {"lat": 37.2358, "lng": -121.9619, "tz": "America/Los_Angeles", "formatted": "Los Gatos, CA, USA"},
    "burlingame": {"lat": 37.5847, "lng": -122.3661, "tz": "America/Los_Angeles", "formatted": "Burlingame, CA, USA"},

    # East Coast
    "new york": {"lat": 40.7128, "lng": -74.0060, "tz": "America/New_York", "formatted": "New York, NY, USA"},
    "brooklyn": {"lat": 40.6782, "lng": -73.9442, "tz": "America/New_York", "formatted": "Brooklyn, NY, USA"},
    "boston": {"lat": 42.3601, "lng": -71.0589, "tz": "America/New_York", "formatted": "Boston, MA, USA"},
    "cambridge": {"lat": 42.3736, "lng": -71.1097, "tz": "America/New_York", "formatted": "Cambridge, MA, USA"},
    "washington": {"lat": 38.9072, "lng": -77.0369, "tz": "America/New_York", "formatted": "Washington, DC, USA"},
    "philadelphia": {"lat": 39.9526, "lng": -75.1652, "tz": "America/New_York", "formatted": "Philadelphia, PA, USA"},

    # Other US
    "chicago": {"lat": 41.8781, "lng": -87.6298, "tz": "America/Chicago", "formatted": "Chicago, IL, USA"},
    "austin": {"lat": 30.2672, "lng": -97.7431, "tz": "America/Chicago", "formatted": "Austin, TX, USA"},
    "seattle": {"lat": 47.6062, "lng": -122.3321, "tz": "America/Los_Angeles", "formatted": "Seattle, WA, USA"},
    "denver": {"lat": 39.7392, "lng": -104.9903, "tz": "America/Denver", "formatted": "Denver, CO, USA"},
    "atlanta": {"lat": 33.7490, "lng": -84.3880, "tz": "America/New_York", "formatted": "Atlanta, GA, USA"},
    "miami": {"lat": 25.7617, "lng": -80.1918, "tz": "America/New_York", "formatted": "Miami, FL, USA"},

    # International
    "london": {"lat": 51.5074, "lng": -0.1278, "tz": "Europe/London", "formatted": "London, UK"},
    "paris": {"lat": 48.8566, "lng": 2.3522, "tz": "Europe/Paris", "formatted": "Paris, France"},
    "berlin": {"lat": 52.5200, "lng": 13.4050, "tz": "Europe/Berlin", "formatted": "Berlin, Germany"},
    "tokyo": {"lat": 35.6762, "lng": 139.6503, "tz": "Asia/Tokyo", "formatted": "Tokyo, Japan"},
    "singapore": {"lat": 1.3521, "lng": 103.8198, "tz": "Asia/Singapore", "formatted": "Singapore"},
    "toronto": {"lat": 43.6532, "lng": -79.3832, "tz": "America/Toronto", "formatted": "Toronto, Canada"},
    "bangalore": {"lat": 12.9716, "lng": 77.5946, "tz": "Asia/Kolkata", "formatted": "Bangalore, India"},
    "sydney": {"lat": -33.8688, "lng": 151.2093, "tz": "Australia/Sydney", "formatted": "Sydney, Australia"},
    "tel aviv": {"lat": 32.0853, "lng": 34.7818, "tz": "Asia/Jerusalem", "formatted": "Tel Aviv, Israel"},
    "copenhagen": {"lat": 55.6761, "lng": 12.5683, "tz": "Europe/Copenhagen", "formatted": "Copenhagen, Denmark"},
    "amsterdam": {"lat": 52.3676, "lng": 4.9041, "tz": "Europe/Amsterdam", "formatted": "Amsterdam, Netherlands"},
    "istanbul": {"lat": 41.0082, "lng": 28.9784, "tz": "Europe/Istanbul", "formatted": "Istanbul, Turkey"},
}


class GeographicEnricherV2:
    """Enhanced geocoder with multiple fallback sources"""

    VERSION = "2.0.0"

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.google_enabled = False

        # Test if Google API is working
        if self.api_key:
            self.google_enabled = self._test_google_api()

        if self.google_enabled:
            logger.info("✓ Using Google Maps API with enhanced data")
        else:
            logger.info("✓ Using multi-source free geocoding (Static DB → Nominatim → GeoNames)")
            logger.info("  Static DB: ~50 common YC cities (instant)")
            logger.info("  Nominatim: OpenStreetMap (free, 1 req/sec)")
            logger.info("  GeoNames: Free geocoding API (30k req/day)")

        self.base_url = "https://maps.googleapis.com/maps/api"
        self.last_nominatim_request = 0  # Rate limiting
        self.geocode_cache = {}  # In-memory cache

    def _test_google_api(self) -> bool:
        """Test if Google Geocoding API is enabled"""
        try:
            url = f"{self.base_url}/geocode/json"
            params = {"address": "San Francisco, CA", "key": self.api_key}
            response = requests.get(url, params=params, timeout=5)
            result = response.json()
            return result.get("status") == "OK"
        except:
            return False

    def enrich(self, company: Dict, all_companies: Optional[List[Dict]] = None) -> Dict:
        """Main enrichment function"""
        enrichment_data = {
            "geographic_enrichment_version": self.VERSION,
            "enriched_at": datetime.now().isoformat(),
        }

        location_query = self._build_location_query(company)
        if not location_query:
            enrichment_data["status"] = "no_location_data"
            return enrichment_data

        logger.info(f"Enriching geographic data for {company.get('name')}: {location_query}")

        # Get place data using multi-source approach
        place_data = self._get_place_data_multi_source(location_query, company.get('name', ''))
        enrichment_data["place_data"] = place_data

        # Calculate ecosystem density if we have coordinates
        if place_data.get("coordinates"):
            if all_companies:
                ecosystem_density = self._calculate_ecosystem_density(
                    place_data["coordinates"],
                    all_companies
                )
                enrichment_data["ecosystem_density"] = ecosystem_density

        return enrichment_data

    def _build_location_query(self, company: Dict) -> Optional[str]:
        """Build location query from company data"""
        if company.get('all_locations'):
            return company['all_locations']
        if company.get('location'):
            return company['location']

        parts = []
        if company.get('city'):
            parts.append(company['city'])
        if company.get('region'):
            parts.append(company['region'])
        if company.get('country'):
            parts.append(company['country'])

        if parts:
            return ", ".join(parts)

        if company.get('name'):
            return company['name']

        return None

    def _normalize_location(self, query: str) -> str:
        """Normalize location string for static DB lookup"""
        # Extract city name from complex queries
        query = query.lower().strip()

        # Remove common suffixes
        query = re.sub(r',?\s*(usa|united states|ca|california|ny|new york)\s*', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\s*;\s*remote.*', '', query, flags=re.IGNORECASE)
        query = re.sub(r',?\s*remote\s*', '', query, flags=re.IGNORECASE)

        # Get first part if comma-separated
        if ',' in query:
            query = query.split(',')[0]

        return query.strip()

    def _get_place_data_multi_source(self, query: str, company_name: str = "") -> Dict:
        """
        Try multiple geocoding sources in order:
        1. Static city database (instant, free)
        2. Google Maps (if enabled)
        3. Nominatim/OSM (free, 1 req/sec)
        4. GeoNames (free, 30k/day)
        """

        # Check cache
        cache_key = query.lower().strip()
        if cache_key in self.geocode_cache:
            cached = self.geocode_cache[cache_key].copy()
            cached["from_cache"] = True
            return cached

        # 1. Try static database first (instant)
        normalized_query = self._normalize_location(query)
        if normalized_query in CITY_COORDINATES:
            data = CITY_COORDINATES[normalized_query]
            result = {
                "status": "success",
                "method": "static_db",
                "formatted_address": data["formatted"],
                "coordinates": {
                    "latitude": data["lat"],
                    "longitude": data["lng"]
                },
                "timezone": {
                    "timezone_id": data["tz"],
                    "timezone_name": data["tz"]
                },
                "retrieved_at": datetime.now().isoformat()
            }
            self.geocode_cache[cache_key] = result
            logger.info(f"✓ Found in static DB: {normalized_query}")
            return result

        # 2. Try Google Maps if enabled
        if self.google_enabled:
            result = self._geocode_google(query)
            if result.get("status") == "success":
                self.geocode_cache[cache_key] = result
                return result

        # 3. Try Nominatim (OpenStreetMap)
        result = self._geocode_nominatim(query)
        if result.get("status") == "success":
            self.geocode_cache[cache_key] = result
            return result

        # 4. Try GeoNames as last resort
        result = self._geocode_geonames(query)
        if result.get("status") == "success":
            self.geocode_cache[cache_key] = result
            return result

        # All methods failed
        return {"status": "not_found", "query": query, "methods_tried": ["static_db", "nominatim", "geonames"]}

    def _geocode_google(self, query: str) -> Dict:
        """Geocode using Google Maps API"""
        try:
            url = f"{self.base_url}/geocode/json"
            params = {"address": query, "key": self.api_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK" or not data.get("results"):
                return {"status": "not_found"}

            result = data["results"][0]
            location = result["geometry"]["location"]

            return {
                "status": "success",
                "method": "google_maps",
                "formatted_address": result.get("formatted_address"),
                "coordinates": {
                    "latitude": location["lat"],
                    "longitude": location["lng"]
                },
                "place_types": result.get("types", []),
                "retrieved_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.debug(f"Google geocoding failed: {e}")
            return {"status": "error", "error": str(e)[:200]}

    def _geocode_nominatim(self, query: str) -> Dict:
        """Geocode using Nominatim (OpenStreetMap) with rate limiting"""
        try:
            # Rate limit: 1 request per second
            current_time = time.time()
            time_since_last = current_time - self.last_nominatim_request
            if time_since_last < 1.0:
                time.sleep(1.0 - time_since_last)

            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": query,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            headers = {
                "User-Agent": "YC-Companies-Enricher/2.0 (https://github.com/yourox)"
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            self.last_nominatim_request = time.time()

            response.raise_for_status()
            results = response.json()

            if not results:
                return {"status": "not_found"}

            result = results[0]
            return {
                "status": "success",
                "method": "nominatim",
                "formatted_address": result.get("display_name"),
                "coordinates": {
                    "latitude": float(result["lat"]),
                    "longitude": float(result["lon"])
                },
                "place_types": [result.get("type")],
                "retrieved_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.debug(f"Nominatim geocoding failed: {e}")
            return {"status": "error", "error": str(e)[:200]}

    def _geocode_geonames(self, query: str) -> Dict:
        """Geocode using GeoNames.org free API (no key required)"""
        try:
            url = "http://api.geonames.org/searchJSON"
            params = {
                "q": query,
                "maxRows": 1,
                "username": "yc_companies_enricher",  # Free demo account
                "style": "FULL"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("geonames"):
                return {"status": "not_found"}

            result = data["geonames"][0]
            return {
                "status": "success",
                "method": "geonames",
                "formatted_address": f"{result.get('name')}, {result.get('countryName')}",
                "coordinates": {
                    "latitude": float(result["lat"]),
                    "longitude": float(result["lng"])
                },
                "place_types": [result.get("fcode")],
                "timezone": {
                    "timezone_id": result.get("timezone", {}).get("timeZoneId")
                },
                "retrieved_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.debug(f"GeoNames geocoding failed: {e}")
            return {"status": "error", "error": str(e)[:200]}

    def _calculate_ecosystem_density(self, coordinates: Dict, all_companies: List[Dict]) -> Dict:
        """Calculate startup ecosystem density"""
        lat = coordinates["latitude"]
        lng = coordinates["longitude"]
        origin = (lat, lng)

        radii = {"1km": 0, "5km": 0, "10km": 0, "25km": 0, "50km": 0}
        nearby_companies = []

        for other_company in all_companies:
            geo_data = other_company.get('geographic_data', {})
            place_data = geo_data.get('place_data', {})
            other_coords = place_data.get('coordinates')

            if not other_coords:
                continue

            other_lat = other_coords.get('latitude')
            other_lng = other_coords.get('longitude')

            if not other_lat or not other_lng:
                continue

            other_point = (other_lat, other_lng)
            distance_km = geodesic(origin, other_point).kilometers

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

        nearby_companies.sort(key=lambda x: x["distance_km"])

        return {
            "companies_within": radii,
            "density_score": radii["10km"],
            "nearby_companies": nearby_companies[:20],
            "calculated_at": datetime.now().isoformat()
        }


def main():
    """Test the enhanced enricher"""
    companies_file = Path("/Users/yourox/AI-Workspace/data/yc_companies/all_companies.json")
    with open(companies_file, 'r') as f:
        companies = json.load(f)

    enricher = GeographicEnricherV2()

    # Test on various location types
    test_companies = [
        companies[0],  # CircuitHub - London
        companies[1],  # iCracked - Redwood City
        companies[2],  # 42Floors - San Francisco
    ]

    for company in test_companies:
        result = enricher.enrich(company, all_companies=companies[:100])
        print(f"\n{'='*70}")
        print(f"Company: {company['name']}")
        print(f"Location: {company.get('all_locations', company.get('location', 'N/A'))}")
        print(f"{'='*70}")
        print(json.dumps(result, indent=2))
        print()


if __name__ == "__main__":
    main()
