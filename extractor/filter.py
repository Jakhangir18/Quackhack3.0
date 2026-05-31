"""Prune + flatten a raw accessibility tree into an ordered, tagged item list.

This is the 'no-AI heuristic pass'. Input is the dict returned by Playwright's
page.accessibility.snapshot(). Output is the contract (schema.A11yItem list).

Why a heuristic pass at all, when an LLM is coming later:
  1. It's your graceful-degradation fallback. If the LLM API call fails mid-demo,
     this still produces a usable ordering with zero network calls.
  2. It shrinks the LLM input. You hand the model ~30 tagged items, not a 4000-node
     raw tree, which is cheaper, faster, and more reliable.
"""

from .schema import A11yItem

# Roles we keep as navigable items. Everything else is dropped.
KEEP_ROLES = {
    "heading",
    "link",
    "button",
    "textbox",
    "searchbox",
    "checkbox",
    "radio",
    "combobox",
    "menuitem",
    "tab",
}

# ARIA landmark roles -> human label. Used for grouping AND scoring.
# This is what solves "where's the real content vs. chrome" before AI touches it.
LANDMARK_ROLES = {
    "banner": "banner",  # site header
    "navigation": "navigation",
    "main": "main",  # the actual content
    "contentinfo": "footer",
    "complementary": "sidebar",
    "search": "search",
    "region": "region",
    "form": "form",
}

# Per-role base importance (0..1).
ROLE_BASE = {
    "heading": 0.70,
    "button": 0.60,
    "textbox": 0.60,
    "searchbox": 0.60,
    "combobox": 0.55,
    "link": 0.50,
    "checkbox": 0.45,
    "radio": 0.45,
    "menuitem": 0.40,
    "tab": 0.40,
}

# Landmark nudges importance up (content) or down (chrome).
LANDMARK_WEIGHT = {
    "main": 0.15,
    "search": 0.05,
    "region": 0.0,
    "form": 0.0,
    "sidebar": -0.05,
    "navigation": -0.10,
    "banner": -0.10,
    "footer": -0.20,
}


def _score(role, level, landmark):
    s = ROLE_BASE.get(role, 0.30)
    if role == "heading" and level:
        s += max(0.0, 0.25 - 0.05 * (level - 1))  # h1 highest, deeper less
    s += LANDMARK_WEIGHT.get(landmark, 0.0)
    return round(max(0.0, min(1.0, s)), 3)


def flatten(tree, landmark=None, context=None, _items=None, _counter=None):
    """Depth-first walk. Keeps KEEP_ROLES nodes with a non-empty name,
    tagging each with the nearest enclosing landmark."""
    if _items is None:
        _items, _counter = [], [0]
    if not tree:
        return _items

    role = tree.get("role", "")
    name = (tree.get("name") or "").strip()

    # If this node is itself a landmark, it becomes the context for its children.
    current_landmark = LANDMARK_ROLES.get(role, landmark)
    current_context = _node_text(tree) if role in {"listitem", "paragraph"} else context

    if role in KEEP_ROLES and name:
        level = tree.get("level")
        item = A11yItem(
            id=_counter[0],
            role=role,
            name=name,
            landmark=current_landmark,
            level=level,
            importance=_score(role, level, current_landmark),
        )
        item.context = current_context
        _items.append(item)
        _counter[0] += 1

    for child in tree.get("children") or []:
        flatten(child, current_landmark, current_context, _items, _counter)

    return _items


def _node_text(tree):
    name = (tree.get("name") or "").strip()
    pieces = [name] if name else []
    for child in tree.get("children") or []:
        child_text = _node_text(child)
        if child_text:
            pieces.append(child_text)

    text = " ".join(pieces)
    return (
        text.replace(" .", ".")
        .replace(" ,", ",")
        .replace(" !", "!")
        .replace(" ?", "?")
        .replace(" :", ":")
        .replace(" ;", ";")
    )


def _heading_context(tree, output):
    children = tree.get("children") or []
    for index, child in enumerate(children):
        if child.get("role") != "heading":
            continue

        name = (child.get("name") or "").strip()
        if not name:
            continue

        for sibling in children[index + 1 :]:
            if sibling.get("role") == "heading":
                break
            if sibling.get("role") == "paragraph":
                text = _node_text(sibling)
                if text:
                    output.setdefault(name, text)
                    break

    for child in children:
        _heading_context(child, output)


def add_context(items, tree):
    heading_context = {}
    _heading_context(tree, heading_context)

    for item in items:
        item["verbatim"] = item["name"]
        context = item.pop("context", None) or heading_context.get(item["name"])
        if context and context != item["name"]:
            item["context"] = context
    return items


def build_contract(tree, url=None, sort_by_importance=False):
    """Top-level entry. Returns the JSON-serialisable contract dict."""
    items = flatten(tree)
    if sort_by_importance:
        items = sorted(items, key=lambda i: i.importance, reverse=True)
    item_dicts = add_context(
        [i.to_dict() | {"context": getattr(i, "context", None)} for i in items], tree
    )
    return {
        "url": url,
        "item_count": len(items),
        "items": item_dicts,
    }
