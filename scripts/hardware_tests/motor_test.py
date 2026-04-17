import sys
if sys.platform == "linux":
    import RPi.GPIO as GPIO
else:
    GPIO = None
import time

MAX_DUTY_CYCLES = 80 # controls motor speed - maximum: 100
PWM_FREQUENCY = 1000 # in Hz

# Pin definitions
PWMA_R = 21
AIN1_R = 16
AIN2_R = 20
PWMB_R = 26
BIN1_R = 6
BIN2_R = 5
PWMA_L = 4
AIN1_L = 17
AIN2_L = 27
PWMB_L = 22
BIN1_L = 24
BIN2_L = 23
STBY = 10 # STBY can also be powered permanently by 3.3V pin

# Refer to channels using Broadcom SOC channel (aka GPIO) numbering
GPIO.setmode(GPIO.BCM)

# Setup pins
pins = [PWMA_R, AIN1_R, AIN2_R, PWMB_R, BIN1_R, BIN2_R, PWMA_L, AIN1_L, AIN2_L, PWMB_L, BIN1_L, BIN2_L, STBY]
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

# Setup PWM
pwmA_R = GPIO.PWM(PWMA_R, PWM_FREQUENCY)
pwmB_R = GPIO.PWM(PWMB_R, PWM_FREQUENCY)
pwmA_L = GPIO.PWM(PWMA_L, PWM_FREQUENCY)
pwmB_L = GPIO.PWM(PWMB_L, PWM_FREQUENCY)

pwmA_R.start(0)
pwmB_R.start(0)
pwmA_L.start(0)
pwmB_L.start(0)

def motor_1_forward(MAX_DUTY_CYCLES): # front right
    GPIO.output(AIN1_R, GPIO.HIGH)
    GPIO.output(AIN2_R, GPIO.LOW)
    pwmA_R.ChangeDutyCycle(MAX_DUTY_CYCLES)

def motor_2_forward(MAX_DUTY_CYCLES): # back right
    GPIO.output(BIN1_R, GPIO.HIGH)
    GPIO.output(BIN2_R, GPIO.LOW)
    pwmB_R.ChangeDutyCycle(MAX_DUTY_CYCLES)

def motor_3_forward(MAX_DUTY_CYCLES): # front left
    if MAX_DUTY_CYCLES >= 0:
        GPIO.output(AIN1_L, GPIO.HIGH)
        GPIO.output(AIN2_L, GPIO.LOW)
    else:
        GPIO.output(AIN1_L, GPIO.LOW)
        GPIO.output(AIN2_L, GPIO.HIGH)
    pwmA_L.ChangeDutyCycle(abs(MAX_DUTY_CYCLES))

def motor_4_forward(MAX_DUTY_CYCLES): # back left
    if MAX_DUTY_CYCLES >= 0:
        GPIO.output(BIN1_L, GPIO.HIGH)
        GPIO.output(BIN2_L, GPIO.LOW)
    else:
        GPIO.output(BIN1_L, GPIO.LOW)
        GPIO.output(BIN2_L, GPIO.HIGH)
    pwmB_L.ChangeDutyCycle(abs(MAX_DUTY_CYCLES))

def motor_forward(MAX_DUTY_CYCLES=50):
    GPIO.output(AIN1_R, GPIO.HIGH)
    GPIO.output(AIN2_R, GPIO.LOW)
    GPIO.output(BIN1_R, GPIO.HIGH)
    GPIO.output(BIN2_R, GPIO.LOW)
    GPIO.output(AIN1_L, GPIO.HIGH)
    GPIO.output(AIN2_L, GPIO.LOW)
    GPIO.output(BIN1_L, GPIO.HIGH)
    GPIO.output(BIN2_L, GPIO.LOW)
    pwmA_R.ChangeDutyCycle(MAX_DUTY_CYCLES)
    pwmB_R.ChangeDutyCycle(MAX_DUTY_CYCLES)
    pwmA_L.ChangeDutyCycle(MAX_DUTY_CYCLES)
    pwmB_L.ChangeDutyCycle(MAX_DUTY_CYCLES)

def motor_reverse(MAX_DUTY_CYCLES=50):
    GPIO.output(AIN1_R, GPIO.LOW)
    GPIO.output(AIN2_R, GPIO.HIGH)
    GPIO.output(BIN1_R, GPIO.LOW)
    GPIO.output(BIN2_R, GPIO.HIGH)
    GPIO.output(AIN1_L, GPIO.LOW)
    GPIO.output(AIN2_L, GPIO.HIGH)
    GPIO.output(BIN1_L, GPIO.LOW)
    GPIO.output(BIN2_L, GPIO.HIGH)
    pwmA_R.ChangeDutyCycle(MAX_DUTY_CYCLES)
    pwmB_R.ChangeDutyCycle(MAX_DUTY_CYCLES)
    pwmA_L.ChangeDutyCycle(MAX_DUTY_CYCLES)
    pwmB_L.ChangeDutyCycle(MAX_DUTY_CYCLES)

def motor_stop():
    pwmA_R.ChangeDutyCycle(0)
    pwmB_R.ChangeDutyCycle(0)
    pwmA_L.ChangeDutyCycle(0)
    pwmB_L.ChangeDutyCycle(0)
    GPIO.output(AIN1_R, GPIO.LOW)
    GPIO.output(AIN2_R, GPIO.LOW)
    GPIO.output(BIN1_R, GPIO.LOW)
    GPIO.output(BIN2_R, GPIO.LOW)
    GPIO.output(AIN1_L, GPIO.LOW)
    GPIO.output(AIN2_L, GPIO.LOW)
    GPIO.output(BIN1_L, GPIO.LOW)
    GPIO.output(BIN2_L, GPIO.LOW)

try:
    speed=50

    GPIO.output(STBY, GPIO.HIGH)
    
    print("Forward")
    motor_forward(speed)
    time.sleep(2)

    print("Turn")
    motor_1_forward(speed)
    motor_2_forward(speed)
    motor_3_forward(-speed)
    motor_4_forward(-speed)
    time.sleep(2.8)

    print("Reverse")
    motor_reverse(speed)
    time.sleep(2)
    
    print("Forward")
    motor_forward(speed)
    time.sleep(4)

    print("Stop")
    motor_stop()
    time.sleep(1)

finally:
    pwmA_R.stop()
    pwmB_R.stop()
    pwmA_L.stop()
    pwmB_L.stop()
    GPIO.cleanup()
