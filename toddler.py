#!/usr/bin/env python
__TODDLER_VERSION__ = "1.0.0"

# constants
THRESHOLD_SONAR = 19
THRESHOLD_LIGHT = 100
THRESHOLD_IR = 200

SATELLITE_X = 0.69
SATELLITE_Y = 0.00
SATELLITE_Z = 2.95

import time
import numpy as np
import cv2
import datetime

# Hardware test code
class Toddler:
    def __init__(self, IO):
        print 'I am a toddler playing in a sandbox'
        self.IO = IO
        self.digital = [0, 0, 0, 0, 0, 0, 0, 0]
        self.analog = [0, 0, 0, 0, 0, 0, 0, 0]
        self.emergency_stop = False

    # Move where space is available
    def move(self):

        ir_left = self.analog[1]
        ir_right = self.analog[2]

        l = ir_left <= THRESHOLD_IR
        r = ir_right <= THRESHOLD_IR

        # if both left and right are blocked
        if not l and not r:
            self.IO.setMotors(-100, -100)
            time.sleep(1)

        # if left is free but right is blocked
        if l and not r:
            self.IO.setMotors(100, -100)
            time.sleep(0.5)

        # if right is free but left is blocked
        if not l and r:
            self.IO.setMotors(-100, 100)
            time.sleep(0.5)

        # if both left and right are available
        if l and r:
            self.IO.setMotors(100, -100)

    def rotate(self, degrees):
        if degrees == 0: return
        if degrees >= 0: self.IO.setMotors(-100, 100)
        else: self.IO.setMotors(100, -100)
        time.sleep(3)
        return

    # x and y distance from deployment base
    # theta is angle from deployment base, 0 pointing east
    def find_satellite(self, x, y, theta):

        # finding required bot rotation
        slope_y = (y - SATELLITE_Y) / (x - SATELLITE_X)
        required_bot_rotation = np.rad2deg(np.arctan(slope_y)) - theta + 180

        # optimize angle
        if abs(required_bot_rotation) > 180:
            if required_bot_rotation > 0: required_bot_rotation -= 360
            else: required_bot_rotation += 360

        # finding required servo angle
        distance_from_satellite = np.sqrt((y - SATELLITE_Y)**2 + (x - SATELLITE_X)**2)
        slope_z = SATELLITE_Z / distance_from_satellite
        required_servo_angle = np.rad2deg(np.arctan(slope_z))

        return required_bot_rotation, required_servo_angle

    # This is a callback that will be called repeatedly.
    # It has its dedicated thread so you can keep block it.
    def Control(self, OK):

        # mot = [False, False, False]
        # motPrev = [False, False, False]
        # pos = 180

        while OK():

            # Read once in every 0.05s
            time.sleep(0.05)

            # Read Sensor Data
            self.digital = self.IO.getInputs()
            self.analog = self.IO.getSensors()

            # Print sensor data to console
            print(self.analog, self.digital)

            # Emergency stop on mot
            if self.digital[6]: self.emergency_stop = not self.emergency_stop
            if self.emergency_stop: self.IO.setMotors(0, 0)

            # Stop on POI
            elif self.analog[3] > THRESHOLD_LIGHT:
                self.IO.setMotors(0, 0)
                time.sleep(10)

            # turn or reverse when sonor is blocked
            elif self.analog[0] > THRESHOLD_SONAR or self.digital[0] or self.digital[1]:
                self.move()

            # keep going forward otherwise
            else:
                self.IO.setMotors(100,100)

                # if mot[0] != motPrev[0] or mot[1] != motPrev[1]:
                #     speed = self.move(mot[0], mot[1])
                #     self.IO.setMotors(-speed[0], speed[1])
                #     if mot[0]:
                #         self.IO.setStatus('on')
                #     else:
                #         self.IO.setStatus('off')
                #     if mot[1]:
                #         self.IO.setError('on')
                #     else:
                #         self.IO.setError('off')
                # if mot[2]:
                #     self.IO.servoEngage()
                #     # pos=(pos+3)%360
                #     # self.IO.servoSet(abs(pos-180))
                #     self.IO.servoSet(30)
                #     print("Servo Activated...")
                # if mot[2] != motPrev[2] and not mot[2]:
                #     self.IO.servoDisengage()
                # motPrev[0] = mot[0]
                # motPrev[1] = mot[1]
                # motPrev[2] = mot[2]

    # This is a callback that will be called repeatedly.
    # It has its dedicated thread so you can keep block it.
    def Vision(self, OK):
        self.IO.cameraSetResolution('low')
        hasImage = False
        res = 0
        sw = False
        swPrev = False
        while OK():
            if self.digital[4]:
                for i in range(0, 5):
                    self.IO.cameraGrab()
                img = self.IO.cameraRead()
                print("Picture taken...")
                if img.__class__ == numpy.ndarray:
                    hasImage = True
                    cv2.imwrite('camera-' + datetime.datetime.now().isoformat() + '.png', img)
                    self.IO.imshow('window', img)
                    self.IO.setStatus('flash', cnt=2)
                    time.sleep(0.5)
            if hasImage:
                self.IO.imshow('window', img)

            sw = self.digital[5]
            if sw != swPrev and sw:
                res = (res + 1) % 4
                if res == 0:
                    self.IO.cameraSetResolution('low')
                    self.IO.setError('flash', cnt=1)
                if res == 1:
                    self.IO.cameraSetResolution('medium')
                    self.IO.setError('flash', cnt=2)
                if res == 2:
                    self.IO.cameraSetResolution('high')
                    self.IO.setError('flash', cnt=3)
                if res == 3:
                    self.IO.cameraSetResolution('full')
                    self.IO.setError('flash', cnt=4)
                time.sleep(0.5)
            swPrev = sw

            time.sleep(0.05)
