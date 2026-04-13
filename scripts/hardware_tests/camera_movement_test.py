import time
from adafruit_servokit import ServoKit

# If i2cdetect shows a different address than 0x40, change it here.
kit = ServoKit(channels=16, address=0x40)

# Calibrate for typical micro servos; adjust if your servos jitter or hit limits.
for ch in (0, 1):
    kit.servo[ch].actuation_range = 180         # try 160 if yours have smaller travel
    kit.servo[ch].set_pulse_width_range(600, 2400)  # microseconds; 600–2400 is a safe start

PAN_CH = 0
TILT_CH = 1

def safe_set(ch, angle, lo=10, hi=170):
    """Set servo angle with simple mechanical margins to avoid binding."""
    angle = max(lo, min(hi, angle))
    kit.servo[ch].angle = angle

# Center both axes
safe_set(PAN_CH, 90)
safe_set(TILT_CH, 90)
time.sleep(1.0)

# Simple sweep demo
try:
    # Pan left to right
    for a in range(10, 171, 2):
        safe_set(PAN_CH, a)
        time.sleep(0.01)
    for a in range(170, 9, -2):
        safe_set(PAN_CH, a)
        time.sleep(0.01)

    # Nod tilt a bit around center
    for a in range(70, 111, 2):
        safe_set(TILT_CH, a)
        time.sleep(0.02)
    for a in range(110, 69, -2):
        safe_set(TILT_CH, a)
        time.sleep(0.02)

    # Park at center
    safe_set(PAN_CH, 90)
    safe_set(TILT_CH, 90)

except KeyboardInterrupt:
    safe_set(PAN_CH, 90)
    safe_set(TILT_CH, 90)
