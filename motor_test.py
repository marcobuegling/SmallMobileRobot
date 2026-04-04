import RPi.GPIO as GPIO
import time

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

GPIO.setmode(GPIO.BCM)

# Setup pins
pins = [PWMA_R, AIN1_R, AIN2_R, PWMB_R, BIN1_R, BIN2_R, PWMA_L, AIN1_L, AIN2_L, PWMB_L, BIN1_L, BIN2_L]
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

# Setup PWM
pwmA_R = GPIO.PWM(PWMA_R, 1000) # 1 kHz
pwmB_R = GPIO.PWM(PWMB_R, 1000)
pwmA_L = GPIO.PWM(PWMA_L, 1000)
pwmB_L = GPIO.PWM(PWMB_L, 1000)

pwmA_R.start(0)
pwmB_R.start(0)
pwmA_L.start(0)
pwmB_L.start(0)

def motor_1_forward(speed): # front right
    GPIO.output(AIN1_R, GPIO.HIGH)
    GPIO.output(AIN2_R, GPIO.LOW)
    pwmA_R.ChangeDutyCycle(speed)

def motor_2_forward(speed): # back right
    GPIO.output(BIN1_R, GPIO.HIGH)
    GPIO.output(BIN2_R, GPIO.LOW)
    pwmB_R.ChangeDutyCycle(speed)

def motor_3_forward(speed): # front left
    if speed >= 0:
        GPIO.output(AIN1_L, GPIO.HIGH)
        GPIO.output(AIN2_L, GPIO.LOW)
    else:
        GPIO.output(AIN1_L, GPIO.LOW)
        GPIO.output(AIN2_L, GPIO.HIGH)
    pwmA_L.ChangeDutyCycle(abs(speed))

def motor_4_forward(speed): # back left
    if speed >= 0:
        GPIO.output(BIN1_L, GPIO.HIGH)
        GPIO.output(BIN2_L, GPIO.LOW)
    else:
        GPIO.output(BIN1_L, GPIO.LOW)
        GPIO.output(BIN2_L, GPIO.HIGH)
    pwmB_L.ChangeDutyCycle(abs(speed))

def motor_forward(speed=50):
    GPIO.output(AIN1_R, GPIO.HIGH)
    GPIO.output(AIN2_R, GPIO.LOW)
    GPIO.output(BIN1_R, GPIO.HIGH)
    GPIO.output(BIN2_R, GPIO.LOW)
    GPIO.output(AIN1_L, GPIO.HIGH)
    GPIO.output(AIN2_L, GPIO.LOW)
    GPIO.output(BIN1_L, GPIO.HIGH)
    GPIO.output(BIN2_L, GPIO.LOW)
    pwmA_R.ChangeDutyCycle(speed)
    pwmB_R.ChangeDutyCycle(speed)
    pwmA_L.ChangeDutyCycle(speed)
    pwmB_L.ChangeDutyCycle(speed)

def motor_reverse(speed=50):
    GPIO.output(AIN1_R, GPIO.LOW)
    GPIO.output(AIN2_R, GPIO.HIGH)
    GPIO.output(BIN1_R, GPIO.LOW)
    GPIO.output(BIN2_R, GPIO.HIGH)
    GPIO.output(AIN1_L, GPIO.LOW)
    GPIO.output(AIN2_L, GPIO.HIGH)
    GPIO.output(BIN1_L, GPIO.LOW)
    GPIO.output(BIN2_L, GPIO.HIGH)
    pwmA_R.ChangeDutyCycle(speed)
    pwmB_R.ChangeDutyCycle(speed)
    pwmA_L.ChangeDutyCycle(speed)
    pwmB_L.ChangeDutyCycle(speed)

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

    # print("Motor 1")
    # motor_1_forward(speed)
    # time.sleep(2)
    # motor_stop()
    
    # print("Motor 2")
    # motor_2_forward(speed)
    # time.sleep(2)
    # motor_stop()
    
    # print("Motor 3")
    # motor_3_forward(speed)
    # time.sleep(2)
    # motor_stop()
    
    # print("Motor 4")
    # motor_4_forward(speed)
    # time.sleep(2)
    # motor_stop()
    
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