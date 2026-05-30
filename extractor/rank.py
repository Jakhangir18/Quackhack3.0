"""LLM re-ranking seam.

The pipeline must never know whether ranking was heuristic or LLM-driven, so
keep this function pure and swappable. Today it just sorts by the heuristic
score; drop the API call in where the TODO is.
"""


def llm_rank(items, goal=None):
    """items: list of dicts (from build_contract['items']).
    goal: optional user intent, e.g. 'buy a USB-C cable'.

    Returns items reordered by relevance. Falls back to heuristic importance
    so the pipeline always works even with no network.
    """
    # TODO: send `items` (as JSON) + `goal` to the LLM and ask it to return the
    # ids in priority order, plus an optional 'drop' list of ids that are noise.
    # Then reorder `items` to match. Example prompt skeleton:
    #
    #   "Here are interactive/structural elements from a web page as JSON.
    #    The user wants to: {goal}. Return ONLY a JSON object
    #    {{'order': [ids...], 'drop': [ids...]}} ranking by usefulness."
    #
    # Parse, reorder, return. On any error, fall through to the line below.
    return sorted(items, key=lambda i: i["importance"], reverse=True)
