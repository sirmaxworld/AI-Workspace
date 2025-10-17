#!/usr/bin/env python3
"""
Test all data sources with different companies
If any source fails 3 times, it will be disabled
"""

import json
from pathlib import Path
from web_data_enricher import WebDataEnricher

def test_data_sources():
    """Test each data source with 3 different companies"""

    # Load companies
    companies_file = Path("/Users/yourox/AI-Workspace/data/yc_companies/all_companies.json")
    with open(companies_file, 'r') as f:
        companies = json.load(f)

    # Get 3 test companies with websites from different batches
    test_companies = []
    for company in companies:
        if company.get('website') and len(test_companies) < 3:
            test_companies.append(company)

    enricher = WebDataEnricher()

    # Test results
    results = {
        "website_status": {"success": 0, "fail": 0},
        "ssl_security": {"success": 0, "fail": 0},
        "domain_info": {"success": 0, "fail": 0},
        "social_links": {"success": 0, "fail": 0},
        "security_headers": {"success": 0, "fail": 0}
    }

    print("\n" + "="*70)
    print("🧪 TESTING DATA SOURCES")
    print("="*70 + "\n")

    for i, company in enumerate(test_companies, 1):
        print(f"\nTest {i}/3: {company['name']} ({company['website']})")
        print("-" * 70)

        # Test website status
        try:
            status = enricher.check_website_status(company['website'])
            if status.get('reachable'):
                results["website_status"]["success"] += 1
                print(f"  ✅ Website Status: {status['status_code']} in {status['response_time_ms']}ms")
            else:
                results["website_status"]["fail"] += 1
                print(f"  ⚠️  Website Status: {status.get('error', 'unreachable')}")
        except Exception as e:
            results["website_status"]["fail"] += 1
            print(f"  ❌ Website Status: {str(e)[:50]}")

        # Test SSL
        try:
            ssl = enricher.check_ssl_security(company['website'])
            if ssl.get('valid'):
                results["ssl_security"]["success"] += 1
                print(f"  ✅ SSL Security: Valid until {ssl['valid_until'][:10]}")
            else:
                results["ssl_security"]["fail"] += 1
                print(f"  ⚠️  SSL Security: {ssl.get('error', 'invalid')[:50]}")
        except Exception as e:
            results["ssl_security"]["fail"] += 1
            print(f"  ❌ SSL Security: {str(e)[:50]}")

        # Test domain info
        try:
            domain = enricher.get_domain_info(company['website'])
            if domain.get('domain_age_years'):
                results["domain_info"]["success"] += 1
                print(f"  ✅ Domain Info: {domain['domain_age_years']} years old")
            else:
                results["domain_info"]["fail"] += 1
                print(f"  ⚠️  Domain Info: {domain.get('error', 'no age data')[:50]}")
        except Exception as e:
            results["domain_info"]["fail"] += 1
            print(f"  ❌ Domain Info: {str(e)[:50]}")

        # Test social links
        try:
            social = enricher.extract_social_links(company['website'])
            found = sum(1 for v in social.values() if v)
            if found > 0:
                results["social_links"]["success"] += 1
                print(f"  ✅ Social Links: Found {found}/6 platforms")
            else:
                results["social_links"]["fail"] += 1
                print(f"  ⚠️  Social Links: None found")
        except Exception as e:
            results["social_links"]["fail"] += 1
            print(f"  ❌ Social Links: {str(e)[:50]}")

        # Test security headers
        try:
            headers = enricher.get_security_headers(company['website'])
            if 'security_score' in headers:
                results["security_headers"]["success"] += 1
                print(f"  ✅ Security Headers: Score {headers['security_score']}/100")
            else:
                results["security_headers"]["fail"] += 1
                print(f"  ⚠️  Security Headers: {headers.get('error', 'no score')[:50]}")
        except Exception as e:
            results["security_headers"]["fail"] += 1
            print(f"  ❌ Security Headers: {str(e)[:50]}")

    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70 + "\n")

    disabled_sources = []
    for source, stats in results.items():
        total = stats['success'] + stats['fail']
        success_rate = (stats['success'] / total * 100) if total > 0 else 0

        status = "✅ ENABLED" if stats['success'] >= 1 else "❌ DISABLED"
        if stats['success'] < 1:
            disabled_sources.append(source)

        print(f"{source:20s}: {stats['success']}/3 success ({success_rate:.0f}%) - {status}")

    print("\n" + "="*70)

    if disabled_sources:
        print(f"\n⚠️  {len(disabled_sources)} source(s) will be DISABLED:")
        for source in disabled_sources:
            print(f"   - {source}")
        print("\nEnrichment will continue with working sources only.")
    else:
        print("\n✅ All data sources working! Ready for full enrichment.")

    print("\n" + "="*70 + "\n")

    return results, disabled_sources


if __name__ == "__main__":
    test_data_sources()
