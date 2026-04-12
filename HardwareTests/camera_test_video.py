import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

cam = Picamera2()
cam.configure(cam.create_video_configuration())
encoder = H264Encoder(bitrate=10000000)
cam.start_recording(encoder, "test.h264")

time.sleep(10) # record for 10 seconds

cam.stop_recording()
