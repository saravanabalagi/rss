#!/usr/bin/env python
__TODDLER_VERSION__ = "1.0.0"

# Constants
THRESHOLD_SONAR = 29
THRESHOLD_LIGHT = 40
# THRESHOLD_SONAR = 5 # For Debugging only
# THRESHOLD_LIGHT = 40 # For Debugging only
THRESHOLD_IR = 250
THRESHOLD_IR_STANDALONE = 350
POI_COOLDOWN_DISTANCE = 0.50
SERVO_OFFSET = -15
IR_COOLDOWN_TIME = 1
MAX_WAIT_TIME_FOR_CAMERA_FOR_ALIGNMENT = 5

CLOCKWISE_M = 26.92747252747253
CLOCKWISE_B = -4.549450549450569

# DO NOT CHANGE THESE
# TIME_TO_ROTATE_ONE_DEGREE = 0.029
TIME_TO_ROTATE_ONE_DEGREE = 0.04        # for battery voltage 13.11V
REVOLUTIONS_PER_ONE_DEGREE = 0.11
REVOLUTIONS_PER_ONE_CM = 0.10

# Imports
import time
import numpy as np
import cv2
import datetime
from random import randint
from image_operations import get_largest_line_and_image_with_lines_drawn
from alignment_operations import get_degrees_for_bot_alignment_from_line_inclination
from find_satellite import find_satellite

