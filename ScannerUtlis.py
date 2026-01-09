import math

import cv2
import numpy as np

class ContourNotFoundError(Exception):
    def __init__(self, value):
        self.value = value

class Contours:
    frame = None
    contours = None
    main_contour = None
    features = None

    PROCESSING_SIZE: tuple # (width, height)
    ORIGINAL_TO_PROCESSING_SIZE_RATIO: np.ndarray

    KSIZE = None
    LOW_THRESHOLD = None
    HIGH_THRESHOLD = None

    frame_resized = None
    frame_gray = None
    frame_blur = None
    frame_canny = None

    def __init__(self, frame, processing_size = (640, 480), ksize = (3, 3), low_threshold = 10, high_threshold = 120):
        self.frame = frame
        self.PROCESSING_SIZE = processing_size
        self.KSIZE = ksize
        self.LOW_THRESHOLD = low_threshold
        self.HIGH_THRESHOLD = high_threshold

    def preprocess_frame(self):
        original_size = self.frame.shape[:2][::-1]
        self.ORIGINAL_TO_PROCESSING_SIZE_RATIO = np.asarray([original_size[i] / self.PROCESSING_SIZE[i] for i in range(2)], dtype = np.float32)
        self.frame_resized = cv2.resize(self.frame, self.PROCESSING_SIZE)
        self.frame_gray = cv2.cvtColor(self.frame_resized, cv2.COLOR_BGR2GRAY)
        self.frame_blur = cv2.GaussianBlur(self.frame_gray, self.KSIZE, 1)
        self.frame_canny = cv2.Canny(self.frame_blur, self.LOW_THRESHOLD, self.HIGH_THRESHOLD)

    def find_contours(self, retr = cv2.RETR_LIST, approx = cv2.CHAIN_APPROX_SIMPLE):
        self.contours, hierarchy = cv2.findContours(self.frame_canny, retr, approx)
        if type(self.contours) == type(None):
            raise ContourNotFoundError("No contours found")
        return self.contours

    def find_main_contour(self, min_threshold_area = 1000):
        max_founded_area = 0
        for contour in self.contours:
            area = cv2.contourArea(contour)
            if area > min_threshold_area:
                corners = self.get_corners(contour)
                if len(corners) == 4 and area > max_founded_area:
                    self.main_contour = contour # Фиксируем только наибольший 4-ник
                    max_founded_area = area

        if type(self.main_contour) == type(None):
            raise ContourNotFoundError("No main contour found")
        return self.main_contour

    def draw_contours(self, contours, color = (255, 0, 0), thickness = 3):
        frameContours = self.frame_resized.copy()
        cv2.drawContours(frameContours, contours, -1, color, thickness = thickness)
        return frameContours

    def get_corners(self, contour):
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        return approx

    def reorder_corners(self, corners):
        corners = corners.reshape((4, 2))
        ordered_corners = np.zeros((4, 2), np.int32)
        add_vec = corners.sum(axis = 1)
        ordered_corners[0] = corners[np.argmin(add_vec)]
        ordered_corners[3] = corners[np.argmax(add_vec)]
        diff_vec = np.diff(corners, axis = 1)
        ordered_corners[1] = corners[np.argmin(diff_vec)]
        ordered_corners[2] = corners[np.argmax(diff_vec)]
        return ordered_corners

    def calc_width_height_output(self, ordered_corners):
        (top_left, top_right, bottom_left, bottom_right) = ordered_corners
        bottom_width = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) + ((bottom_right[1] - bottom_left[1]) ** 2))
        top_width = np.sqrt(((top_right[0] - top_left[0]) ** 2) + ((top_right[1] - top_left[1]) ** 2))
        right_height = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) + ((top_right[1] - bottom_right[1]) ** 2))
        left_height = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) + ((top_left[1] - bottom_left[1]) ** 2))

        max_width = max(int(bottom_width), int(top_width))
        max_height = max(int(right_height), int(left_height))
        return max_width, max_height

    def warp_perspective(self, corners, frame):
        original = np.float32(self.reorder_corners(corners))
        output_width, output_height = self.calc_width_height_output(original)
        rectangular = np.float32([[0, 0], [output_width, 0], [0, output_height], [output_width, output_height]])
        matrix_T = cv2.getPerspectiveTransform(original, rectangular)
        warped = cv2.warpPerspective(frame, matrix_T, (output_width, output_height))
        return warped

    def processing_to_original_convert(self, point: np.ndarray):
        return np.int32(point * self.ORIGINAL_TO_PROCESSING_SIZE_RATIO)