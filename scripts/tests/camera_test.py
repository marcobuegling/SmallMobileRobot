"""
Script for testing the functionality provided by the PiCamera and PanTiltUnit classes.
"""
import curses
from robot.hardware.cameras import PiCamera
from robot.hardware.pan_tilt_unit import PanTiltUnit

def main(stdscr):
    # Setup keyboard input
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.timeout(20) # 20 ms loop

    while(True):
        # Get key input
        key = stdscr.getch()
        if key == curses.KEY_UP:
            pan_tilt.step_up()
        if key == curses.KEY_DOWN:
            pan_tilt.step_down()
        if key == curses.KEY_LEFT:
            pan_tilt.step_left()
        if key == curses.KEY_RIGHT:
            pan_tilt.step_right()
        if key == ord('c'): # center the camera
            pan_tilt.center()
        if key == ord('t'): # test setting to a specified position
            pan_tilt.set_position(0.0, 0.0)
        if key == ord('z'):
            pan_tilt.set_position(180.0, 180.0)
        if key == ord('u'):
            pan_tilt.set_position(180.0, 190.0)
        if key == ord('i'): # take image
            camera.single_image()
        if key == ord('v'): # take video
            camera.single_video(5.0)
        if key == ord('q'): # quit
            break

try:
    pan_tilt = PanTiltUnit()
    camera = PiCamera(mode='video')

    pan_tilt.center()

    curses.set_escdelay(25)
    curses.wrapper(main)
finally:
    camera.close()
