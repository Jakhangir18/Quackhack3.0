"""Fetch the accessibility tree for a URL using Playwright (Chromium).

One-time setup on the host machine (NOT needed for --offline mode):
    pip install playwright
    playwright install chromium

Note: page.accessibility.snapshot() is the classic API and returns clean JSON,
which is the easiest thing to hand an LLM. Playwright's newer aria_snapshot()
returns YAML and is aimed at testing; the 'AI snapshot' variant also embeds
element refs (e.g. [ref=e2]) that let an agent act on specific nodes later.
Start with snapshot(); switch only if you hit its limits.
"""
from playwright.sync_api import sync_playwright


def fetch_ax_tree(url, timeout_ms=15000, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            # interesting_only=True (default) prunes presentational nodes for us.
            tree = page.accessibility.snapshot(interesting_only=True)
        finally:
            browser.close()
        return tree or {}
