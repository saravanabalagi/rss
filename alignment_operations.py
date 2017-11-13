import numpy as np

# calculate how much bot needs to turn for the given line
def get_degrees_for_bot_alignment_from_line_inclination(largest_line_inclination):

    # print("Line incl",largest_line_inclination)
    if abs(largest_line_inclination) <= 45: degrees = -1 * np.sign(largest_line_inclination) * abs(largest_line_inclination)
    else: degrees = np.sign(largest_line_inclination) * (90 - abs(largest_line_inclination))
    # print("Result",degrees)
    return degrees

def get_degrees_for_bot_alignment_from_ir_readings(ir_readings):
    ir_readings = np.array(ir_readings)
    diff = ir_readings[1:] - ir_readings[:-1]
    if 0 < diff < 100:
        return 10
    return 0

if __name__ == "__main__":
    print(get_degrees_for_bot_alignment_from_ir_readings([100, 101, 102, 103, 104]))