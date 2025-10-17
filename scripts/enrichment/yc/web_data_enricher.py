#!/usr/bin/env python3
"""
Web Data Enricher - Phase 1
Free/Public data sources for YC companies:
- Website status and SSL validation
- Domain age and registration info
- Social media link extraction
- Security headers analysis
"""

import requests
import socket
import ssl
import whois
from datetime import datetime
from typing import Dict, Optional, List
from urllib.parse import urlparse
import logging
import time
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebDataEnricher:
    """Enriches YC companies with web and domain data"""

    VERSION = "1.0.0"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def enrich(self, company: Dict) -> Dict:
        """
        Main enrichment function for a single company

        Args:
            company: Company data dict with 'website' field

        Returns:
            Dict with enrichment data
        """
        website = company.get('website', '').strip()

        if not website:
            return {
                "web_enrichment_version": self.VERSION,
                "enriched_at": datetime.now().isoformat(),
                "status": "no_website"
            }

        logger.info(f"Enriching {company.get('name')}: {website}")

        enrichment_data = {
            "web_enrichment_version": self.VERSION,
            "enriched_at": datetime.now().isoformat(),
            "website": website
        }

        # 1. Website status and performance
        website_status = self.check_website_status(website)
        enrichment_data["website_status"] = website_status

        # 2. SSL/Security (DISABLED - certificate verification issues)
        # ssl_info = self.check_ssl_security(website)
        # enrichment_data["ssl_security"] = ssl_info
        enrichment_data["ssl_security"] = {"disabled": True, "reason": "certificate_verification_failed"}

        # 3. Domain information (WHOIS)
        domain_info = self.get_domain_info(website)
        enrichment_data["domain_info"] = domain_info

        # 4. Extract social media links
        social_links = self.extract_social_links(website)
        enrichment_data["social_links"] = social_links

        # 5. Security headers
        security_headers = self.get_security_headers(website)
        enrichment_data["security_headers"] = security_headers

        return enrichment_data

    def check_website_status(self, url: str) -> Dict:
        """Check if website is reachable and get status"""
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response_time = time.time() - start_time

            return {
                "reachable": True,
                "status_code": response.status_code,
                "response_time_ms": round(response_time * 1000, 2),
                "final_url": response.url,
                "redirected": response.url != url,
                "checked_at": datetime.now().isoformat()
            }
        except requests.exceptions.Timeout:
            return {"reachable": False, "error": "timeout"}
        except requests.exceptions.SSLError:
            return {"reachable": False, "error": "ssl_error"}
        except requests.exceptions.ConnectionError:
            return {"reachable": False, "error": "connection_error"}
        except Exception as e:
            return {"reachable": False, "error": str(e)[:200]}

    def check_ssl_security(self, url: str) -> Dict:
        """Check SSL certificate validity"""
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path

        # Remove www. prefix if present
        hostname = hostname.replace('www.', '')

        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

                    # Parse cert dates
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')

                    days_until_expiry = (not_after - datetime.now()).days

                    return {
                        "valid": True,
                        "issuer": dict(x[0] for x in cert['issuer']).get('organizationName', 'Unknown'),
                        "subject": dict(x[0] for x in cert['subject']).get('commonName', 'Unknown'),
                        "valid_from": not_before.isoformat(),
                        "valid_until": not_after.isoformat(),
                        "days_until_expiry": days_until_expiry,
                        "is_expired": days_until_expiry < 0
                    }
        except ssl.SSLError as e:
            return {"valid": False, "error": f"ssl_error: {str(e)[:100]}"}
        except socket.timeout:
            return {"valid": False, "error": "timeout"}
        except Exception as e:
            return {"valid": False, "error": str(e)[:100]}

    def get_domain_info(self, url: str) -> Dict:
        """Get WHOIS domain information"""
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        domain = domain.replace('www.', '')

        try:
            w = whois.whois(domain)

            # Handle creation_date (can be list or single value)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            if creation_date:
                # Handle timezone-aware datetime
                if creation_date.tzinfo:
                    creation_date = creation_date.replace(tzinfo=None)
                domain_age_days = (datetime.now() - creation_date).days
                domain_age_years = round(domain_age_days / 365.25, 1)
            else:
                domain_age_days = None
                domain_age_years = None

            # Handle expiration date
            exp_date = None
            if isinstance(w.expiration_date, list) and w.expiration_date:
                exp_date = w.expiration_date[0]
            elif w.expiration_date:
                exp_date = w.expiration_date

            if exp_date and hasattr(exp_date, 'tzinfo') and exp_date.tzinfo:
                exp_date = exp_date.replace(tzinfo=None)

            return {
                "domain": domain,
                "registrar": w.registrar,
                "creation_date": creation_date.isoformat() if creation_date else None,
                "expiration_date": exp_date.isoformat() if exp_date else None,
                "domain_age_days": domain_age_days,
                "domain_age_years": domain_age_years,
                "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else []
            }
        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {e}")
            return {
                "domain": domain,
                "error": str(e)[:200]
            }

    def extract_social_links(self, url: str) -> Dict:
        """Extract social media links from website"""
        social_links = {
            "twitter": None,
            "linkedin": None,
            "github": None,
            "facebook": None,
            "instagram": None,
            "youtube": None
        }

        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links
            all_links = soup.find_all('a', href=True)

            for link in all_links:
                href = link['href'].lower()

                if 'twitter.com/' in href or 'x.com/' in href:
                    social_links["twitter"] = link['href']
                elif 'linkedin.com/company/' in href:
                    social_links["linkedin"] = link['href']
                elif 'github.com/' in href:
                    social_links["github"] = link['href']
                elif 'facebook.com/' in href:
                    social_links["facebook"] = link['href']
                elif 'instagram.com/' in href:
                    social_links["instagram"] = link['href']
                elif 'youtube.com/' in href:
                    social_links["youtube"] = link['href']

            return social_links
        except Exception as e:
            logger.warning(f"Failed to extract social links from {url}: {e}")
            return social_links

    def get_security_headers(self, url: str) -> Dict:
        """Analyze security headers"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            headers = response.headers

            security_checks = {
                "strict_transport_security": bool(headers.get('Strict-Transport-Security')),
                "content_security_policy": bool(headers.get('Content-Security-Policy')),
                "x_frame_options": bool(headers.get('X-Frame-Options')),
                "x_content_type_options": bool(headers.get('X-Content-Type-Options')),
                "x_xss_protection": bool(headers.get('X-XSS-Protection')),
                "referrer_policy": bool(headers.get('Referrer-Policy'))
            }

            # Calculate security score (0-100)
            security_score = int((sum(security_checks.values()) / len(security_checks)) * 100)

            return {
                **security_checks,
                "security_score": security_score,
                "server": headers.get('Server', 'Unknown')
            }
        except Exception as e:
            logger.warning(f"Failed to get security headers for {url}: {e}")
            return {"error": str(e)[:100]}


def main():
    """Test the enricher"""
    import json
    from pathlib import Path

    # Load a sample company
    companies_file = Path("/Users/yourox/AI-Workspace/data/yc_companies/all_companies.json")
    with open(companies_file, 'r') as f:
        companies = json.load(f)

    # Test on first 5 companies with websites
    enricher = WebDataEnricher()

    for company in companies[:5]:
        if company.get('website'):
            result = enricher.enrich(company)
            print(f"\n{'='*70}")
            print(f"Company: {company['name']}")
            print(f"{'='*70}")
            print(json.dumps(result, indent=2))
            print()


if __name__ == "__main__":
    main()
