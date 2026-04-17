import sys
if sys.platform == "linux":
    import RPi.GPIO as GPIO
else:
    GPIO = None

# Class defining a single motor using the corresponding output pins
class Motor:
    def __init__(self, label: str, pwm: int, pwm_frequency: float, in1: int, in2: int):
        self.label = label
        self._in1 = in1
        self._in2 = in2
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        self._pwm = GPIO.PWM(pwm, pwm_frequency)
        self._pwm.start(0)
        self._speed = 0

    # updates speed of motor to fixed value considering forward vs. backward driving
    def update_speed(self, speed: float):
        self._speed = speed
        if self._speed > 0:
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)
        elif self._speed < 0:
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.HIGH)
        else:
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.LOW)
        self._pwm.ChangeDutyCycle(abs(self._speed))

    # updates speed by value considering forward vs. backward driving
    def change_speed(self, value: float):
        self.update_speed(self._speed + value)

    # stop motor entirely
    def stop(self):
        self._pwm.stop()

    def __str__(self):
        return self.label
    

# Class defining a group of motors and providing functionality for efficient control
class MotorGroup:
    def __init__(self, label: str, motors: list[Motor], max_speed: float):
        self.label = label
        if len(motors) > 0:
            self._motors = motors
        else:
            self._motors = []
        for m in self._motors:
            m.update_speed(0)
        self._speed = 0
        self._max_speed = max_speed
    
    def add_motor(self, motor):
        self._motors.append(motor)

    # updates speed for all motors in group
    def update_speed(self, speed: float):
        self._speed = max(-self._max_speed, min(speed, self._max_speed))
        for m in self.motors:
            m.update_speed(self._speed)

    # stops all motors entirely
    def stop(self):
        for m in self._motors:
            m.stop()

    def __str__(self):
        return self.label
    