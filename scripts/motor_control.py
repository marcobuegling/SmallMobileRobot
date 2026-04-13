import RPi.GPIO as GPIO
import time
import curses

from motors import Motor, MotorGroup
from sensors import UltrasonicSensor, LineTrackingSensor


MAX_DUTY_CYCLES = 80 # controls motor speed - maximum: 100
PWM_FREQUENCY = 1000 # in Hz
INPUT_INCREASE = 0.5 # defines effect of control input
ULTRASONIC_BUFFER_SIZE = 3 # number of measurements used to calculate average for ultrasonic sensor


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

# Refer to pins by the Broadcom SOC channel (aka GPIO) numbering
GPIO.setmode(GPIO.BCM)

# Setup output pins
output_pins = [PWMA_R, AIN1_R, AIN2_R, PWMB_R, BIN1_R, BIN2_R, PWMA_L, AIN1_L, AIN2_L, PWMB_L, BIN1_L, BIN2_L, TRIG, STBY]
for pin in output_pins:
    GPIO.setup(pin, GPIO.OUT)

# Setup input pins
input_pins = [ECHO, LINE]
for pin in input_pins:
    GPIO.setup(pin, GPIO.IN)


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
        line_tracked = lineTracker.read_value()

        # Calculate emergency break distance based on current velocity (approximation)
        emergency_break_dist = velocity * MAX_DUTY_CYCLES / 4

        # Log current status and sensor data
        stdscr.move(0, 0)
        stdscr.clrtoeol()
        stdscr.addstr(0, 0, f"Distance: {distance} cm")
        stdscr.addstr(1, 0, f"Distance Avg: {distance_avg} cm")
        stdscr.addstr(2, 0, f"Velocity: {velocity}")
        stdscr.addstr(3, 0, f"Steering: {steering}")
        stdscr.addstr(4, 0, f"Emergency Break: {distance_avg < emergency_break_dist} ")
        stdscr.addstr(5, 0, f"Line detected: {line_tracked} ")
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
        if distance_avg < emergency_break_dist and velocity > 0.0:
            motorsLeft.update_speed(-steering * MAX_DUTY_CYCLES)
            motorsRight.update_speed(steering * MAX_DUTY_CYCLES)
        else:
            motorsLeft.update_speed((velocity - steering) * MAX_DUTY_CYCLES)
            motorsRight.update_speed((velocity + steering) * MAX_DUTY_CYCLES)

        time.sleep(0.05)

try:
    # Setup of motors and sensors
    motorsLeft = MotorGroup("LEFT", [Motor("FL", PWMA_L, AIN1_L, AIN2_L), Motor("RL", PWMB_L, BIN1_L, BIN2_L)], MAX_DUTY_CYCLES)
    motorsRight = MotorGroup("RIGHT", [Motor("FR", PWMA_R, AIN1_R, AIN2_R), Motor("RR", PWMB_R, BIN1_R, BIN2_R)], MAX_DUTY_CYCLES)
    ultrasonicFront = UltrasonicSensor("US_FRONT", TRIG, ECHO, ULTRASONIC_BUFFER_SIZE)
    lineTracker = LineTrackingSensor("LINE_TRACKER", LINE)

    curses.set_escdelay(25)
    curses.wrapper(main)

finally:
    # Cleanup
    motorsLeft.stop()
    motorsRight.stop()
    print("Motors stopped")
    GPIO.cleanup()
    print("Cleanup completed")
