"""
transmitter.py

Sends a fixed-length serial packet to the STM32.

Packet format (default, to match example):
- 4 x uint16 (big-endian) : motor1, motor2, servo1, servo2 (each 2 bytes)
- 1 x uint8 : direction flags (bit0 = motor1 dir, bit1 = motor2 dir)

Total payload length: 9 bytes. Optional header/footer bytes are provided
as constants at the top; they default to empty to match the expected
string like "03e805dc07d009c402".

Usage:
 - Configure ports at the top of this file.
 - Run on Windows or Linux; other OS will error out.

Requires: pyserial
"""
import platform
import struct
import sys
import time

try:
	import serial
except ModuleNotFoundError:
	raise SystemExit("pyserial is required. Install with: pip install pyserial")

# ----------------------- Port / Serial Config (top of file) -----------------------
# Windows and Linux port names. Change as needed.
# Windows and Linux port names. Change as needed.
TX_PORT_WIN = 'COM15'
TX_PORT_LIN = '/dev/ttyUSB0'
BAUDRATE = 115200
TIMEOUT = 1  # seconds

# Frame header/footer (updated per request): 0x0D (CR) header, 0x20 (space) footer
# These are included in the transmitted frame and the receiver must use the same.
FRAME_HEADER = b"\x0D"
FRAME_FOOTER = b"\x20"
# -------------------------------------------------------------------------------


def detect_port():
	os_name = platform.system().lower()
	if os_name.startswith('win'):
		return TX_PORT_WIN
	if os_name.startswith('linux'):
		return TX_PORT_LIN
	raise SystemExit(f"Unsupported OS: {platform.system()}. Only Windows and Linux supported.")


def build_packet(m1, m2, s1, s2, dir_m1_flag=0, dir_m2_flag=0):
	"""Builds the packet bytes.

	- m1,m2,s1,s2: integers 0..65535
	- dir_m1_flag, dir_m2_flag: integers 0 or 1 where 0=backward, 1=forward

	Returns full frame (header + payload + footer) as bytes.
	"""
	if not all(isinstance(v, int) and 0 <= v <= 0xFFFF for v in (m1, m2, s1, s2)):
		raise ValueError('PWM values must be integers 0..65535')

	# Ensure direction flags are either 0 or 1
	d1 = 1 if int(dir_m1_flag) & 0x1 else 0
	d2 = 1 if int(dir_m2_flag) & 0x1 else 0

	# bit0 = motor1 direction flag, bit1 = motor2 direction flag
	dir_byte = (d1) | (d2 << 1)
	payload = struct.pack('>HHHHB', int(m1), int(m2), int(s1), int(s2), dir_byte)
	return FRAME_HEADER + payload + FRAME_FOOTER


def bytes_to_hex(b: bytes) -> str:
	return b.hex()


def send_control_command(m1, m2, s1, s2, dir1, dir2, port=None):
	"""Send one control command line.

	- dir1, dir2: 0 = backward, 1 = forward (integers)
	- port: optional override port string; if None, detect by OS.
	"""
	if port is None:
		port = detect_port()

	frame = build_packet(m1, m2, s1, s2, dir1, dir2)
	print(f"Opening serial port: {port} @ {BAUDRATE}")
	with serial.Serial(port, BAUDRATE, timeout=TIMEOUT) as ser:
		# small pause for some USB-serial adapters
		time.sleep(0.05)
		sent = ser.write(frame)
		ser.flush()
	print(f"Sent {sent} bytes -> {bytes_to_hex(frame)}")


def send_control_loop(m1, m2, s1, s2, dir1, dir2, interval=1.0, port=None):
	"""Open the serial port once and continuously send the same control frame.

	- interval: seconds between sends
	- stops on KeyboardInterrupt
	"""
	if port is None:
		port = detect_port()

	frame = build_packet(m1, m2, s1, s2, dir1, dir2)
	print(f"Opening serial port: {port} @ {BAUDRATE} — sending every {interval}s. Ctrl-C to stop")
	with serial.Serial(port, BAUDRATE, timeout=TIMEOUT) as ser:
		# small pause for some USB-serial adapters
		time.sleep(0.05)
		try:
			while True:
				sent = ser.write(frame)
				ser.flush()
				print(f"Sent {sent} bytes -> {bytes_to_hex(frame)}")
				time.sleep(interval)
		except KeyboardInterrupt:
			print('\nSend loop stopped by user')


if __name__ == '__main__':
	# Continuous send loop (single-line): dir flags: 0=backward, 1=forward
	send_control_loop(10000, 20000, 1000, 1400, 1, 1)
