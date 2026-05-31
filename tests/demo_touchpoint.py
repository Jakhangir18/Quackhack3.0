"""Spell "Touchpoint" through the vibration motors using Braille mappings.

Run on the Raspberry Pi:
    python tests/demo_touchpoint.py
"""

import os
import sys
import time

sys.path.insert(0, __file__.rsplit("/tests", 1)[0])

if os.environ.get("GPIOZERO_PIN_FACTORY") == "mock":
    from gpiozero import Device
    from gpiozero.pins.mock import MockFactory, MockPWMPin

    Device.pin_factory = MockFactory(pin_class=MockPWMPin)

from output.mappings import mapping
from output.motors import buzz_pattern, motors

DWELL_S = 0.5  # how long each letter stays on
GAP_S = 0.2  # silence between letters
WORD = "touchpoint"


def main():
    try:
        for ch in WORD:
            buzz_pattern(mapping.get(ch, [0] * 6), duration=DWELL_S)
            time.sleep(GAP_S)
        print("Done.")
    finally:
        for motor in motors.values():
            motor.off()
            motor.close()


if __name__ == "__main__":
    main()
