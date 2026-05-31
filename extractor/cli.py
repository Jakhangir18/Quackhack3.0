"""CLI: extract a de-noised accessibility item list from a URL.

Live (needs `playwright install chromium`):
    python -m extractor.cli https://example.com

Offline (no browser; reads a saved AX-tree JSON):
    python -m extractor.cli sample_tree.json --offline
"""

import argparse
import json
import os
import sys
from urllib.parse import urlparse

from .filter import build_contract


def _load_dotenv(path=".env"):
    if not os.path.exists(path):
        return

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def _dummy_tree(domain=None):
    return {
        "domain": domain,
        "title": "Unavailable",
        "orientation": "Failed to produce website content.",
        "sections": [
            {
                "heading": "Error",
                "items": [
                    {
                        "text": "Content unavailable",
                        "verbatim": "Failed to produce website content.",
                        "role": "status",
                    }
                ],
            }
        ],
    }


def _domain(source):
    parsed = urlparse(source or "")
    return parsed.netloc or source


def main(argv=None):
    _load_dotenv()

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "source", help="page URL, or path to a saved AX-tree JSON with --offline"
    )
    ap.add_argument(
        "--offline",
        action="store_true",
        help="treat source as a local JSON file (no Playwright needed)",
    )
    args = ap.parse_args(argv)

    if args.offline:
        with open(args.source) as f:
            tree = json.load(f)
        url = None
    else:
        from .extract import fetch_ax_tree  # lazy import so offline needs no playwright

        tree = fetch_ax_tree(args.source)
        url = args.source

    contract = build_contract(tree, url=url)
    if os.getenv("GEMINI_API_KEY"):
        from .rank import llm_build_tree

        llm_tree = llm_build_tree(contract["items"], domain=_domain(url))
        if llm_tree is not None:
            json.dump(llm_tree, sys.stdout, indent=2, ensure_ascii=False)
            print()
            return
        print("[cli] LLM tree failed, outputting dummy tree", file=sys.stderr)
        json.dump(_dummy_tree(domain=_domain(url)), sys.stdout, indent=2, ensure_ascii=False)
        print()
        return

    json.dump(contract, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
