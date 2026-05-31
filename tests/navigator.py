#!/usr/bin/env python3
"""Navigate an accessibility tree with a joystick and Braille vibration motors.

Controls:
    Left / Right  — previous / next item within the current section
    Up   / Down   — previous / next section (resets to first item)
    Button press  — re-buzz the current item

Usage:
    # 1. Generate the tree (needs GEMINI_API_KEY for sectioned output):
    python -m extractor.cli https://example.com > tree.json

    # 2. Navigate:
    python tests/navigator.py tree.json
"""
import json
import sys
import time

sys.path.insert(0, __file__.rsplit("/tests", 1)[0])

import spidev

from output.mappings import mapping
from output.motors import buzz_pattern, motors

# --- Joystick thresholds (ADC 0-1023, center ~512) ---
LOW = 200
HIGH = 800
DEBOUNCE_S = 0.45   # seconds to ignore input after a move

# --- SPI setup ---
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000  # required on Pi 5

SWT_CH = 0
VRX_CH = 1
VRY_CH = 2


def _read(ch):
    adc = spi.xfer2([1, (8 + ch) << 4, 0])
    return ((adc[1] & 3) << 8) + adc[2]


# --- Braille output ---
LETTER_DURATION = 0.3
LETTER_GAP      = 0.12


def buzz_text(text):
    for ch in text.lower():
        buzz_pattern(mapping.get(ch, [0] * 6), duration=LETTER_DURATION)
        time.sleep(LETTER_GAP)


# --- Tree normalisation ---
def _to_sections(tree):
    """Accept both llm_build_tree output (sections[]) and flat contract (items[])."""
    if "sections" in tree:
        return tree["sections"]
    # flat contract fallback: one section containing all items
    items = tree.get("items", [])
    return [{"heading": tree.get("url", "Page"), "items": [
        {"text": it.get("name", ""), "verbatim": it.get("name", ""), "role": it.get("role", "")}
        for it in items
    ]}]


# --- Navigation loop ---
def navigate(sections):
    if not sections:
        print("Tree is empty.")
        return

    sec_idx  = 0
    item_idx = 0

    def clamp_item():
        nonlocal item_idx
        n = len(sections[sec_idx].get("items", []))
        item_idx = max(0, min(item_idx, n - 1))

    def current():
        items = sections[sec_idx].get("items", [])
        return items[item_idx] if items else None

    def buzz_current():
        item = current()
        if not item:
            return
        label = item.get("text") or item.get("name") or ""
        print(f"  [{sections[sec_idx]['heading']}] {label}")
        buzz_text(label)

    buzz_current()

    while True:
        x   = _read(VRX_CH)
        y   = _read(VRY_CH)
        btn = _read(SWT_CH)

        moved = False

        if x < LOW:                                  # left — prev item
            item_idx = max(0, item_idx - 1)
            moved = True
        elif x > HIGH:                               # right — next item
            n = len(sections[sec_idx].get("items", []))
            item_idx = min(n - 1, item_idx + 1)
            moved = True
        elif y < LOW:                                # up — prev section
            sec_idx  = max(0, sec_idx - 1)
            item_idx = 0
            moved = True
        elif y > HIGH:                               # down — next section
            sec_idx  = min(len(sections) - 1, sec_idx + 1)
            item_idx = 0
            moved = True
        elif btn < LOW:                              # button — re-buzz
            buzz_current()
            time.sleep(DEBOUNCE_S)

        if moved:
            clamp_item()
            buzz_current()
            time.sleep(DEBOUNCE_S)
        else:
            time.sleep(0.05)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tests/navigator.py tree.json")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        tree = json.load(f)

    sections = _to_sections(tree)
    print(f"Loaded {len(sections)} section(s). Move joystick to navigate.")

    try:
        navigate(sections)
    except KeyboardInterrupt:
        print("\nDone.")
    finally:
        spi.close()
        for m in motors.values():
            m.off()
            m.close()


if __name__ == "__main__":
    main()
