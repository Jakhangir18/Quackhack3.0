"""GPIO button pin configuration.

gpiozero uses BCM GPIO numbering, not physical pin numbers.
"""

BTN_LEFT = 27  # previous item
BTN_RIGHT = 23  # next item
BTN_UP = 17  # next section (wraps around)
BTN_CENTER = 25  # verbatim / where am I

BOUNCE_TIME = 0.05
CENTER_HOLD_TIME = 1
