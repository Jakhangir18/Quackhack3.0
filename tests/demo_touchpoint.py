"""Spell "Touchpoint" through the vibration motors using Braille mappings.

Run on the Raspberry Pi:
    python tests/demo_touchpoint.py

Requires gpiozero and the 6 motor GPIO pins to be wired up.
"""
import sys
import time

sys.path.insert(0, __file__.rsplit("/tests", 1)[0])
from output.mappings import mapping

# One PWMOutputDevice per Braille dot. Fill in the correct GPIO pin numbers.
# Dot layout:
#   dot1  dot4
#   dot2  dot5
#   dot3  dot6
GPIO_PINS = [
    4,    # dot1
    5,    # dot2
    None, # dot3 — fill in
    None, # dot4 — fill in
    None, # dot5 — fill in
    None, # dot6 — fill in
]

LEVEL      = 0.35  # vibration strength
KICK_S     = 0.04  # kick-start duration
DWELL_S    = 0.5   # how long each letter stays on
GAP_S      = 0.2   # silence between letters

WORD = "touchpoint"


def main():
    from gpiozero import PWMOutputDevice

    motors = [
        PWMOutputDevice(pin, frequency=200) if pin is not None else None
        for pin in GPIO_PINS
    ]

    def fire(dots):
        for motor, active in zip(motors, dots):
            if motor and active:
                motor.value = 1.0
        time.sleep(KICK_S)
        for motor, active in zip(motors, dots):
            if motor and active:
                motor.value = LEVEL

    def off_all():
        for motor in motors:
            if motor:
                motor.off()

    try:
        for ch in WORD:
            dots = mapping.get(ch, [0] * 6)
            fire(dots)
            time.sleep(DWELL_S)
            off_all()
            time.sleep(GAP_S)
        print("Done.")
    finally:
        off_all()
        for motor in motors:
            if motor:
                motor.close()


if __name__ == "__main__":
    main()
