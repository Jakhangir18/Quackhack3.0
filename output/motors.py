from time import sleep

from gpiozero import PWMOutputDevice

LEVEL = 0.35  # vibration strength 0.0-1.0 (raise/lower as needed)
FREQ = 200

# gpiozero uses BCM GPIO numbering, NOT physical pin numbering.
# Assumed 6-dot braille layout for now:
#
#   left column       right column
#   dot 1            dot 4
#   dot 2            dot 5
#   dot 3            dot 6
#
# Bottom left/right dots for 8-dot braille are commented out for now.
DOT_GPIO = {
    1: 4,  # dot1 / left top     -> GPIO4  / physical pin 7
    2: 5,  # dot2 / left middle  -> GPIO5  / physical pin 29
    3: 6,  # dot3 / left bottom  -> GPIO6  / physical pin 31
    4: 26,  # dot4 / right top    -> GPIO26 / physical pin 37
    5: 12,  # dot5 / right middle -> GPIO12 / physical pin 32
    6: 16,  # dot6 / right bottom -> GPIO16 / physical pin 36
    # 7: 20, # dot7 / bottom left  -> GPIO20 / physical pin 38  (8-dot braille later)
    # 8: 21, # dot8 / bottom right -> GPIO21 / physical pin 40  (8-dot braille later)
}

motors = {dot: PWMOutputDevice(gpio, frequency=FREQ) for dot, gpio in DOT_GPIO.items()}


def buzz(motor, level=LEVEL, duration=2.0):
    motor.value = 1.0  # kick-start to overcome stall torque
    sleep(0.04)
    motor.value = level  # settle to running level
    sleep(duration)
    motor.off()


def buzz_dot(dot, level=LEVEL, duration=2.0):
    """Buzz one braille dot by dot number: 1-6 for now."""
    buzz(motors[dot], level=level, duration=duration)


def buzz_pattern(pattern, level=LEVEL, duration=2.0):
    """
    Buzz a 6-dot braille pattern like [1, 0, 0, 1, 0, 0].
    Index 0 -> dot1, index 1 -> dot2, ..., index 5 -> dot6.
    """
    active_dots = [dot for dot, is_on in enumerate(pattern, start=1) if is_on]

    for dot in active_dots:
        motors[dot].value = 1.0
    sleep(0.04)

    for dot in active_dots:
        motors[dot].value = level
    sleep(duration)

    for dot in active_dots:
        motors[dot].off()


try:
    # Test each dot one at a time so you can verify the physical layout.
    for dot, gpio in DOT_GPIO.items():
        print(f">>> dot{dot} / GPIO{gpio}. Watch which motor vibrates.")
        buzz_dot(dot)
        sleep(1.0)

    print(">>> All 6 active dots together.")
    buzz_pattern([1, 1, 1, 1, 1, 1])

    print("Done.")

finally:
    for motor in motors.values():
        motor.off()
        motor.close()
