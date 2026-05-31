"""Build a navigation tree and run Braille joystick navigation."""

import argparse
import json
import os
import sys
from pathlib import Path
from time import sleep
from urllib.parse import urlparse

from output.navigate import NavigationStateMachine, TextPlayer, bind_buttons, dummy_tree

DEFAULT_TREE_PATH = Path(__file__).resolve().parents[1] / "output" / "sample_navigation_tree.json"


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


def _domain(source):
    parsed = urlparse(source or "")
    return parsed.netloc or source


def _build_tree_from_url(url):
    from .extract import fetch_ax_tree
    from .filter import build_contract
    from .rank import llm_build_tree

    ax_tree = fetch_ax_tree(url)
    contract = build_contract(ax_tree, url=url)
    return llm_build_tree(contract["items"], domain=_domain(url))


def _load_tree(source=None, offline=False):
    if source is None:
        source = DEFAULT_TREE_PATH
        offline = True

    if offline:
        with open(source) as f:
            return json.load(f)

    tree = _build_tree_from_url(source)
    if tree is None:
        print("[main] LLM tree failed, using fallback tree", file=sys.stderr)
        return dummy_tree(domain=_domain(source))
    return tree


def main(argv=None):
    _load_dotenv()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        nargs="?",
        help="page URL, or saved navigation-tree JSON with --offline",
    )
    parser.add_argument("--offline", action="store_true", help="load source as tree JSON")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="print the first item and exit without GPIO buttons",
    )
    args = parser.parse_args(argv)

    tree = _load_tree(args.source, offline=args.offline)
    player = TextPlayer()
    nav = NavigationStateMachine(tree, player.play)

    nav.play_current_item()
    if args.simulate:
        return

    buttons = bind_buttons(nav)
    print("Navigation ready. Press Ctrl+C to exit.")
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for button in buttons:
            button.close()


if __name__ == "__main__":
    main()
