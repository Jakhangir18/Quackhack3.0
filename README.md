# touchpoint / extractor

Pulls the accessibility tree from a live URL (or a saved JSON snapshot) and produces a clean, ranked list of interactive/structural elements — suitable for TTS or an LLM agent.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
# from the repo root (touchpoint/)
uv sync
uv run playwright install chromium
```

## Running

**Live — fetch a real page:**
```bash
uv run python -m extractor.cli https://andrewkelley.me/ --rank
```

**Offline — replay a saved AX-tree JSON:**
```bash
uv run python -m extractor.cli sample_tree.json --offline --rank
```

`--rank` sorts output by heuristic importance (role + landmark position) instead of DOM reading order.

## Output

JSON written to stdout:

```json
{
  "url": "https://andrewkelley.me/",
  "item_count": 12,
  "items": [
    { "id": 0, "role": "heading", "name": "Andrew Kelley", "landmark": "main", "level": 1, "importance": 0.9 },
    ...
  ]
}
```

## Project layout

```
touchpoint/
├── extractor/
│   ├── __init__.py
│   ├── cli.py        # entry point, argument parsing
│   ├── extract.py    # Playwright → raw AX tree
│   ├── filter.py     # prune + flatten + heuristic scoring
│   ├── rank.py       # LLM re-ranking seam (stub, heuristic fallback for now)
│   └── schema.py     # A11yItem dataclass
├── pyproject.toml
└── uv.lock
```

## Dependencies

- `playwright` — headless Chromium for live fetches
- `pyyaml` — parse Playwright's `aria_snapshot()` output
