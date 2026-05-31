"""LLM re-ranking seam.

Gemini can reorder the small, de-noised item list by usefulness for a user
goal. If anything goes wrong, we fall back to the local heuristic score.
"""

import json
import os
import re
import sys


def _fallback(items):
    return sorted(items, key=lambda i: i["importance"], reverse=True)


def _extract_json(text):
    match = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not match:
        raise ValueError("Gemini did not return JSON")
    return json.loads(match.group(0))


def llm_rank(items, goal=None):
    """items: list of dicts (from build_contract['items']).
    goal: optional user intent, e.g. 'buy a USB-C cable'.

    Returns items reordered by relevance. Falls back to heuristic importance
    so the pipeline always works even with no network.
    """
    if not items:
        return []

    if not (os.getenv("GEMINI_API_KEY")):
        return _fallback(items)

    try:
        from google import genai

        prompt = f"""Here are interactive/structural elements from a web page as JSON.
        The user wants to: {goal or "navigate the page efficiently"}.

        Return ONLY a JSON object {{"order": [ids...], "drop": [ids...]}} ranking by usefulness.
        Only use ids present in the items. Put obvious page noise in drop.
        Do not drop items containing numbers, names, prices, dates, negations, legal, medical, or safety information.

        Items:
        {json.dumps(items, ensure_ascii=False)}
        """
        with genai.Client() as client:
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt,
            )
        ranking = _extract_json(response.text)

        by_id = {item["id"]: item for item in items}
        dropped = set(ranking.get("drop", []))
        ordered = []
        seen = set()
        for item_id in ranking.get("order", []):
            if item_id in by_id and item_id not in dropped and item_id not in seen:
                ordered.append(by_id[item_id])
                seen.add(item_id)

        ordered.extend(
            item
            for item in _fallback(items)
            if item["id"] not in seen and item["id"] not in dropped
        )
        return ordered
    except Exception:
        return _fallback(items)


def _load_tree_json(text):
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text or "", re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _validate_tree(tree):
    if "domain" not in tree:
        raise ValueError("LLM tree missing domain")
    if "sections" not in tree:
        raise ValueError("LLM tree missing sections")

    for section in tree["sections"]:
        if "heading" not in section or "items" not in section:
            raise ValueError("LLM tree section missing heading or items")
        for item in section["items"]:
            if "text" not in item or "verbatim" not in item:
                raise ValueError("LLM tree item missing text or verbatim")


def llm_build_tree(items, domain=None):
    """Use Gemini to turn flat accessibility items into a navigation tree.

    Returns a tree dict on success, or None on failure.
    """
    try:
        from google import genai
        from google.genai import types

        prompt = f"""You are a navigation assistant for a tactile Braille device for deafblind users.
Users navigate with a joystick: left/right moves between items within a section, up/down jumps between sections.
Braille is slow — short labels matter enormously.

Transform the raw accessibility items below into a clean navigation tree.

OUTPUT: Return ONLY a valid JSON object with this exact shape:
{{
  "domain": "<domain string>",
  "title": "<page title>",
  "orientation": "<single most important descriptive line about this page>",
  "sections": [
    {{
      "heading": "<section name>",
      "items": [
        {{
          "text": "<short Braille label, max 8 words, include dates/numbers if present>",
          "verbatim": "<exact original text, never paraphrased>",
          "role": "<role from original item>"
        }}
      ]
    }}
  ]
}}

RULES:
1. Group items into logical sections based on the page content structure. Use whatever headings exist — h1, h2, h3, h4, or none. If no clear headings exist, infer sections from content clusters. Every item belongs to exactly one section.
2. "text" is the short Braille label — max 8 words. Must include dates if present. Must be meaningful without surrounding context.
3. "verbatim" should combine the exact original item text with useful exact surrounding context from the input item's "context" field when present. For dates, output "Title — date". For descriptions, output "Title — description". Never paraphrase. Never drop or alter numbers, dates, prices, names, negations, or legal/medical/safety language.
4. Orphaned links like "source", "play in your browser", "game development journal" must be prefixed with their parent item's name. Example: text "Face the Music — source", verbatim "Face the Music — source".
5. Drop pure noise: cookie banners, share buttons, navigation chrome. Do NOT drop anything containing a date, number, price, or proper noun.
6. Preserve reading order within each section.
7. "orientation" is the single most useful sentence for a blind user to understand what this page is about.
8. If a heading item has descriptive context, use the heading name as "text" and output "Heading — context" as "verbatim".
9. Examples:
   - name "Zig's New Async I/O (Text Version)", context "2025 Oct 29 - Zig's New Async I/O (Text Version)" => text "Async IO text — Oct 2025", verbatim "Zig's New Async I/O (Text Version) — 2025 Oct 29"
   - name "Zig", context "Zig - a general-purpose programming language and toolchain for maintaining robust, optimal and reusable software." => text "Zig language and toolchain", verbatim "Zig - a general-purpose programming language and toolchain for maintaining robust, optimal and reusable software."
   - name "Face the Music", context "Rock your way out of being trampled by a mob of screaming fans. You can play in your browser or check out the source." => text "Face the Music", verbatim "Face the Music — Rock your way out of being trampled by a mob of screaming fans."

INPUT ITEMS:
{json.dumps(items, ensure_ascii=False)}
"""
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                system_instruction="You are a JSON-only responder. Output a single JSON object and nothing else. No markdown fences, no explanation, no preamble.",
            ),
        )
        tree = _load_tree_json(response.text)
        _validate_tree(tree)
        if domain is not None:
            tree["domain"] = domain
        return tree
    except Exception as exc:
        print(f"[rank] llm_build_tree failed: {exc}", file=sys.stderr)
        return None
