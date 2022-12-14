#! /usr/bin/python2

from picamera import PiCamera
import time

camera = PiCamera()

def captureImg():
    # Code to call on camera and take photo
    print("Starting Camera")
    camera.start_preview()
    time.sleep(5)
    camera.capture('./images/image_1.jpg')
    print("Picture Captured")
    camera.stop_preview()
