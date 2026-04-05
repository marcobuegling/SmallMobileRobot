import RPi.GPIO as GPIO
import time
import curses
from collections import deque

MAX_DUTY_CYCLES = 80 # controls motor speed - maximum: 100
EMERGENCY_BREAK_DIST = MAX_DUTY_CYCLES / 4.0 # approximation based on motor speed - in cm
PWM_FREQUENCY = 1000 # in Hz
INPUT_INCREASE = 0.5 # defines effect of control input
ULTRASONIC_BUFFER_SIZE = 3 # number of measurements used to calculate average

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

GPIO.setmode(GPIO.BCM) # use GPIO pin numbers

# Setup output pins
output_pins = [PWMA_R, AIN1_R, AIN2_R, PWMB_R, BIN1_R, BIN2_R, PWMA_L, AIN1_L, AIN2_L, PWMB_L, BIN1_L, BIN2_L, TRIG, STBY]
for pin in output_pins:
    GPIO.setup(pin, GPIO.OUT)

# Setup input pins
input_pins = [ECHO, LINE]
for pin in input_pins:
    GPIO.setup(pin, GPIO.IN)


# Class defining a single motor using the corresponding output pins
class Motor:
    def __init__(self, label, pwm, in1, in2):
        self.label = label
        self.in1 = in1
        self.in2 = in2
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        self.pwm = GPIO.PWM(pwm, PWM_FREQUENCY)
        self.pwm.start(0)
        self.speed = 0

    # updates speed of motor to fixed value considering forward vs. backward driving
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

    # updates speed by value considering forward vs. backward driving
    def change_speed(self, value):
        self.update_speed(self.speed + value)

    # stop motor entirely
    def stop(self):
        self.pwm.stop()

    def __str__(self):
        return self.label
    

# Class defining a group of motors and providing functionality for efficient control
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

    # updates speed for all motors in group
    def update_speed(self, speed):
        self.speed = max(-MAX_DUTY_CYCLES, min(speed, MAX_DUTY_CYCLES))
        for m in self.motors:
            m.update_speed(self.speed)

    # stops all motors entirely
    def stop(self):
        for m in self.motors:
            m.stop()

    def __str__(self):
        return self.label
    

# Class defining an ultrasonic sensor with ability to store the last measurements in a buffer
class UltrasonicSensor:
    def __init__(self, label, trig, echo, buffer_size):
        self.label = label
        self.trig = trig
        self.echo = echo
        GPIO.output(self.trig, GPIO.LOW)
        self.buffer = deque(maxlen=buffer_size)

    # Reads a single value, stores it in the buffer and returns it
    def read_value(self):
        # Trigger pulse
        GPIO.output(self.trig, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trig, GPIO.LOW)

        # Measure time of pulse start and end
        pulse_start = time.time()
        pulse_end = time.time()
        while not GPIO.input(self.echo):
            pulse_start = time.time()
        while GPIO.input(self.echo):
            pulse_end = time.time()

        # Calculate distance based on ultrasonic travel time
        pulse_duration = pulse_end - pulse_start
        distance_cm = pulse_duration * 17150
        distance_cm = round(distance_cm, 2)
        self.buffer.append(distance_cm)
        return distance_cm
    
    # Calculate average of measurements stored in buffer
    def get_recent_avg(self):
        return round(sum(self.buffer) / len(self.buffer), 2)

    def __str__(self):
        return self.label


def main(stdscr):
    # Setup keyboard input
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.timeout(20) # 20 ms loop
    last_key = -1

    # Setup default values for velocity and steering
    velocity = 0.0    # -1.0 (max speed backwards) to 1.0 (max speed forwards)
    steering = 0.0    # -1.0 (max right) to 1.0 (max left)

    # Set STBY signal to turn on motors
    GPIO.output(STBY, GPIO.HIGH) 

    print("Control loop started")

    while True:
        # Get key input and current sensor data
        key = stdscr.getch()
        distance = ultrasonicFront.read_value()
        distance_avg = ultrasonicFront.get_recent_avg()

        # Log current status and sensor data
        stdscr.move(0, 0)
        stdscr.clrtoeol()
        stdscr.addstr(0, 0, f"Distance: {distance} cm")
        stdscr.addstr(1, 0, f"Distance Avg: {distance_avg} cm")
        stdscr.addstr(2, 0, f"Velocity: {velocity}")
        stdscr.addstr(3, 0, f"Steering: {steering}")
        stdscr.addstr(4, 0, f"Emergency Break: {distance_avg < EMERGENCY_BREAK_DIST} ")
        stdscr.addstr(5, 0, f"Line detected: {bool(GPIO.input(LINE))} ")
        stdscr.refresh()

        # Process key input
        if key != last_key:
            last_key = key

            # Increase/decrease velocity/steering with single keystrokes
            if key == curses.KEY_UP:
                velocity += INPUT_INCREASE
            if key == curses.KEY_DOWN:
                velocity -= INPUT_INCREASE
            if key == curses.KEY_LEFT:
                steering += INPUT_INCREASE
            if key == curses.KEY_RIGHT:
                steering -= INPUT_INCREASE
            if key == ord('s'): # stop motors entirely
                GPIO.output(STBY, False)
            if key == ord('d'): # restart motors
                GPIO.output(STBY, True)
            if key == ord('q'): # quit
                break
        
        # Clip velocity and steering to values between -1 and 1
        velocity = max(min(1.0, velocity), -1.0)
        steering = max(min(1.0, steering), -1.0)

        # Perform emergency break in case of obstacle ahead
        if distance_avg < EMERGENCY_BREAK_DIST and velocity > 0.0:
            motorsLeft.update_speed(-steering * MAX_DUTY_CYCLES)
            motorsRight.update_speed(steering * MAX_DUTY_CYCLES)
        else:
            motorsLeft.update_speed((velocity - steering) * MAX_DUTY_CYCLES)
            motorsRight.update_speed((velocity + steering) * MAX_DUTY_CYCLES)

        time.sleep(0.05)

try:
    # Setup of motors and sensors
    motorsLeft = MotorGroup("LEFT", [Motor("FL", PWMA_L, AIN1_L, AIN2_L), Motor("RL", PWMB_L, BIN1_L, BIN2_L)])
    motorsRight = MotorGroup("RIGHT", [Motor("FR", PWMA_R, AIN1_R, AIN2_R), Motor("RR", PWMB_R, BIN1_R, BIN2_R)])
    ultrasonicFront = UltrasonicSensor("US_FRONT", TRIG, ECHO, ULTRASONIC_BUFFER_SIZE)

    curses.set_escdelay(25)
    curses.wrapper(main)

finally:
    # Cleanup
    motorsLeft.stop()
    motorsRight.stop()
    print("Motors stopped")
    GPIO.cleanup()
    print("Cleanup completed")
