"""lib3360.py

Small convenience library wrapping the existing `transmitter.py` API so callers
can send a control frame with one function call.

Functions:
- send_control(m1,m2,s1,s2,dir1,dir2, mode='once', interval=1.0, port=None)
    mode: 'once' | 'loop' | 'hex' ('hex' returns hex string without sending)

This file expects `transmitter.py` to be in the same directory.
"""
from typing import Optional

try:
    # local import from same folder
    from transmitter import send_control_command, send_control_loop, build_packet
except Exception as e:
    raise ImportError('lib3360 requires transmitter.py in the same directory') from e


def send_control(m1: int, m2: int, s1: int, s2: int,
                 dir1: int, dir2: int,
                 mode: str = 'once',
                 interval: float = 1.0,
                 port: Optional[str] = None):
    """High-level single-call API.

    - dir1, dir2: 0 = backward, 1 = forward
    - mode: 'once' (default) sends a single frame and returns None
            'loop' opens the port and sends repeatedly until Ctrl-C
            'hex' returns the hex string for the frame without sending
    - interval: seconds between sends when mode=='loop'
    - port: optional serial port override
    """
    if mode not in ('once', 'loop', 'hex'):
        raise ValueError("mode must be 'once', 'loop' or 'hex'")

    if mode == 'hex':
        frame = build_packet(int(m1), int(m2), int(s1), int(s2), int(dir1), int(dir2))
        return frame.hex()

    if mode == 'once':
        # call transmitter's function which opens/closes port for us
        return send_control_command(int(m1), int(m2), int(s1), int(s2), int(dir1), int(dir2), port=port)

    # mode == 'loop'
    return send_control_loop(int(m1), int(m2), int(s1), int(s2), int(dir1), int(dir2), interval=interval, port=port)


__all__ = ['send_control']
