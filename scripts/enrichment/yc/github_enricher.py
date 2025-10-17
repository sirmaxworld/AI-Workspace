#!/usr/bin/env python3
"""
GitHub/Technical Data Enricher - Phase 3
Uses GitHub API (free: 5,000 requests/hour) to add:
- Repository statistics (stars, forks, watchers)
- Programming languages used
- Recent activity
- Organization member count
- Popular repositories
- Package registry presence (NPM, PyPI, RubyGems, etc.)
"""

import os
import requests
import json
from typing import Dict, Optional, List
from datetime import datetime
import logging
import time
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/yourox/AI-Workspace/.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubEnricher:
    """Enriches YC companies with GitHub and technical data"""

    VERSION = "1.0.0"

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()

        if self.github_token:
            self.session.headers.update({
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            })
            logger.info("Using authenticated GitHub API (5,000 req/hr)")
        else:
            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json"
            })
            logger.warning("No GITHUB_TOKEN found. Using unauthenticated API (60 req/hr)")

    def enrich(self, company: Dict) -> Dict:
        """
        Main enrichment function for GitHub/technical data

        Args:
            company: Company data dict with social_links or website

        Returns:
            Dict with GitHub enrichment data
        """
        enrichment_data = {
            "github_enrichment_version": self.VERSION,
            "enriched_at": datetime.now().isoformat(),
        }

        # Extract GitHub info from social links (from Phase 1)
        web_data = company.get('web_data', {})
        social_links = web_data.get('social_links', {})
        github_url = social_links.get('github')

        if not github_url:
            enrichment_data["status"] = "no_github_link"
            return enrichment_data

        logger.info(f"Enriching GitHub data for {company.get('name')}: {github_url}")

        # Extract org/user from GitHub URL
        org_name = self._extract_github_org(github_url)

        if not org_name:
            enrichment_data["status"] = "invalid_github_url"
            enrichment_data["github_url"] = github_url
            return enrichment_data

        # 1. Get organization info
        org_data = self._get_org_data(org_name)
        enrichment_data["organization"] = org_data

        # 2. Get repositories
        if org_data.get("status") == "success":
            repos_data = self._get_repositories(org_name)
            enrichment_data["repositories"] = repos_data

            # 3. Analyze tech stack from repos
            if repos_data.get("repositories"):
                tech_stack = self._analyze_tech_stack(repos_data["repositories"])
                enrichment_data["tech_stack"] = tech_stack

        # 4. Check package registries
        package_data = self._check_package_registries(org_name, company.get('name', ''))
        enrichment_data["packages"] = package_data

        return enrichment_data

    def _extract_github_org(self, github_url: str) -> Optional[str]:
        """Extract organization/user name from GitHub URL"""
        try:
            parsed = urlparse(github_url)
            path_parts = [p for p in parsed.path.split('/') if p]

            if len(path_parts) >= 1:
                return path_parts[0]

            return None
        except Exception as e:
            logger.warning(f"Failed to parse GitHub URL {github_url}: {e}")
            return None

    def _get_org_data(self, org_name: str) -> Dict:
        """Get GitHub organization data"""
        try:
            url = f"https://api.github.com/orgs/{org_name}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 404:
                # Try as user instead
                return self._get_user_data(org_name)

            response.raise_for_status()
            data = response.json()

            return {
                "status": "success",
                "type": "organization",
                "name": data.get("name"),
                "login": data.get("login"),
                "description": data.get("description"),
                "public_repos": data.get("public_repos", 0),
                "followers": data.get("followers", 0),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "html_url": data.get("html_url"),
                "blog": data.get("blog"),
                "email": data.get("email"),
                "twitter_username": data.get("twitter_username"),
                "verified": data.get("is_verified", False),
                "has_organization_projects": data.get("has_organization_projects", False),
                "has_repository_projects": data.get("has_repository_projects", False)
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                return {"status": "rate_limited", "error": "GitHub API rate limit exceeded"}
            return {"status": "error", "error": str(e)[:200]}
        except Exception as e:
            logger.error(f"Failed to get org data for {org_name}: {e}")
            return {"status": "error", "error": str(e)[:200]}

    def _get_user_data(self, username: str) -> Dict:
        """Get GitHub user data (for personal accounts)"""
        try:
            url = f"https://api.github.com/users/{username}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                "status": "success",
                "type": "user",
                "name": data.get("name"),
                "login": data.get("login"),
                "bio": data.get("bio"),
                "public_repos": data.get("public_repos", 0),
                "followers": data.get("followers", 0),
                "following": data.get("following", 0),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "html_url": data.get("html_url"),
                "blog": data.get("blog"),
                "twitter_username": data.get("twitter_username"),
                "company": data.get("company")
            }

        except Exception as e:
            logger.error(f"Failed to get user data for {username}: {e}")
            return {"status": "error", "error": str(e)[:200]}

    def _get_repositories(self, org_name: str, max_repos: int = 100) -> Dict:
        """Get repositories for organization/user"""
        try:
            # Try org repos first
            url = f"https://api.github.com/orgs/{org_name}/repos"
            params = {
                "sort": "updated",
                "per_page": min(max_repos, 100),
                "type": "public"
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 404:
                # Try user repos
                url = f"https://api.github.com/users/{org_name}/repos"
                response = self.session.get(url, params=params, timeout=10)

            response.raise_for_status()
            repos = response.json()

            # Process repositories
            processed_repos = []
            total_stars = 0
            total_forks = 0
            total_watchers = 0
            languages = {}

            for repo in repos[:max_repos]:
                repo_data = {
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description"),
                    "html_url": repo["html_url"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "watchers": repo["watchers_count"],
                    "language": repo.get("language"),
                    "topics": repo.get("topics", []),
                    "created_at": repo["created_at"],
                    "updated_at": repo["updated_at"],
                    "pushed_at": repo.get("pushed_at"),
                    "size": repo["size"],
                    "archived": repo.get("archived", False),
                    "disabled": repo.get("disabled", False),
                    "open_issues": repo.get("open_issues_count", 0),
                    "license": repo.get("license", {}).get("spdx_id") if repo.get("license") else None,
                    "has_wiki": repo.get("has_wiki", False),
                    "has_pages": repo.get("has_pages", False)
                }

                processed_repos.append(repo_data)

                # Aggregate stats
                total_stars += repo["stargazers_count"]
                total_forks += repo["forks_count"]
                total_watchers += repo["watchers_count"]

                # Track languages
                if repo.get("language"):
                    languages[repo["language"]] = languages.get(repo["language"], 0) + 1

            # Sort languages by frequency
            sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)

            # Get top repositories by stars
            top_repos = sorted(processed_repos, key=lambda x: x["stars"], reverse=True)[:5]

            # Count active repos (updated in last 6 months)
            six_months_ago = datetime.now().timestamp() - (6 * 30 * 24 * 60 * 60)
            active_repos = sum(1 for r in processed_repos
                             if datetime.fromisoformat(r["updated_at"].replace('Z', '+00:00')).timestamp() > six_months_ago)

            return {
                "status": "success",
                "total_repos": len(processed_repos),
                "total_stars": total_stars,
                "total_forks": total_forks,
                "total_watchers": total_watchers,
                "active_repos": active_repos,
                "archived_repos": sum(1 for r in processed_repos if r["archived"]),
                "languages": sorted_languages,
                "primary_language": sorted_languages[0][0] if sorted_languages else None,
                "top_repositories": top_repos,
                "repositories": processed_repos,
                "retrieved_at": datetime.now().isoformat()
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                return {"status": "rate_limited", "error": "GitHub API rate limit exceeded"}
            return {"status": "error", "error": str(e)[:200]}
        except Exception as e:
            logger.error(f"Failed to get repositories for {org_name}: {e}")
            return {"status": "error", "error": str(e)[:200]}

    def _analyze_tech_stack(self, repositories: List[Dict]) -> Dict:
        """Analyze technology stack from repositories"""

        languages = {}
        frameworks = []
        build_tools = []
        licenses = {}
        topics = set()

        for repo in repositories:
            # Language analysis
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + repo.get("stars", 1)

            # Topics
            if repo.get("topics"):
                topics.update(repo["topics"])

            # License tracking
            license_type = repo.get("license")
            if license_type:
                licenses[license_type] = licenses.get(license_type, 0) + 1

        # Sort languages by weighted stars
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)

        # Calculate language percentages (weighted by stars)
        total_weight = sum(languages.values())
        language_percentages = {
            lang: round((weight / total_weight) * 100, 1)
            for lang, weight in sorted_languages
        } if total_weight > 0 else {}

        return {
            "languages_weighted": sorted_languages[:10],
            "language_percentages": language_percentages,
            "primary_language": sorted_languages[0][0] if sorted_languages else None,
            "topics": list(topics),
            "licenses": sorted(licenses.items(), key=lambda x: x[1], reverse=True),
            "tech_diversity_score": len(languages),  # Number of different languages used
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _check_package_registries(self, org_name: str, company_name: str) -> Dict:
        """Check various package registries for published packages"""

        packages = {
            "npm": self._check_npm(org_name, company_name),
            "pypi": self._check_pypi(org_name, company_name),
            "rubygems": self._check_rubygems(org_name, company_name),
            "crates_io": self._check_crates_io(org_name, company_name)
        }

        total_packages = sum(
            p.get("package_count", 0)
            for p in packages.values()
            if isinstance(p.get("package_count"), int)
        )

        return {
            **packages,
            "total_packages": total_packages,
            "has_packages": total_packages > 0,
            "checked_at": datetime.now().isoformat()
        }

    def _check_npm(self, org_name: str, company_name: str) -> Dict:
        """Check NPM registry"""
        try:
            # Try organization scope first
            url = f"https://registry.npmjs.org/-/v1/search"
            params = {
                "text": f"@{org_name}",
                "size": 100
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            packages = [
                {
                    "name": pkg["package"]["name"],
                    "description": pkg["package"].get("description"),
                    "version": pkg["package"]["version"],
                    "downloads": pkg.get("score", {}).get("detail", {}).get("popularity"),
                    "url": pkg["package"]["links"]["npm"]
                }
                for pkg in data.get("objects", [])
            ]

            return {
                "status": "success",
                "package_count": len(packages),
                "packages": packages
            }

        except Exception as e:
            return {"status": "error", "error": str(e)[:100]}

    def _check_pypi(self, org_name: str, company_name: str) -> Dict:
        """Check PyPI registry"""
        try:
            # Search by organization/company name
            url = "https://pypi.org/search/"
            params = {"q": company_name or org_name}

            response = requests.get(url, params=params, timeout=10, headers={
                "User-Agent": "YC-Companies-Enricher/1.0"
            })

            if response.status_code == 200:
                # Simple check if search returned results
                has_results = company_name.lower() in response.text.lower() or org_name.lower() in response.text.lower()
                return {
                    "status": "checked",
                    "has_packages": has_results,
                    "note": "PyPI checked via search (detailed scraping not implemented)"
                }

            return {"status": "error", "error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"status": "error", "error": str(e)[:100]}

    def _check_rubygems(self, org_name: str, company_name: str) -> Dict:
        """Check RubyGems registry"""
        try:
            url = f"https://rubygems.org/api/v1/search.json"
            params = {"query": org_name}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            gems = response.json()

            packages = [
                {
                    "name": gem["name"],
                    "version": gem.get("version"),
                    "downloads": gem.get("downloads"),
                    "url": f"https://rubygems.org/gems/{gem['name']}"
                }
                for gem in gems[:20]
            ]

            return {
                "status": "success",
                "package_count": len(packages),
                "packages": packages
            }

        except Exception as e:
            return {"status": "error", "error": str(e)[:100]}

    def _check_crates_io(self, org_name: str, company_name: str) -> Dict:
        """Check Rust crates.io registry"""
        try:
            url = "https://crates.io/api/v1/crates"
            params = {"q": org_name}
            headers = {"User-Agent": "YC-Companies-Enricher/1.0"}

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            crates = [
                {
                    "name": crate["name"],
                    "description": crate.get("description"),
                    "version": crate.get("newest_version"),
                    "downloads": crate.get("downloads"),
                    "url": f"https://crates.io/crates/{crate['name']}"
                }
                for crate in data.get("crates", [])[:20]
            ]

            return {
                "status": "success",
                "package_count": len(crates),
                "packages": crates
            }

        except Exception as e:
            return {"status": "error", "error": str(e)[:100]}


def main():
    """Test the enricher"""

    # Load companies with GitHub links
    import sys
    sys.path.append('/Users/yourox/AI-Workspace/scripts/enrichment/yc')

    companies_file = "/Users/yourox/AI-Workspace/data/yc_enriched/stripe_enriched.json"

    with open(companies_file, 'r') as f:
        company = json.load(f)

    enricher = GitHubEnricher()
    result = enricher.enrich(company)

    print(f"\n{'='*70}")
    print(f"Company: {company['name']}")
    print(f"{'='*70}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
