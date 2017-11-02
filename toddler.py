#!/usr/bin/env python
__TODDLER_VERSION__ = "1.0.0"

# Constants
THRESHOLD_SONAR = 29
THRESHOLD_LIGHT = 40
THRESHOLD_IR = 275
THRESHOLD_IR_STANDALONE = 425

CURRENT_BOT_X = 0.36
CURRENT_BOT_Y = 3.32
CURRENT_BOT_THETA = 270

# DO NOT CHANGE THESE
# TIME_TO_ROTATE_ONE_DEGREE = 0.029
TIME_TO_ROTATE_ONE_DEGREE = 0.04
REVOLUTIONS_PER_ONE_DEGREE = 0.5

# Imports
import time
import numpy as np
import cv2
import datetime
from random import randint
from image_operations import get_largest_line_and_image_with_lines_drawn, get_degrees_for_bot_alignment
from find_satellite import find_satellite

# Hardware test code
class Toddler:
    def __init__(self, IO):
        print 'I am a toddler playing in a sandbox'
        self.IO = IO
        self.digital = [0, 0, 0, 0, 0, 0, 0, 0]
        self.analog = [0, 0, 0, 0, 0, 0, 0, 0]
        self.emergency_stop = False
        self.degrees_for_alignment = 999
        self.is_aligned = False
        self.cam_ready = False

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

            # # ---------------------------------------------------- # #
            # #  Milestone Part 3, Point to satellite to send data   # #
            # #  Uncomment to make it work                           # #
            # #  Comment Everything else below                       # #
            # # ---------------------------------------------------- # #

            rotate_bot, rotate_servo = find_satellite(CURRENT_BOT_X, CURRENT_BOT_Y, CURRENT_BOT_THETA)
            print(rotate_bot, rotate_servo)
            self.rotate_bot(rotate_bot)
            self.rotate_servo(rotate_servo)

            # # ____________________________________________________ # #
            # # ---------------------------------------------------- # #

            # DO NOT UNCOMMENT:
            # FOR DEBUGGING MOTORS ONLY

            # # Run straight for 10 seconds
            # self.IO.setMotors(-100, -100)
            # time.sleep(10)
            # self.IO.setMotors(0, 0)
            # time.sleep(5)

            # Check if rotations are right
            self.rotate_bot(20)
            time.sleep(5)
            self.rotate_bot(45)
            time.sleep(5)
            self.rotate_bot(90)
            time.sleep(5)
            self.rotate_bot(180)
            time.sleep(5)
            self.rotate_bot(360)
            time.sleep(120)

            # UNCOMMENT ME:

            # # Emergency stop on mot
            # if self.digital[6]:
            #     print("Emergency Pressed: ", True)
            #     self.emergency_stop = not self.emergency_stop
            # if self.emergency_stop:
            #     print("Emergency Stop: ", True)
            #     self.IO.setMotors(0, 0)
            # if not self.emergency_stop:g
            #     if self.cam_ready and not self.is_aligned:
            #         if self.degrees_for_alignment == 999:
            #             print("Didn't find any line, rotating bot...")
            #             self.rotate_bot(45)
            #         else:
            #             print("Aligning robot")
            #             print(self.degrees_for_alignment, "to be aligned")
            #             self.rotate_bot(self.degrees_for_alignment)
            #             self.is_aligned = # pTrue
            #             print("Alignment complete")
            #             time.sleep(5)
            #             self.degrees_for_alignment = 999
            #
            #     if self.is_aligned:
            #         # Stop on POI
            #         if self.analog[3] > THRESHOLD_LIGHT:
            #             self.IO.setMotors(0, 0)
            #
            #         # turn or reverse when sonar is blocked
            #         elif self.analog[0] < THRESHOLD_SONAR or self.digital[0] or self.digital[1]:
            #             # self.IO.setMotors(0, 0)
            #             self.move()
            #
            #         # check if the bot is getting too close to the walls on both side, when sonar is clear
            #         elif self.analog[1] > THRESHOLD_IR_STANDALONE or self.analog[2] > THRESHOLD_IR_STANDALONE:
            #             if self.analog[1] > THRESHOLD_IR_STANDALONE:
            #                 self.rotate_bot(15)
            #             else:
            #                 self.rotate_bot(-15)
            #
            #         # keep going forward otherwise
            #         else:
            #             self.IO.setMotors(-100, -100)

    # This is a callback that will be called repeatedly.
    # It has its dedicated thread so you can keep block it.
    def Vision(self, OK):

        # 800 x 600 resolution
        self.IO.cameraSetResolution('high')

        hasImage = False
        res = 0
        sw = False
        swPrev = False
        while OK():
            if self.degrees_for_alignment == 999 and self.is_aligned is False:

                self.cam_ready = False
                # for i in range(0, 5):
                self.IO.cameraGrab()
                temp_img = self.IO.cameraRead()
                temp_img = cv2.cvtColor(temp_img, cv2.COLOR_RGB2GRAY)
                line, img = get_largest_line_and_image_with_lines_drawn(temp_img)

                if line is None:
                    print("No line found")
                    self.degrees_for_alignment = 999
                else:
                    self.degrees_for_alignment = get_degrees_for_bot_alignment(line.inclination())
                    print("Line found", self.degrees_for_alignment)
                self.cam_ready = True

                print("Picture taken...")

                if img.__class__ == np.ndarray:
                    hasImage = True
                    cv2.imwrite('cam/camera-' + datetime.datetime.now().isoformat() + '.png', img)
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

    # Move where space is available
    def move(self):

        # get both ir values
        ir_left = self.analog[1]
        ir_right = self.analog[2]

        # find if blocked or not
        l = ir_left > THRESHOLD_IR
        r = ir_right > THRESHOLD_IR

        # if both left and right are blocked
        if l and r:
            self.IO.setMotors(100, 100)
            time.sleep(0.75)

        # if right is free but left is blocked
        if l and not r:
            self.rotate_bot(90)

        # if left is free but right is blocked
        if not l and r:
            self.rotate_bot(-90)

        # if both left and right are available
        if not l and not r:
            if randint(0, 9) > 5:
                self.rotate_bot(-90)
            else: self.rotate_bot(90)

    # rotate bot to specific angle
    # 38.5 degrees observed per second ~= 0.026s per degree
    def rotate_bot(self, degrees):

        print("Rotation initiated for", degrees, "degrees")

        # do not rotate if zero
        if degrees == 0: return

        # rotate clockwise if degrees more than 0
        if degrees >= 0:
            self.IO.setMotors(-100, 100)

        # rotate counter-clockwise if degrees is less than 0
        else:
            self.IO.setMotors(100, -100)

        # sustain rotation
        revolutions = 0
        rotation_done = False
        hall_prev = False
        while not rotation_done:
            hall_current = self.digital[-1]
            if hall_current != hall_prev:
                hall_prev = hall_current
                revolutions += 1
                print(revolutions)

            if degrees * REVOLUTIONS_PER_ONE_DEGREE < revolutions:
                rotation_done = True

        print("Rotation complete for", degrees, "degrees")
        # time.sleep((TIME_TO_ROTATE_ONE_DEGREE - abs(degrees)/float(360) * 0.015) * abs(degrees))
        self.IO.setMotors(0, 0)

        return

    # rotate servo
    def rotate_servo(self, degrees):

        # lock in position
        self.IO.servoEngage()

        # rotate and send status
        self.IO.servoSet(degrees - 5)
        print("Servo Activated... Setting", degrees, "degrees")

        # sustain
        time.sleep(60)

