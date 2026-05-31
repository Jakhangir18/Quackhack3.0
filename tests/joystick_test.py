#!/usr/bin/python3
"""Joystick raw value monitor — run this to verify wiring before navigator.py.

Wiring (MCP3008 via SPI):
    CE0 = GPIO8 / physical pin 24
    SWT (button) -> channel 0
    VRX (X axis) -> channel 1
    VRY (Y axis) -> channel 2
"""
import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000  # required on Pi 5, otherwise junk values

SWT_CH = 0
VRX_CH = 1
VRY_CH = 2


def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) + adc[2]


try:
    while True:
        x = read_channel(VRX_CH)
        y = read_channel(VRY_CH)
        btn = read_channel(SWT_CH)
        print(f"X: {x:4d}  Y: {y:4d}  Button: {btn:4d}")
        time.sleep(0.5)
except KeyboardInterrupt:
    spi.close()
