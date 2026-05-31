"""GPIO button pin configuration.

gpiozero uses BCM GPIO numbering, not physical pin numbers.
"""

BTN_LEFT = 17  # previous item
BTN_RIGHT = 27  # next item
BTN_UP = 22  # next section (wraps around)
BTN_CENTER = 23  # verbatim / where am I

BOUNCE_TIME = 0.05
CENTER_HOLD_TIME = 1
