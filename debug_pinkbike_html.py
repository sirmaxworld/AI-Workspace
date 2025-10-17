#!/usr/bin/env python3
"""Debug script to capture Pinkbike HTML for selector analysis"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from browserbase import Browserbase
from playwright.sync_api import sync_playwright

load_dotenv('/Users/yourox/AI-Workspace/.env')

def capture_pinkbike_html(article_url: str):
    """Capture raw HTML from Pinkbike article for analysis"""

    api_key = os.getenv('BROWSERBASE_API_KEY')
    project_id = os.getenv('BROWSERBASE_PROJECT_ID')

    print(f"🌐 Starting Browserbase session...")
    print(f"📄 URL: {article_url}")

    bb = Browserbase(api_key=api_key)
    session = bb.sessions.create(project_id=project_id)
    session_id = session.id

    print(f"✅ Session created: {session_id}")

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(
                f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={session_id}"
            )

            context = browser.contexts[0]
            page = context.pages[0]

            print(f"🔗 Navigating to article...")
            page.goto(article_url, wait_until="domcontentloaded", timeout=30000)

            # Wait for page to fully load
            time.sleep(3)

            print(f"📝 Capturing HTML...")
            html_content = page.content()

            # Save to file
            output_file = Path("/Users/yourox/AI-Workspace/debug_pinkbike_page.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"💾 Saved HTML to: {output_file}")
            print(f"📊 HTML size: {len(html_content):,} chars")

            # Also capture some diagnostic info
            print(f"\n{'='*70}")
            print("🔍 QUICK DIAGNOSTICS")
            print(f"{'='*70}\n")

            # Check for common article containers
            containers = [
                'article',
                'main',
                '.article-body',
                '.post-content',
                '[class*="article"]',
                '[class*="content"]'
            ]

            for selector in containers:
                try:
                    elem = page.locator(selector).first
                    if elem:
                        text = elem.inner_text()[:100]
                        print(f"✅ Found {selector}: {len(text)} chars preview")
                except:
                    print(f"❌ Not found: {selector}")

            return output_file

    finally:
        try:
            bb.sessions.delete(session_id)
            print(f"\n🧹 Session closed")
        except:
            pass

if __name__ == "__main__":
    test_url = "https://www.pinkbike.com/news/review-2024-yt-jeffsy-core-4.html"

    print(f"\n{'='*70}")
    print(f"🔍 PINKBIKE HTML DEBUGGER")
    print(f"{'='*70}\n")

    capture_pinkbike_html(test_url)

    print(f"\n✅ Done! Inspect debug_pinkbike_page.html to find correct selectors")
