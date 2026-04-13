import time
from picamera2 import Picamera2

cam = Picamera2()
cam.configure(cam.create_still_configuration())
cam.start()
time.sleep(2) # let camera adjust to the light
cam.capture_file("test.jpg")
cam.stop()
