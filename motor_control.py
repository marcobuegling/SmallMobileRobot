import RPi.GPIO as GPIO
import time
import curses
from collections import deque

MAX_DUTY_CYCLES = 80 # 100
EMERGENCY_BREAK_DIST = MAX_DUTY_CYCLES / 4.0

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
TRIG = 18
ECHO = 25
STBY = 10
LINE = 12

GPIO.setmode(GPIO.BCM)

# Setup pins
output_pins = [PWMA_R, AIN1_R, AIN2_R, PWMB_R, BIN1_R, BIN2_R, PWMA_L, AIN1_L, AIN2_L, PWMB_L, BIN1_L, BIN2_L, TRIG, STBY]
for pin in output_pins:
    GPIO.setup(pin, GPIO.OUT)

input_pins = [ECHO, LINE]
for pin in input_pins:
    GPIO.setup(pin, GPIO.IN)


class Motor:
    def __init__(self, label, pwm, in1, in2):
        self.label = label
        self.in1 = in1
        self.in2 = in2
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        self.pwm = GPIO.PWM(pwm, 1000) # 1 kHz
        self.pwm.start(0)
        self.speed = 0

    def update_speed(self, speed):
        self.speed = max(-MAX_DUTY_CYCLES, min(speed, MAX_DUTY_CYCLES))
        if self.speed > 0:
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)
        elif self.speed < 0:
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.HIGH)
        else:
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(abs(self.speed))

    def change_speed(self, value):
        self.update_speed(self.speed + value)

    def stop(self):
        self.pwm.stop()

    def __str__(self):
        return self.label
    
class MotorGroup:
    def __init__(self, label, motors):
        self.label = label
        if len(motors) > 0:
            self.motors = motors
        else:
            self.motors = []
        for m in self.motors:
            m.update_speed(0)
        self.speed = 0
    
    def add_motor(self, motor):
        self.motors.append(motor)

    def update_speed(self, speed):
        self.speed = max(-MAX_DUTY_CYCLES, min(speed, MAX_DUTY_CYCLES))
        for m in self.motors:
            m.update_speed(self.speed)

    def stop(self):
        for m in self.motors:
            m.stop()

    def __str__(self):
        return self.label
    
class UltrasonicSensor:
    def __init__(self, label, trig, echo):
        self.label = label
        self.trig = trig
        self.echo = echo
        GPIO.output(self.trig, False)
        self.buffer = deque(maxlen=3)

    def read_value(self):
        # Trigger pulse
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

        pulse_start = time.time()
        pulse_end = time.time()

        # Wait for echo start
        while not GPIO.input(self.echo):
            pulse_start = time.time()
        while GPIO.input(self.echo):
            pulse_end = time.time()
            #if pulse_end - pulse_start > 500 / 17150:
            #    break

        # Calculate distance
        pulse_duration = pulse_end - pulse_start
        distance_cm = pulse_duration * 17150
        distance_cm = round(distance_cm, 2)
        self.buffer.append(distance_cm)
        return distance_cm
    
    def get_recent_avg(self):
        return round(sum(self.buffer) / len(self.buffer), 2)

def main(stdscr):
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.timeout(20) # 20 ms loop

    last_key = -1

    # Setup default values for velocity and steering
    velocity = 0.0    # -1.0 (max speed backwards) to 1.0 (max speed forwards)
    steering = 0.0    # -1.0 (max right) to 1.0 (max left)

    GPIO.output(STBY, True)

    print("Control loop started")

    while True:
        key = stdscr.getch()
        distance = ultrasonicFront.read_value()
        distance_avg = ultrasonicFront.get_recent_avg()
        stdscr.move(0, 0)
        stdscr.clrtoeol()
        stdscr.addstr(0, 0, f"Distance: {distance} cm")
        stdscr.addstr(1, 0, f"Distance Avg: {distance_avg} cm")
        stdscr.addstr(2, 0, f"Velocity: {velocity}")
        stdscr.addstr(3, 0, f"Steering: {steering}")
        stdscr.addstr(4, 0, f"Emergency Break: {distance_avg < EMERGENCY_BREAK_DIST} ")
        stdscr.addstr(5, 0, f"Line detected: {bool(GPIO.input(LINE))} ")
        stdscr.refresh()

        if key != last_key:
            last_key = key

            if key == curses.KEY_UP:
                velocity += 1.0
            if key == curses.KEY_DOWN:
                velocity -= 1.0
            if key == curses.KEY_LEFT:
                steering += 1.0
            if key == curses.KEY_RIGHT:
                steering -= 1.0
            if key == ord('s'):
                GPIO.output(STBY, False)
            if key == ord('d'):
                GPIO.output(STBY, True)
            if key == ord('q'):
                break

        velocity = max(min(1.0, velocity), -1.0)
        steering = max(min(1.0, steering), -1.0)

        if distance_avg < EMERGENCY_BREAK_DIST and velocity > 0.0:
            motorsLeft.update_speed(-steering * MAX_DUTY_CYCLES)
            motorsRight.update_speed(steering * MAX_DUTY_CYCLES)
        else:
            motorsLeft.update_speed((velocity - steering) * MAX_DUTY_CYCLES)
            motorsRight.update_speed((velocity + steering) * MAX_DUTY_CYCLES)

        time.sleep(0.05)

try:
    # Setup
    motorsLeft = MotorGroup("LEFT", [Motor("FL", PWMA_L, AIN1_L, AIN2_L), Motor("RL", PWMB_L, BIN1_L, BIN2_L)])
    motorsRight = MotorGroup("RIGHT", [Motor("FR", PWMA_R, AIN1_R, AIN2_R), Motor("RR", PWMB_R, BIN1_R, BIN2_R)])
    ultrasonicFront = UltrasonicSensor("US_FRONT", TRIG, ECHO)

    curses.set_escdelay(25) # 25 ms instead of 1000 ms
    curses.wrapper(main)

    # Test
    # velocity = 1.0
    # motorsLeft.update_speed(velocity * MAX_DUTY_CYCLES - steering * MAX_DUTY_CYCLES)
    # motorsRight.update_speed(velocity * MAX_DUTY_CYCLES + steering * MAX_DUTY_CYCLES)
    # time.sleep(1.5)
    # steering = 1.0
    # motorsLeft.update_speed(velocity * MAX_DUTY_CYCLES - steering * MAX_DUTY_CYCLES)
    # motorsRight.update_speed(velocity * MAX_DUTY_CYCLES + steering * MAX_DUTY_CYCLES)
    # time.sleep(1.5)
    # velocity = 0.0
    # motorsLeft.update_speed(velocity * MAX_DUTY_CYCLES - steering * MAX_DUTY_CYCLES)
    # motorsRight.update_speed(velocity * MAX_DUTY_CYCLES + steering * MAX_DUTY_CYCLES)
    # time.sleep(1.5)
    # steering = 0.0
    # motorsLeft.update_speed(velocity * MAX_DUTY_CYCLES - steering * MAX_DUTY_CYCLES)
    # motorsRight.update_speed(velocity * MAX_DUTY_CYCLES + steering * MAX_DUTY_CYCLES)

    # Control loop
    # while True:
    #     motorsLeft.update_speed(velocity * MAX_DUTY_CYCLES - steering * MAX_DUTY_CYCLES)
    #     motorsRight.update_speed(velocity * MAX_DUTY_CYCLES + steering * MAX_DUTY_CYCLES)

finally:
    motorsLeft.stop()
    motorsRight.stop()
    print("Motors stopped")
    GPIO.cleanup()
    print("Cleanup completed")
