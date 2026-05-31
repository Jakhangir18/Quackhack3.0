#!/usr/bin/env python3
"""Print button press/release events for configured navigation GPIO pins."""

import sys
import time

sys.path.insert(0, __file__.rsplit("/tests", 1)[0])

from gpiozero import Button

from output.button_config import (
    BOUNCE_TIME,
    BTN_CENTER,
    BTN_LEFT,
    BTN_RIGHT,
    BTN_UP,
)


BUTTONS = {
    "left": BTN_LEFT,
    "right": BTN_RIGHT,
    "up": BTN_UP,
    "center": BTN_CENTER,
}


def main():
    buttons = []
    for name, pin in BUTTONS.items():
        button = Button(pin, bounce_time=BOUNCE_TIME)
        button.when_pressed = lambda name=name, pin=pin: print(f"{name} pressed GPIO {pin}", flush=True)
        button.when_released = lambda name=name, pin=pin: print(f"{name} released GPIO {pin}", flush=True)
        buttons.append(button)

    print("Listening for button presses. Press Ctrl+C to exit.")
    print(f"Configured pins: {BUTTONS}")
    for name, button in zip(BUTTONS, buttons):
        print(f"{name} initial pressed={button.is_pressed}", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for button in buttons:
            button.close()


if __name__ == "__main__":
    main()
