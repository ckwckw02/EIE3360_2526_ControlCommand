"""keyboard.py — Keyboard motor control for EIE3360.

Usage:
    python3 keyboard.py

Controls:
    w — forward        (m1=+30000, m2=+30000)
    s — backward       (m1=-30000, m2=-30000)
    a — turn left      (m1=-30000, m2=+30000)
    d — turn right     (m1=+30000, m2=-30000)
    q — stop           (m1=0,     m2=0)
    x — exit program

To change the serial port, edit DEFAULT_PORT in lib3360.py.
"""
import sys
import tty
import termios
from lib3360 import motor


def _getch() -> str:
    """Read a single character without pressing Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        return ch.lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    print("=== Keyboard Motor Control ===")
    print('w: forward  |  s: backward  |  a: left  |  d: right')
    print('q: stop     |  x: exit\n')

    try:
        while True:
            key = _getch()

            if key == "x":
                print("Exiting.")
                break
            elif key == "w":
                motor(30000, 30000)
            elif key == "s":
                motor(-30000, -30000)
            elif key == "a":
                motor(-30000, 30000)
            elif key == "d":
                motor(30000, -30000)
            elif key == "q":
                motor(0, 0)

    except KeyboardInterrupt:
        print("\nInterrupted. Stopping motors...")
        motor(0, 0)
