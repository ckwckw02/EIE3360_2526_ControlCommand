"""example.py — Demonstrates using lib3360 to send control commands.

Usage:
    python3 example.py

To change the serial port, edit DEFAULT_PORT in lib3360.py.
"""
from lib3360 import motor, servo, get_encoder


if __name__ == "__main__":
    print("=== lib3360 Example ===")

    # Update servo values (stored internally)
    servo(1000, 1400)

    # Send: m1 forward (+20000), m2 backward (-20000)
    motor(20000, -20000)

    print("Reading encoder...")
    m1, m2 = get_encoder()      # read [m1,m2] from serial port
    print(f"Encoder: [{m1},{m2}]")
