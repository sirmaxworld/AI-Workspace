#!/usr/bin/env python3
"""
Simple proxy rotation manager for YouTube downloads
"""
import requests
from typing import List, Dict, Optional
import random
import time

class ProxyManager:
    def __init__(self):
        self.proxies: List[Dict[str, str]] = []
        self.current_index = 0
        self.failed_proxies = set()

    def fetch_free_proxies(self) -> List[str]:
        """Fetch free proxies from multiple sources"""
        proxies = []

        # Source 1: Free Proxy List
        try:
            response = requests.get('https://www.proxy-list.download/api/v1/get?type=http', timeout=10)
            if response.status_code == 200:
                proxies.extend(response.text.strip().split('\n'))
        except:
            pass

        # Source 2: ProxyScrape
        try:
            response = requests.get('https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all', timeout=10)
            if response.status_code == 200:
                proxies.extend(response.text.strip().split('\n'))
        except:
            pass

        return list(set(proxies))[:50]  # Get top 50 unique proxies

    def test_proxy(self, proxy: str) -> bool:
        """Test if a proxy is working"""
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }

        try:
            response = requests.get('https://www.google.com', proxies=proxies, timeout=5)
            return response.status_code == 200
        except:
            return False

    def load_proxies(self, test: bool = True):
        """Load and optionally test proxies"""
        print("Fetching proxies...")
        proxy_list = self.fetch_free_proxies()
        print(f"Found {len(proxy_list)} proxies")

        if test:
            print("Testing proxies...")
            working_proxies = []
            for proxy in proxy_list[:20]:  # Test first 20
                if self.test_proxy(proxy):
                    working_proxies.append({
                        'http': f'http://{proxy}',
                        'https': f'http://{proxy}'
                    })
                    print(f"✓ {proxy}")
                if len(working_proxies) >= 5:  # Get at least 5 working proxies
                    break

            self.proxies = working_proxies
            print(f"Loaded {len(self.proxies)} working proxies")
        else:
            self.proxies = [{'http': f'http://{p}', 'https': f'http://{p}'} for p in proxy_list]

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get next working proxy"""
        if not self.proxies:
            return None

        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)

            if str(proxy) not in self.failed_proxies:
                return proxy

            attempts += 1

        return None

    def mark_failed(self, proxy: Dict[str, str]):
        """Mark a proxy as failed"""
        self.failed_proxies.add(str(proxy))

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)

# Standalone usage
if __name__ == '__main__':
    manager = ProxyManager()
    manager.load_proxies(test=True)

    if manager.proxies:
        print("\n✅ Proxy manager ready!")
        print(f"Available proxies: {len(manager.proxies)}")
        print("\nSample proxy:")
        print(manager.get_proxy())
    else:
        print("\n❌ No working proxies found")
