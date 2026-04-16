import sys
if sys.platform == "linux":
    import RPi.GPIO as GPIO
else:
    GPIO = None
from robot.hardware.motors import MotorGroup, Motor
from collections import overload

class FourWheelCarControl:
    """
    Provides an interface for controlling a basic four wheel (and motor) car with common motor drivers like the TB6612FNG.
    Each motor has three pins: PWM, IN1 and IN2. The motor drivers share one STBY pin.
    """
    @overload
    def __init__(
        self, 
        base_speed : float, 
        stby: int,
        pwma_l: int, 
        ain1_l: int, 
        ain2_l: int, 
        pwmb_l: int, 
        bin1_l: int, 
        bin2_l: int, 
        pwma_r: int, 
        ain1_r: int, 
        ain2_r: int, 
        pwmb_r: int, 
        bin1_r: int, 
        bin2_r: int,
    ):
        """
        Args:
            base_speed: values 0 and 100, defines max duty cycles for motors
            stby: stby pin shared by all motor drivers
            pwma_l: pwm pin of front left motor
            ain1_l: in1 pin of front left motor
            ain2_l: in2 pin of front left motor
            pwmb_l: pwm pin of rear left motor
            bin1_l: in1 pin of rear left motor
            bin2_l: in2 pin of rear left motor
            pwma_r: pwm pin of front right motor
            ain1_r: in1 pin of front right motor
            ain2_r: in2 pin of front right motor
            pwmb_r: pwm pin of rear right motor
            bin1_r: in1 pin of rear right motor
            bin2_r: in2 pin of rear right motor
        """
        if base_speed < 0.0 or base_speed > 100.0:
            raise ValueError("base_speed must be in range (0.0, 100.0)")
        self._base_speed = base_speed
        self._speed = 0.0
        self._steering = 0.0

        self._motors_left = MotorGroup("LEFT", [Motor("FL", pwma_l, ain1_l, ain2_l), Motor("RL", pwmb_l, bin1_l, bin2_l)], self._base_speed)
        self._motors_right = MotorGroup("RIGHT", [Motor("FR", pwma_r, ain1_r, ain2_r), Motor("RR", pwmb_r, bin1_r, bin2_r)], self._base_speed)
        self._stby = stby

        self.start()

    def _update_motor_speed(self):
        rel_speed_left = self._clamp(self._speed - self._steering, -1.0, 1.0)
        rel_speed_right = self._clamp(self._speed + self._steering, -1.0, 1.0)
        self._motors_left.update_speed(self._base_speed * rel_speed_left)
        self._motors_right.update_speed(self._base_speed * rel_speed_right)

    def set_speed(self, speed: float):
        """
        Sets speed to specified value. Clamps speed to (-1.0, 1.0)
        """
        self._speed = self._clamp(speed, -1.0, 1.0)
        self._update_motor_speed()

    def change_speed(self, change: float):
        """
        Changes speed by specified value. Clamps speed to (-1.0, 1.0)
        """
        self._speed = self._clamp(self._speed + change, -1.0, 1.0)
        self._update_motor_speed()

    def set_steering(self, steering: float):
        """
        Sets steering to specified value. Clamps steering to (-1.0, 1.0)
        """
        self._steering = self._clamp(steering, -1.0, 1.0)
        self._update_motor_speed()

    def change_steering(self, change: float):
        """
        Changes steering by specified value. Clamps steering to (-1.0, 1.0)
        """
        self._steering = self._clamp(self._steering + change, -1.0, 1.0)
        self._update_motor_speed()

    def start(self):
        """
        Activate motor drivers by setting a high signal on the stby pin
        """
        GPIO.output(self._stby, True)

    def stop(self):
        """
        Set car into stby mode, stopping completely until start() is called
        """
        GPIO.output(self._stby, False)

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))

# Potentially smoother mapping
# def map_controls(v, s):
#     # exponential response
#     k = 0.5
#     v = (1-k)*v + k*(v**3)
#     s = (1-k)*s + k*(s**3)

#     # speed-dependent steering
#     s *= (1 - abs(v))

#     # arcade mix
#     left  = v + s
#     right = v - s

#     # normalize
#     max_val = max(1, abs(left), abs(right))
#     left  /= max_val
#     right /= max_val

#     return left, right