import numpy as np

SATELLITE_X = -0.69
SATELLITE_Y = 0
SATELLITE_Z = 2.95

def find_satellite(x, y, theta):

        # finding required bot rotation
        slope_y = (y - SATELLITE_Y) / (x - SATELLITE_X)
        required_bot_rotation = np.rad2deg(np.arctan(slope_y)) - theta + 180

        # optimize angle
        if abs(required_bot_rotation) > 180:
            if required_bot_rotation > 0: required_bot_rotation -= 360
            else: required_bot_rotation += 360

        # finding required servo angle
        distance_from_satellite = np.sqrt((y - SATELLITE_Y)**2 + (x - SATELLITE_X)**2)
        print("x2", (x - SATELLITE_X)**2)
        print("y2", (y - SATELLITE_Y)**2)
        print("x2+y2", (y - SATELLITE_Y)**2 + (x - SATELLITE_X)**2)
        print("root x2+y2", np.sqrt((y - SATELLITE_Y)**2 + (x - SATELLITE_X)**2))
        print("distance_from_satellite", distance_from_satellite)
        slope_z = SATELLITE_Z / distance_from_satellite
        required_servo_angle = np.rad2deg(np.arctan(slope_z))

        return -required_bot_rotation, required_servo_angle
        
# print(find_satellite(0.5, 2, 90))
print(find_satellite(0.36, 3.22, 270))
# print("169.40847225202862, 48.018699563443406")