# Small Mobile Robot
This is a personal project of mine with the goal of designing and programming a mobile robot myself. I constantly want to expand its capabilities by improving both hardware and software.

## Key Features
- **Manual driving mode**: Control using keyboard via ssh
- **Automatic safety stop**: Stops automatically when driving towards obstacle ahead
- **Live transfer of sensor data**: Sends live sensor data to remote device

## Hardware
- Four 6V DC motors
- Two TB6612FNG motor drivers
- Raspberry Pi Zero 2
- 6V battery compartment w/ 4 AA batteries
- Powerbank
- Homemade chassis
- Arducam Pan Tilt Platform

## Sensors
- HC-SR04 ultrasonic sensor
- HW-511 line tracker module
- Raspberry Pi Camera Module 3

## Setup
If you want to use this code for your own project on a Raspberry Pi, make sure that your virtual enviroment has all the Pi-specific system-wide packages needed. You can do so by inheriting them on environment creation after making sure they are installed:

```
sudo apt install python3-gpiozero python3-rpi.gpio i2c-tools
python3 -m venv venv --system-site-packages
```

Then, install the dependencies specific to this project:

```
source venv/bin/activate
pip install -r requirements.txt
```

 


