TIME_TO_ROTATE_ONE_DEGREE = 0.025

def rotate_bot(degrees):

    # do not rotate if zero
    if degrees == 0: return

    # rotate clockwise if degrees more than 0
    if degrees >= 0:
        print("Right Rotation")
        # self.IO.setMotors(-100, 100)

    # rotate counter-clockwise if degrees is less than 0
    else:
        print("Left Rotation")
        # self.IO.setMotors(100, -100)

    # sustain rotation
    # time.sleep((TIME_TO_ROTATE_ONE_DEGREE + degrees/float(360) * 0.05) * abs(degrees))
    print((TIME_TO_ROTATE_ONE_DEGREE + abs(degrees)/float(360) * 0.05) * abs(degrees))
    # self.IO.setMotors(0, 0)

    return

rotate_bot(-90)




