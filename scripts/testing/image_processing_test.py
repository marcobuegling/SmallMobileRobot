"""
Test for live image processing, marking areas of a specified color in the camera output image.
"""

import numpy as np
import cv2
from robot.hardware.cameras import PiCamera

cam = PiCamera(mode='stream')

# HSV range for an orange object
LOWER = np.array([10, 120, 120])
UPPER = np.array([25, 255, 255])

while True:
    frame = cam.video_stream_frame()
    bgr   = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    hsv   = cv2.cvtColor(bgr,   cv2.COLOR_BGR2HSV)

    mask    = cv2.inRange(hsv, LOWER, UPPER)
    mask    = cv2.erode(mask, None, iterations=2)   # remove noise
    mask    = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius > 10:
            cv2.circle(bgr, (int(x), int(y)), int(radius), (0, 255, 0), 2)
            cv2.circle(bgr, (int(x), int(y)), 4, (0, 0, 255), -1)

    cv2.imshow("Tracker", bgr)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.close()
cv2.destroyAllWindows()
