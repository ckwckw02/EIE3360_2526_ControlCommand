# SendSerial (EIE3360) — Linux Serial Control Library

Python library for sending 11-byte control frames over UART to an STM32 microcontroller and reading encoder values from the same port.

## Frame Format (11 bytes, fixed)

| Header | Motor1 PWM | Motor2 PWM | Servo1 PWM | Servo2 PWM | Dir Byte | Footer |
|--------|------------|------------|------------|------------|----------|--------|
| 0x0D   | 2 bytes    | 2 bytes    | 2 bytes    | 2 bytes    | 1 byte   | 0x20   |

All values are **big-endian uint16**. Motor PWM range: **-65535 to +65535** (positive = forward, negative = backward). Servo PWM range: **0–65535**. Direction is encoded in the dir byte (bit 0 = motor1, bit 1 = motor2).

## Encoder Response Format

The STM32 sends encoder values back from the same port:
```
[m1,m2]
```
Examples: `[0,0]`, `[-123,23]`, `[1234567,-1234567]`

## Installation

```bash
pip install pyserial
```

## Quick Start

### example.py — Send one frame + read encoder

```bash
python3 example.py
```

### keyboard.py — Keyboard motor control (Linux only)

```bash
python3 keyboard.py
```

| Key  | Action           | Motor Values          |
|------|------------------|-----------------------|
| **w** | Forward         | `motor(30000, 30000)` |
| **s** | Backward        | `motor(-30000, -30000)` |
| **a** | Turn left       | `motor(-30000, 30000)` |
| **d** | Turn right      | `motor(30000, -30000)` |
| **q** | Stop            | `motor(0, 0)`         |
| **x** | Exit program    | —                     |

To change the serial port, edit `DEFAULT_PORT` in `lib3360.py`.

### Using the library in your own code

```python
from lib3360 import motor, servo, get_encoder

# Update servo + send one frame
servo(1000, 1400)
motor(-30000, 30000)   # m1 backward, m2 forward

# Read encoder values (returns tuple of int)
m1, m2 = get_encoder()
print(f"Encoder: [{m1},{m2}]")
```

## API Reference

### `motor(m1, m2)` → None

| Parameter | Description |
|-----------|-------------|
| `m1` | Motor 1 PWM: **-65535 to +65535**. Positive = forward, negative = backward. Pass `None` to keep previous value. |
| `m2` | Motor 2 PWM: same range as m1. Pass `None` to keep previous value. |

### `servo(s1, s2)` → None

| Parameter | Description |
|-----------|-------------|
| `s1` | Servo 1 PWM value: **0–65535** (e.g. 500–2500). Pass `None` to keep previous value. |
| `s2` | Servo 2 PWM value, same range as s1. |

### `get_encoder(timeout=1.0)` → tuple[int, int]

Read encoder values from the serial port. Expects data in format `[m1,m2]`.

| Parameter | Description |
|-----------|-------------|
| `timeout` | Seconds to wait for response (default 1.0). |

Returns `(m1, m2)` as signed integers. Raises `ValueError` if no valid encoder data received.

## Configuration

Both `motor()`, `servo()` and `get_encoder()` share the same serial port defined by `DEFAULT_PORT` in `lib3360.py`:

```python
# In lib3360.py, change this line:
DEFAULT_PORT = "/dev/ttyTHS1"   # e.g., "/dev/ttyUSB0"
```

## Files

| File | Purpose |
|------|---------|
| `lib3360.py` | Core library with `motor()`, `servo()` and `get_encoder()` functions |
| `example.py` | Demo script — send one frame + read encoder |
| `keyboard.py` | Keyboard motor control (Linux only) |
