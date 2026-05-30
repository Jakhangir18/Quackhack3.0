"""LLM re-ranking seam.

Gemini can reorder the small, de-noised item list by usefulness for a user
goal. If anything goes wrong, we fall back to the local heuristic score.
"""

import json
import os
import re


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
