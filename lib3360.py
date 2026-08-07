"""lib3360.py — Linux-only serial control library for EIE3360.

Sends 11-byte control frames over UART to an STM32 microcontroller.
Receives encoder values from the same port in format: [m1,m2]

Frame format (11 bytes, fixed):
    Header: 0x0D | Payload (9 bytes) | Footer: 0x20

Payload layout (big-endian):
    m1_pwm: uint16  — Motor 1 PWM magnitude (0–65535)
    m2_pwm: uint16  — Motor 2 PWM magnitude (0–65535)
    s1_pwm: uint16  — Servo 1 PWM value (0–65535)
    s2_pwm: uint16  — Servo 2 PWM value (0–65535)
    dir_byte: uint8  — Direction flags
        bit 0: motor1 direction (0 = backward, 1 = forward)
        bit 1: motor2 direction (0 = backward, 1 = forward)

Motor values are signed integers in range [-65535, +65535]:
    Positive (+) → forward, Negative (-) → backward.

Functions:
    motor(m1, m2) — Send motor control command. Pass None to keep previous value.
    servo(s1, s2) — Send servo control command. Pass None to keep previous value.
    get_encoder()  — Read encoder values from serial port, returns (m1, m2).

Both functions share the same serial port defined by DEFAULT_PORT at the top of this file.
"""

import re
import serial
import struct
from typing import Optional

# Shared serial port for all commands
DEFAULT_PORT = "/dev/ttyTHS1"
BAUDRATE = 115200
FRAME_HEADER = 0x0D
FRAME_FOOTER = 0x20

# Internal state (persists across calls)
_state = {
    "m1": 0,
    "m2": 0,
    "s1": 0,
    "s2": 0,
}


def _send_frame() -> None:
    """Build and send the current frame. Called once per motor()/servo()."""
    m1 = _state["m1"]
    m2 = _state["m2"]
    s1 = _state["s1"]
    s2 = _state["s2"]

    # Direction bits: positive/zero = forward (1), negative = backward (0)
    d1 = 1 if m1 >= 0 else 0
    d2 = 1 if m2 >= 0 else 0

    pwm1 = abs(m1) & 0xFFFF
    pwm2 = abs(m2) & 0xFFFF

    payload = struct.pack(">HHHHB", pwm1, pwm2, s1 & 0xFFFF, s2 & 0xFFFF, d1 | (d2 << 1))
    frame = bytes([FRAME_HEADER]) + payload + bytes([FRAME_FOOTER])

    ser = serial.Serial(DEFAULT_PORT, BAUDRATE, timeout=1)
    try:
        ser.write(frame)
    finally:
        ser.close()


def motor(m1: Optional[int] = None, m2: Optional[int] = None) -> None:
    """Send motor control command (PWM values -65535 to +65535).

    Positive value → forward, negative value → backward.
    Pass None for a channel to keep its previous value unchanged.

    Args:
        m1: Motor 1 PWM (-65535 .. +65535), or None.
        m2: Motor 2 PWM (-65535 .. +65535), or None.
    """
    if m1 is not None:
        _state["m1"] = max(-65535, min(65535, int(m1)))
    if m2 is not None:
        _state["m2"] = max(-65535, min(65535, int(m2)))

    _send_frame()


def servo(s1: Optional[int] = None, s2: Optional[int] = None) -> None:
    """Send servo control command (PWM values 0–65535).

    Pass None for a channel to keep its previous value unchanged.

    Args:
        s1: Servo 1 PWM value (e.g. 500–2500), or None.
        s2: Servo 2 PWM value, or None.
    """
    if s1 is not None:
        _state["s1"] = max(0, min(65535, int(s1)))
    if s2 is not None:
        _state["s2"] = max(0, min(65535, int(s2)))

    _send_frame()


def get_encoder(timeout: float = 1.0) -> tuple[int, int]:
    """Read encoder values from the serial port.

    Expects data in format: [m1,m2] where m1 and m2 are signed integers.
    Examples: [0,0], [-123,23], [1234567,-1234567]

    Args:
        timeout: Seconds to wait for a response (default 1.0).

    Returns:
        Tuple of (m1, m2) encoder values.
    """
    ser = serial.Serial(DEFAULT_PORT, BAUDRATE, timeout=timeout)
    try:
        data = ser.read(ser.in_waiting or 64).decode("utf-8", errors="ignore").strip()

        # Parse [m1,m2] pattern from received data
        match = re.search(r"\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]", data)
        if match:
            return int(match.group(1)), int(match.group(2))

        raise ValueError(f"No encoder data found. Received: {repr(data)}")
    finally:
        ser.close()


__all__ = ["motor", "servo", "get_encoder"]
