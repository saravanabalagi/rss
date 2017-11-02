import numpy as np

ONE_REV = 0.35

def find_hall_sensor_revs(bool_list):
    bool_list = np.array(bool_list)
    print(np.sum(bool_list))

find_hall_sensor_revs([True, True, False, False, True, False, False])
