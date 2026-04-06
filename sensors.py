import RPi.GPIO as GPIO
import time
from collections import deque

# Class defining an ultrasonic sensor with ability to store the last measurements in a buffer
class UltrasonicSensor:
    def __init__(self, label: str, trig: int, echo: int, buffer_size: int):
        self.label = label
        self._trig = trig
        self._echo = echo
        GPIO.output(self._trig, GPIO.LOW)
        self._buffer = deque(maxlen=buffer_size)

    # Reads a single value, stores it in the buffer and returns it
    def read_value(self) -> float:
        # Trigger pulse
        GPIO.output(self._trig, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self._trig, GPIO.LOW)

        # Measure time of pulse start and end
        pulse_start = time.time()
        pulse_end = time.time()
        while not GPIO.input(self._echo):
            pulse_start = time.time()
        while GPIO.input(self._echo):
            pulse_end = time.time()

        # Calculate distance based on ultrasonic travel time
        pulse_duration = pulse_end - pulse_start
        distance_cm = pulse_duration * 17150
        distance_cm = round(distance_cm, 2)
        self._buffer.append(distance_cm)
        return distance_cm
    
    # Calculate average of measurements stored in buffer
    def get_recent_avg(self) -> float:
        return round(sum(self._buffer) / len(self._buffer), 2)

    def __str__(self):
        return self.label
    

# Class defining a line tracking sensor
class LineTrackingSensor:
    def __init__(self, label: str, signal: int):
        self.label = label
        self._signal = signal

    # Returns true if line detected, false otherwise
    def read_value(self) -> bool:
        return bool(GPIO.input(self._signal))

    def __str__(self):
        return self.label