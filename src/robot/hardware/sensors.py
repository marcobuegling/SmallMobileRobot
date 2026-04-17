if sys.platform == "linux":
    import RPi.GPIO as GPIO
else:
    GPIO = None
import time
from collections import overload, deque

# Base class for sensor modules
class Sensor:
    def __init__(self, output_type: type):
        self._output_type = type

    @property
    def output_type(self) -> type:
        return self._output_type

    def __str__(self):
        return self._label
    
# Class representing an ultrasonic sensor module (HC-SR04 or similar) with ability to store the last measurements in a buffer
class UltrasonicSensor(Sensor):
    @overload
    def __init__(self, trig_pin: int, echo_pin: int, buffer_size: int):
        Sensor.__init__(self, float)
        self._trig = trig_pin
        self._echo = echo_pin
        GPIO.output(self._trig, GPIO.LOW)
        self._buffer = deque(maxlen=buffer_size)

    @overload

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
    

# Class representing a line tracking sensor module (HW-511 or similar)
class LineTrackingSensor(Sensor):
    def __init__(self, signal_pin: int):
        Sensor.__init__(self, bool)
        self._signal = signal_pin

    # Returns true if line detected, false otherwise
    def read_value(self) -> bool:
        return bool(GPIO.input(self._signal))
    

# Class representing a passive infrared (PIR) sensor module (HW-416A or similar)
class PassiveInfraredSensor(Sensor):
    def __init__(self, signal_pin: int):
        Sensor.__init__(self, bool)
        self._signal = signal_pin

    # Returns true if movement detected, false otherwise
    def read_value(self) -> bool:
        return bool(GPIO.input(self._signal))
