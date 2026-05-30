"""CLI: extract a de-noised accessibility item list from a URL.

  Live (needs `playwright install chromium`):
      python -m extractor.cli https://example.com --rank

  Offline (no browser; reads a saved AX-tree JSON):
      python -m extractor.cli sample_tree.json --offline --rank
"""
import argparse
import json
import sys

from .filter import build_contract


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="page URL, or path to a saved AX-tree JSON with --offline")
    ap.add_argument("--offline", action="store_true",
                    help="treat source as a local JSON file (no Playwright needed)")
    ap.add_argument("--rank", action="store_true",
                    help="sort by heuristic importance instead of reading order")
    args = ap.parse_args(argv)

    if args.offline:
        with open(args.source) as f:
            tree = json.load(f)
        url = None
    else:
        from .extract import fetch_ax_tree  # lazy import so offline needs no playwright
        tree = fetch_ax_tree(args.source)
        url = args.source

    contract = build_contract(tree, url=url, sort_by_importance=args.rank)
    json.dump(contract, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
