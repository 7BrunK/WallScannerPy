import cv2
import numpy as np

class Contours:
    frame = None

    KSIZE = None
    LOW_THRESHOLD = None
    HIGH_THRESHOLD = None

    frameGray = None
    frameBlur = None
    frameCanny = None

    def __init__(self, frame, KSIZE = (3, 3), LOW_THRESHOLD = 10, HIGH_THRESHOLD = 70):
        self.frame = frame
        self.KSIZE = KSIZE
        self.LOW_THRESHOLD = LOW_THRESHOLD
        self.HIGH_THRESHOLD = HIGH_THRESHOLD

    def process_frame(self):
        self.frameGray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.frameBlur = cv2.GaussianBlur(self.frameGray, self.KSIZE, 1)
        self.frameCanny = cv2.Canny(self.frameBlur, self.LOW_THRESHOLD, self.HIGH_THRESHOLD)

    def get_contours(self):
        contours, hierarchy = cv2.findContours(self.frameCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours

    def draw_contours(self):
        frameContours = self.frame.copy()
        contours = self.get_contours()
        cv2.drawContours(frameContours, contours, -1, color = (255, 0, 0), thickness = 5)
        return frameContours

    def rect_contour(self):
        contours = self.get_contours()
