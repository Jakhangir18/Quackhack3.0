"""Spell "Touchpoint" through the vibration motors using Braille mappings.

Run on the Raspberry Pi:
    python tests/demo_touchpoint.py
"""
import sys
import time

sys.path.insert(0, __file__.rsplit("/tests", 1)[0])
from output.motors import buzz_pattern, motors
from output.mappings import mapping

DWELL_S = 0.5  # how long each letter stays on
GAP_S   = 0.2  # silence between letters
WORD    = "touchpoint"


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
