import numpy as np
import cv2
from line import Line

THRESHOLD_1 = 100
THRESHOLD_2 = 100
GAUSSIAN_KERNEL_SIZE = 11       # needs to be odd
GAUSSIAN_SIGMA = 1

MIN_LINE_LENGTH = 100
MAX_LINE_GAP = 20
NEAR_VERTICAL_ANG_DIFF = 20
SKIP_BOTTOM_THRESHOLD = 20
LINE_THICKNESS = 1
PRIME_LINE_THICKNESS = 5
THRESHOLD_INTERCEPT_FOR_SIMILARITY = 10
THRESHOLD_INCLINATION_FOR_SIMILARITY = 10

# do edge detection
def get_edges(img):
    img = cv2.GaussianBlur(img, (GAUSSIAN_KERNEL_SIZE, GAUSSIAN_KERNEL_SIZE), GAUSSIAN_SIGMA)
    edges = cv2.Canny(img, THRESHOLD_1, THRESHOLD_2)
    return edges

# convert hough lines to custom class Line
def convert_to_lines(lines):
    new_lines = []
    for line in lines:
        if np.array(line[0]).shape[0] == 4:
            valid_line = line[0]
        elif np.array(line[0]).shape[1] == 4:
            valid_line = line[0][0]
        else: valid_line = None
        if valid_line is not None:
            new_lines.append(Line(valid_line))
    return new_lines

# eliminate lines at the bottom
def eliminate_lines(lines):
    new_lines = []
    for line in lines:
        if line.y1 > 400:
            if line.y2 > 400:
                continue
        if abs(line.slope()) > np.tan(np.radians(90-NEAR_VERTICAL_ANG_DIFF)):
            continue
        new_lines.append(line)
    return new_lines

# combine multiple lines detected into 1, if they are all near
def combine_lines(lines):
    duplicate = np.zeros(len(lines))
    duplicate.fill(-1)
    for index, line in enumerate(lines):
        for c_index, c_line in enumerate(lines):
            if c_index == index: continue
            if duplicate[c_index] != -1: continue
            if abs(line.intercept() - c_line.intercept()) < THRESHOLD_INTERCEPT_FOR_SIMILARITY:
                if abs(line.inclination() - c_line.inclination()) < THRESHOLD_INCLINATION_FOR_SIMILARITY:
                    duplicate[index] = index
                    duplicate[c_index] = index
    new_lines = [lines[index] for index, i in enumerate(duplicate) if i == -1]
    for index in set(duplicate):
        if index == -1: continue
        duplicate_lines = [lines[i] for i, x in enumerate(duplicate) if x == index]
        new_lines.append(Line.combine(duplicate_lines))
    return new_lines

# find the prime line
def get_largest_line_and_image_with_lines_drawn(img):

    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    largest_line = Line([0, 0, 0, 0])
    edges = get_edges(img)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, np.array([]), MIN_LINE_LENGTH, MAX_LINE_GAP)

    if lines is None: print("No lines"); return None, img

    lines = convert_to_lines(lines)
    lines = combine_lines(lines)
    lines = eliminate_lines(lines)

    for line in lines:
        cv2.line(img, line.point_1(), line.point_2(), (255, 0, 0), LINE_THICKNESS)
        if line.length() > largest_line.length():
            largest_line = line
    cv2.line(img, largest_line.point_1(), largest_line.point_2(), (0, 0, 255), PRIME_LINE_THICKNESS)
    return largest_line, img
