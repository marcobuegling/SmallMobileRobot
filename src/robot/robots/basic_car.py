import sys
import time
import curses
if sys.platform == "linux":
    import RPi.GPIO as GPIO
else:
    GPIO = None

from base import Robot
from robot.control.four_wheel_car_control import FourWheelCarControl
from robot.hardware.sensors import UltrasonicSensor, LineTrackingSensor
from robot.utils.config import RobotConfig

class BasicCar:
    """
    Class for a simple four wheel robot with an ultrasonic sensor and a line tracking sensor.
    Can be controlled by user input and allows live tracking of the sensor output values.
    Initialise a config file corresponding to this type of robot. See /config for an example file.
    """

    def __init__(self, cfg: RobotConfig):
        self._initialised = False

        self._motorControl = FourWheelCarControl.from_config(cfg.motors)
        self._ultrasonicFront = UltrasonicSensor(cfg.sensors.ultrasonic)
        self._lineTracker = LineTrackingSensor(cfg.sensors.line)

        self._initialised = True

    def run(self):
        if not self._initialised:
            raise RuntimeError("Robot not fully initialized")

        def _run(stdscr):
            # Setup keyboard input
            curses.cbreak()
            stdscr.keypad(True)
            stdscr.nodelay(True)
            stdscr.timeout(20) # 20 ms loop
            last_key = -1

            print("Control loop started")

            while True:
                # Get key input and current sensor data
                key = stdscr.getch()
                distance = self._ultrasonicFront.read_value()
                distance_avg = self._ultrasonicFront.get_recent_avg()
                line_tracked = self._lineTracker.read_value()

                # Calculate emergency break distance based on current velocity (approximation)
                emergency_break_dist = self._motorControl.speed * self._motorControl.base_speed / 4

                # Log current status and sensor data
                stdscr.move(0, 0)
                stdscr.clrtoeol()
                stdscr.addstr(0, 0, f"Distance: {distance} cm")
                stdscr.addstr(1, 0, f"Distance Avg: {distance_avg} cm")
                stdscr.addstr(2, 0, f"Velocity: {self._motorControl.speed}")
                stdscr.addstr(3, 0, f"Steering: {self._motorControl.steering}")
                stdscr.addstr(4, 0, f"Emergency Break: {distance_avg < emergency_break_dist} ")
                stdscr.addstr(5, 0, f"Line detected: {line_tracked} ")
                stdscr.refresh()

                # Process key input
                if key != last_key:
                    last_key = key

                    # Increase/decrease velocity/steering with single keystrokes
                    if key == curses.KEY_UP:
                        self._motorControl.accelerate()
                    if key == curses.KEY_DOWN:
                        self._motorControl.decelerate()
                    if key == curses.KEY_LEFT:
                        self._motorControl.turn_left()
                    if key == curses.KEY_RIGHT:
                        self._motorControl.turn_right()
                    if key == ord('s'): # stop motors entirely
                        self._motorControl.stop()
                    if key == ord('d'): # restart motors
                        self._motorControl.start()
                    if key == ord('q'): # quit
                        break

                # Perform emergency break in case of obstacle ahead
                if distance_avg < emergency_break_dist and self._motorControl.speed > 0.0:
                    self._motorControl.allow_forward = False
                else:
                    self._motorControl.allow_forward = True

                time.sleep(0.05)

        try:
            curses.set_escdelay(25)
            curses.wrapper(_run)

        finally:
            # Cleanup
            self._motorControl.cleanup()
            print("Motors stopped")
            GPIO.cleanup()
            print("Cleanup completed")
