"""Fetch the accessibility tree for a URL using Playwright (Chromium).

One-time setup on the host machine (NOT needed for --offline mode):
    pip install playwright
    playwright install chromium

Note: page.accessibility.snapshot() was removed in Playwright 1.49+. We now use
page.aria_snapshot() which returns a YAML string in ARIA role syntax. We parse
it back into a dict tree so the rest of the pipeline is unchanged.
"""
import re
import yaml
from playwright.sync_api import sync_playwright


def _yaml_to_tree(node):
    """Convert the parsed ARIA YAML structure into the dict shape filter.py expects."""
    if isinstance(node, str):
        return {"role": "text", "name": node, "children": []}
    if isinstance(node, dict):
        result = {}
        for key, value in node.items():
            # key is like 'heading "Page Title" [level=1]'
            match = re.match(r'(\w+)(?:\s+"([^"]*)")?(?:\s+\[level=(\d+)\])?', key)
            if match:
                result["role"] = match.group(1)
                if match.group(2):
                    result["name"] = match.group(2)
                if match.group(3):
                    result["level"] = int(match.group(3))
            children = value if isinstance(value, list) else ([value] if value else [])
            result["children"] = [_yaml_to_tree(c) for c in children]
            return result
    return {}


def fetch_ax_tree(url, timeout_ms=15000, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            snapshot = page.aria_snapshot()
        finally:
            browser.close()
        parsed = yaml.safe_load(snapshot) if snapshot else {}
        return _yaml_to_tree(parsed) if parsed else {}
