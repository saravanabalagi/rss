import numpy as np

SATELLITE_X = -0.69
SATELLITE_Y = 0
SATELLITE_Z = 2.95

HEIGHT_OF_BOT = 0.13

# x and y distance from deployment base
# theta is angle from deployment base, 0 pointing east
def find_satellite(x, y, theta):

        # finding required bot rotation
        slope_y = (y - SATELLITE_Y) / (x - SATELLITE_X)
        required_bot_rotation = np.rad2deg(np.arctan(slope_y)) - theta + 180

        # optimize angle
        if abs(required_bot_rotation) > 180:
            if required_bot_rotation > 0:
                required_bot_rotation -= 360
            else:
                required_bot_rotation += 360

        # finding required servo angle
        distance_from_satellite = np.sqrt(((y - SATELLITE_Y) ** 2) + ((x - SATELLITE_X) ** 2))
        slope_z = (SATELLITE_Z - HEIGHT_OF_BOT) / distance_from_satellite
        required_servo_angle = np.rad2deg(np.arctan(slope_z))

        return -required_bot_rotation, required_servo_angle

if __name__ == "__main__":
    # print(find_satellite(0,0,0))
    print(find_satellite(0.36, 3.22, 270))
