from gpiozero import PWMOutputDevice
from time import sleep

LEVEL = 0.35   # vibration strength 0.0-1.0 (raise/lower as needed)

MOT1 = PWMOutputDevice(4, frequency=200)   # dot1 -> GPIO4
MOT2 = PWMOutputDevice(5, frequency=200)   # dot2 -> GPIO5

def buzz(motor, level=LEVEL, duration=2.0):
    motor.value = 1.0    # kick-start to overcome stall torque
    sleep(0.04)
    motor.value = level  # settle to running level
    sleep(duration)
    motor.off()

try:
    print(">>> GPIO4 (dot1) only. Watch which motor vibrates.")
    buzz(MOT1)
    sleep(1.5)

    print(">>> GPIO5 (dot2) only. Watch which motor vibrates.")
    buzz(MOT2)
    sleep(1.5)

    print(">>> Both together.")
    MOT1.value = 1.0; MOT2.value = 1.0
    sleep(0.04)
    MOT1.value = LEVEL; MOT2.value = LEVEL
    sleep(2.0)
    MOT1.off(); MOT2.off()

    print("Done.")

finally:
    MOT1.off(); MOT2.off()
    MOT1.close(); MOT2.close()
