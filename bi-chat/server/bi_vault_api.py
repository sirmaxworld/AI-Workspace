#!/usr/bin/env python3
"""
Direct API wrapper for bi-vault data
Bypasses MCP protocol for simpler integration
"""

import sys
import os

# Add the bi-vault directory to the path
sys.path.insert(0, '/Users/yourox/AI-Workspace/mcp-servers/bi-vault')

# Import the BusinessIntelligenceDB directly
import logging

logger = logging.getLogger(__name__)


class BIVaultAPI:
    """Direct API wrapper for bi-vault data"""

    def __init__(self):
        self.db = None
        self._load_database()

    def _load_database(self):
        """Load the BusinessIntelligenceDB directly"""
        try:
            # Set up environment
            os.environ.setdefault('RAILWAY_DATABASE_URL', os.getenv('RAILWAY_DATABASE_URL', ''))

            # Import server module
            from server import BusinessIntelligenceDB

            logger.info("Loading BI Vault database...")
            self.db = BusinessIntelligenceDB()
            logger.info(f"BI Vault loaded: {len(self.db.insights_files)} files")

        except Exception as e:
            logger.error(f"Failed to load BI Vault: {e}")
            self.db = None

    def search_products(self, query: str, limit: int = 20) -> dict:
        """Search products"""
        if not self.db:
            return {"error": "Database not loaded"}

        results = self.db.search(query, "products", {})[:limit]
        return {
            "query": query,
            "count": len(results),
            "results": results
        }

    def search_trends(self, query: str, limit: int = 20) -> dict:
        """Search trends"""
        if not self.db:
            return {"error": "Database not loaded"}

        results = self.db.search(query, "trends", {})[:limit]
        return {
            "query": query,
            "count": len(results),
            "results": results
        }

    def search_startup_ideas(self, query: str, limit: int = 20) -> dict:
        """Search startup ideas"""
        if not self.db:
            return {"error": "Database not loaded"}

        results = self.db.search(query, "startup_ideas", {})[:limit]
        return {
            "query": query,
            "count": len(results),
            "results": results
        }

    def search_growth_tactics(self, query: str, limit: int = 20) -> dict:
        """Search growth tactics"""
        if not self.db:
            return {"error": "Database not loaded"}

        results = self.db.search(query, "growth_tactics", {})[:limit]
        return {
            "query": query,
            "count": len(results),
            "results": results
        }

    def get_stats(self) -> dict:
        """Get database statistics"""
        if not self.db:
            return {"error": "Database not loaded"}

        return self.db.get_stats()

    def search_all(self, query: str, limit: int = 10) -> dict:
        """Search across all categories"""
        if not self.db:
            return {"error": "Database not loaded"}

        categories = ['products', 'problems', 'startup_ideas', 'growth_tactics',
                      'ai_workflows', 'target_markets', 'trends', 'strategies']

        results = {}
        for category in categories:
            category_results = self.db.search(query, category, {})[:limit]
            if category_results:
                results[category] = category_results

        return {
            "query": query,
            "categories_found": len(results),
            "results": results
        }


# Singleton instance
_bi_vault_instance = None


def get_bi_vault() -> BIVaultAPI:
    """Get or create the BI Vault API instance"""
    global _bi_vault_instance
    if _bi_vault_instance is None:
        _bi_vault_instance = BIVaultAPI()
    return _bi_vault_instance
