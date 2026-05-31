"""Navigation controls for a Braille navigation tree."""

import threading
from time import sleep

from output.button_config import (
    BOUNCE_TIME,
    BTN_CENTER,
    BTN_LEFT,
    BTN_RIGHT,
    BTN_UP,
    CENTER_HOLD_TIME,
)

LETTER_DUR = 0.12


def dummy_tree(domain=None):
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


class TextPlayer:
    def __init__(self):
        from output.mappings import mapping

        self.mapping = mapping
        try:
            from output.motors import buzz_pattern

            self.buzz_pattern = buzz_pattern
        except Exception:
            self.buzz_pattern = None

    def play(self, text):
        text = str(text or "")
        if not text:
            return

        print(text)
        for char in text.lower():
            pattern = self.mapping.get(char, [0, 0, 0, 0, 0, 0])
            print(f"{pattern} -> {char}")
            if self.buzz_pattern:
                self.buzz_pattern(pattern, duration=LETTER_DUR)
            else:
                sleep(0.01)


class NavigationStateMachine:
    def __init__(self, tree, play_text):
        self.tree = tree or dummy_tree()
        self.play_text = play_text
        self.section_idx = 0
        self.item_idx = 0
        self._center_hold_fired = False
        self._lock = threading.Lock()

    @property
    def sections(self):
        sections = self.tree.get("sections") or []
        return sections or dummy_tree(self.tree.get("domain")).get("sections", [])

    @property
    def current_section(self):
        return self.sections[self.section_idx]

    @property
    def current_items(self):
        return self.current_section.get("items") or []

    @property
    def current_item(self):
        items = self.current_items
        if not items:
            return {"text": "No items", "verbatim": "No items", "role": "status"}
        return items[self.item_idx]

    def play_current_item(self):
        self.play_text(self.current_item.get("text", ""))

    def previous_item(self):
        print("BTN_LEFT pressed")
        if self.item_idx > 0:
            self.item_idx -= 1
            self.play_current_item()

    def next_item(self):
        print("BTN_RIGHT pressed")
        if self.item_idx < len(self.current_items) - 1:
            self.item_idx += 1
            self.play_current_item()

    def next_section(self):
        print("BTN_UP pressed")
        self.section_idx = (self.section_idx + 1) % len(self.sections)
        self.item_idx = 0
        self.play_text(self.current_section.get("heading", ""))
        self.play_current_item()

    def play_verbatim(self):
        print("BTN_CENTER tapped")
        self.play_text(self.current_item.get("verbatim", ""))

    def play_orientation_burst(self):
        print("BTN_CENTER held")
        items = self.current_items
        parts = [
            self.tree.get("domain", ""),
            self.tree.get("title", ""),
            self.current_section.get("heading", ""),
            f"item {self.item_idx + 1} of {len(items)}",
        ]
        self.play_text(" ".join(part for part in parts if part))

    def center_pressed(self):
        print("BTN_CENTER pressed")
        with self._lock:
            self._center_hold_fired = False

    def center_held(self):
        with self._lock:
            self._center_hold_fired = True
        self.play_orientation_burst()

    def center_released(self):
        with self._lock:
            was_hold = self._center_hold_fired
        if not was_hold:
            self.play_verbatim()


def _require_button_pin(name, value):
    if value is None:
        raise ValueError(f"{name} must be set to a GPIO pin before running on hardware")


def bind_buttons(nav):
    from gpiozero import Button

    _require_button_pin("BTN_LEFT", BTN_LEFT)
    _require_button_pin("BTN_RIGHT", BTN_RIGHT)
    _require_button_pin("BTN_UP", BTN_UP)
    _require_button_pin("BTN_CENTER", BTN_CENTER)

    left = Button(BTN_LEFT, bounce_time=BOUNCE_TIME)
    right = Button(BTN_RIGHT, bounce_time=BOUNCE_TIME)
    up = Button(BTN_UP, bounce_time=BOUNCE_TIME)
    center = Button(
        BTN_CENTER,
        bounce_time=BOUNCE_TIME,
        hold_time=CENTER_HOLD_TIME,
    )

    left.when_pressed = nav.previous_item
    right.when_pressed = nav.next_item
    up.when_pressed = nav.next_section
    center.when_pressed = nav.center_pressed
    center.when_held = nav.center_held
    center.when_released = nav.center_released

    return [left, right, up, center]
