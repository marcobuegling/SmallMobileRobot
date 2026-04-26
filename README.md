# Small Mobile Robot
This is a personal project of mine with the goal of designing and programming a mobile robot myself. I constantly want to expand its capabilities by improving both hardware and software.

## Key Features
- **Manual driving mode**: Control using keyboard via ssh
- **Automatic safety stop**: Stops automatically when driving towards obstacle ahead
- **Line tracking**: Basic line tracker following dark line on light ground
- **Live transfer of sensor data**: Sends live sensor data to remote device
- **Library**: Features interfaces for sensors, motors and cameras commonly used with Raspberry Pis

## Hardware
### Basis
- Raspberry Pi Zero 2
- Powerbank
- Homemade chassis
- Arducam Pan Tilt Platform

### Motors
- Four 6V DC motors
- Two TB6612FNG motor drivers
- 6V battery compartment w/ 4 AA batteries

### Sensors
- HC-SR04 ultrasonic sensor
- HW-511 line tracker module
- Varying additional sensors compatible with Raspberry Pi
- Raspberry Pi Camera Module 3

## Setup
If you want to use this code for your own project on a Raspberry Pi, make sure that all Pi-specific system dependencies are installed. They are not included in the requirements.txt, which only includes the packages you should install in your virtual environment for this project. Install system dependencies:

```
sudo apt install python3-gpiozero python3-rpi.gpio i2c-tools libcap-dev
```

Create the virtual environments including the system packages:

```
python3 -m venv venv --system-site-packages
```

Finally, install the dependencies specific to this project and the source code in your virtual environment:

```
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

 


