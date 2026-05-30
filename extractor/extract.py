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

# Matches: role "name" [level=N]  — name and level are optional
_KEY_RE = re.compile(r'^(\w+)(?:\s+"([^"]*)")?(?:\s+\[level=(\d+)\])?')


def _parse_node(key, value):
    """Turn one ARIA YAML key+value into the dict shape filter.py expects."""
    m = _KEY_RE.match(key)
    node = {"role": m.group(1) if m else "generic", "children": []}
    if m and m.group(2):
        node["name"] = m.group(2)
    if m and m.group(3):
        node["level"] = int(m.group(3))

    children = value if isinstance(value, list) else ([value] if value is not None else [])
    for child in children:
        if isinstance(child, str):
            node["children"].append({"role": "text", "name": child, "children": []})
        elif isinstance(child, dict):
            for ck, cv in child.items():
                node["children"].append(_parse_node(ck, cv))
    return node


def fetch_ax_tree(url, timeout_ms=15000, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            snapshot = page.aria_snapshot()
        finally:
            browser.close()

    parsed = yaml.safe_load(snapshot) if snapshot else []
    # aria_snapshot() always returns a top-level list; wrap in a root node
    root_children = []
    for item in (parsed or []):
        if isinstance(item, str):
            root_children.append({"role": "text", "name": item, "children": []})
        elif isinstance(item, dict):
            for k, v in item.items():
                root_children.append(_parse_node(k, v))
    return {"role": "document", "name": "", "children": root_children}