# Hardware test code
class Toddler:
    def __init__(self, IO):
        print 'I am a toddler playing in a sandbox'
        self.IO = IO
        self.digital = [0, 0, 0, 0, 0, 0, 0, 0]
        self.analog = [0, 0, 0, 0, 0, 0, 0, 0]
        self.emergency_stop = False
        self.sonar = [0, 0, 0, 0, 0]

        self.ir_left = [0, 0, 0, 0, 0]
        self.ir_right = [0, 0, 0, 0, 0]
        self.ir_last_detected_at = 0

        # vision
        self.degrees_for_alignment = 999
        self.is_aligned = True
        self.cam_ready = False

        # poi
        self.poi_count = 0
        self.poi_locations = np.zeros((4,2))

        self.x = 0
        self.y = 0
        self.theta = 0

    # This is a callback that will be called repeatedly.
    # It has its dedicated thread so you can keep block it.
    def Control(self, OK):

        # mot = [False, False, False]
        # motPrev = [False, False, False]
        # pos = 180

        forward_revolutions = 0
        cycle = 0
        hall_prev = self.digital[-1]

        while OK():
            # Read once in every 0.05s
            time.sleep(0.05)

            # Read Sensor Data
            self.digital = self.IO.getInputs()
            self.analog = self.IO.getSensors()

            # Print sensor data to console
            print(self.analog, self.digital, [self.x, self.y, self.theta])
            self.sonar = self.sonar[1:] + [self.analog[0]]
            self.ir_left = self.ir_left[1:] + [self.analog[1]]
            self.ir_right = self.ir_right[1:] + [self.analog[2]]

            # # ---------------------------------------------------- # #
            # #  Milestone Part 3, Point to satellite to send data   # #
            # #  Uncomment to make it work                           # #
            # #  Comment Everything else below                       # #
            # # ---------------------------------------------------- # #

            # rotate_bot, rotate_servo = find_satellite(self.x, self.y, self.theta)
            # print(rotate_bot, rotate_servo)
            # self.rotate_bot(rotate_bot)
            # self.rotate_servo(rotate_servo)

            # # ____________________________________________________ # #
            # # ---------------------------------------------------- # #

            # DO NOT UNCOMMENT:
            # FOR DEBUGGING MOTORS ONLY

            # # Run straight for 10 seconds
            # self.rotate_servo(45)
            # time.sleep(5)
            # self.reset_servo()
            # time.sleep(100)
            # self.IO.setMotors(100, -100)
            # time.sleep(7)
            # self.IO.setMotors(0, 0)
            # time.sleep(1000)

            # Check if rotations are right
            # time.sleep(5)
            self.rotate_bot(10)
            time.sleep(1000)
            # self.rotate_bot(-90)
            # time.sleep(1000)
            # self.rotate_bot(45)
            # time.sleep(10)
            # self.rotate_bot(90)
            # time.sleep(10)
            # self.rotate_bot(180)
            # time.sleep(10)
            # self.rotate_bot(360)
            # time.sleep(120)

            # UNCOMMENT ME:

            # Stop on POI and Do not detect POI if already detected
            if not self.is_near_known_poi() and self.analog[3] > THRESHOLD_LIGHT:

                # set POI detected flag and stop motors
                # self.poi_detected_at = time.time()
                print("POI Detected at", self.x, self.y)
                self.poi_count += 1
                self.poi_locations[self.poi_count] = [self.x, self.y]
                self.IO.setMotors(0, 0)
                time.sleep(5)

                # do the math and rotate bot and set servo
                rotate_bot, rotate_servo = find_satellite(self.x, self.y, self.theta)
                print(rotate_bot, rotate_servo)
                self.rotate_bot(rotate_bot)
                self.rotate_servo(rotate_servo)

                # wait for 10 seconds and reset bot orientation and servo
                time.sleep(10)
                self.rotate_bot(-rotate_bot)
                self.reset_servo()
                self.align_bot_using_camera()

            # turn or reverse when sonar is blocked
            elif (self.analog[0] < THRESHOLD_SONAR and abs(self.sonar[-1] - np.mean(self.sonar[:-1])) <= 15) \
                    or self.digital[0] or self.digital[1]:
                print("Sonar activated")
                # self.IO.setMotors(0, 0)
                self.move()

            # check if the bot is getting too close to the walls on both side, when sonar is clear
            elif time.time() - self.ir_last_detected_at > IR_COOLDOWN_TIME and \
                    ((self.analog[1] > THRESHOLD_IR_STANDALONE and np.sum(np.array(self.ir_left[1:]) - np.array(self.ir_left[:-1])) > len(self.ir_left))
                    or (self.analog[2] > THRESHOLD_IR_STANDALONE and np.sum(np.array(self.ir_right[1:]) - np.array(self.ir_right[:-1])) > len(self.ir_right))):
                if self.analog[1] > THRESHOLD_IR_STANDALONE:
                    print("IR Left Activated")
                    self.rotate_bot(30)
                    self.ir_last_detected_at = time.time()
                else:
                    print("IR Right Activated")
                    self.rotate_bot(-30)
                    self.ir_last_detected_at = time.time()

            # keep going forward otherwise
            else:
                # # Debugging code
                # if cycle >= 6:
                #     self.IO.setMotors(0,0)
                #     rotate_bot, rotate_servo = find_satellite(self.x, self.y, self.theta)
                #     print(rotate_bot, rotate_servo)
                #     self.rotate_bot(rotate_bot)
                #     self.rotate_servo(rotate_servo)
                # else:
                    self.IO.setMotors(-100, -100)
                    hall_current = self.digital[-1]
                    if hall_current != hall_prev:
                        hall_prev = hall_current
                        forward_revolutions += 1
            if forward_revolutions >= 5:
                self.x += 13.5 * np.cos(np.radians(self.theta)) / 100
                self.y += 13.5 * np.sin(np.radians(self.theta)) / 100
                forward_revolutions %= 5
                cycle += 1
                print("Cycle:",cycle, "X: ", self.x, "Y: ", self.y)

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
                    self.degrees_for_alignment = get_degrees_for_bot_alignment_from_line_inclination(line.inclination())
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
            # if randint(0, 9) > 5:
            #     self.rotate_bot(-90)
            # else: self.rotate_bot(90)
            self.rotate_bot(-90)

    # rotate bot to specific angle using hall sensor
    def rotate_bot(self, degrees, update_theta=True):

        print("Rotation initiated for", degrees, "degrees")

        # do not rotate if zero
        if degrees == 0: return

        # rotate clockwise if degrees more than 0
        if degrees >= 0:
            self.IO.setMotors(100, -100)
            # time.sleep((TIME_TO_ROTATE_ONE_DEGREE - abs(degrees)/float(360) * 0.015) * abs(degrees))
            time.sleep((degrees - CLOCKWISE_B)/CLOCKWISE_M)

        # rotate counter-clockwise if degrees is less than 0
        else:
            self.IO.setMotors(-100, 100)
            time.sleep((TIME_TO_ROTATE_ONE_DEGREE - abs(degrees)/float(360) * 0.015) * abs(degrees) * 0.8)

        # # sustain rotation
        # revolutions = 0
        # rotation_done = False
        # hall_prev = False
        # while not rotation_done:
        #     hall_current = self.digital[-1]
        #     if hall_current != hall_prev180:
        #         hall_prev = hall_current
        #         revolutions += 1
        #         print(revolutions)
        #
        #     if revolutions >= round(abs(degrees) * REVOLUTIONS_PER_ONE_DEGREE):
        #         rotation_done = True

        # sustain rotation
        # time.sleep((TIME_TO_ROTATE_ONE_DEGREE - abs(degrees)/float(360) * 0.015) * abs(degrees))
        print("Rotation complete for", degrees, "degrees")

        # stop motors
        self.IO.setMotors(0, 0)

        # align bot to nearest 90 if rotated 90 degrees
        if abs(degrees) == 90:
            self.align_bot_using_camera()

        # update current orientation
        if update_theta:
            self.theta -= degrees
            self.theta %= 360

        return

    # rotate servo
    def rotate_servo(self, degrees):

        # lock in position
        self.IO.servoEngage()

        # rotate and send status
        self.IO.servoSet(degrees + SERVO_OFFSET)
        print("\n\nServo Activated")
        print("Setting", degrees, "degrees")
        print("\n")

    # reset servo
    def reset_servo(self):

        # set servo back to zero
        self.IO.servoEngage()
        self.IO.servoSet(0)
        print("\n\nSetting zero degrees")

    def is_near_known_poi(self):
        diff = np.abs(self.poi_locations - [self.x, self.y])
        min_diff = np.min(diff, axis=0)
        if np.max(min_diff) < POI_COOLDOWN_DISTANCE:
            return True
        return False

    def align_bot_using_camera(self, force=True):
        self.is_aligned = False
        start = time.time()
        while self.cam_ready is False:
            time.sleep(0.05)
            if time.time() - start > MAX_WAIT_TIME_FOR_CAMERA_FOR_ALIGNMENT:
                break

        if self.degrees_for_alignment < 45:
            print("Aligning robot")
            print(self.degrees_for_alignment, "to be aligned")
            self.rotate_bot(self.degrees_for_alignment, update_theta=False)
            self.is_aligned = True
            print("Alignment complete")
            self.degrees_for_alignment = 999
            time.sleep(1)

        else:
            if self.degrees_for_alignment == 999:
                # self.rotate_bot(-20, update_theta=False)
                # self.align_bot_using_camera()
                print("No line found")
            else:
                print("\n\n")
                print("Error")
                print("Degrees for alignment", self.degrees_for_alignment)
                print("\n\n")

            self.is_aligned = True
            self.degrees_for_alignment = 999
            print("Skipping alignment")

