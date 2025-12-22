"""example.py

Demonstrates using `lib3360.send_control`.

This example shows how to:
- get the raw hex frame without sending
- send one frame
- (optionally) start the continuous send loop

Run in the same directory as `transmitter.py` and `lib3360.py`.
"""
import time

try:
    # Preferred import
    from lib3360 import send_control
except Exception:
    # Fallback: load by filename using importlib (works even if you named it 3360lib.py)
    import importlib.util
    import pathlib
    import os

    lib_path = pathlib.Path(__file__).resolve().parent / 'lib3360.py'
    spec = importlib.util.spec_from_file_location('lib3360', str(lib_path))
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    send_control = lib.send_control

# Optionally allow overriding serial port via environment variable or CLI
PORT = None
import os
if os.getenv('SENDSERIAL_PORT'):
    PORT = os.getenv('SENDSERIAL_PORT')
elif len(sys.argv) > 1:
    PORT = sys.argv[1]


def demo_hex():
    hexstr = send_control(1000, 1500, 1000, 1400, 0, 1, mode='hex')
    print('Hex frame (no header/footer shown in payload):', hexstr)


def demo_once():
    print('Sending one frame...')
    send_control(1000, 1500, 1000, 1400, 0, 1, mode='once', port=PORT)


def demo_loop():
    print('Starting send loop (press Ctrl-C to stop)')
    send_control(1000, 1500, 1000, 1400, 0, 1, mode='loop', interval=1.0, port=PORT)


if __name__ == '__main__':
    time.sleep(0.2)
    # demo_hex()
    # Uncomment to actually send once (requires transmitter port available):
    demo_once()
    # Uncomment to start continuous send loop:
    # demo_loop()
