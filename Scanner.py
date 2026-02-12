import cv2
import numpy as np
from pyexpat import features

import ScannerUtlis as su
import SaveLoadUtlis as slu

class Scanner:
    def __init__(self, processing_size_w_h: tuple = (640, 480)):
        self.PROCESSING_SIZE = processing_size_w_h

    def scan_process_frame(self, frame):
        Contours = su.Contours(frame, self.PROCESSING_SIZE)
        Contours.preprocess_frame()

        Contours.find_contours() # Может вызвать ContourNotFoundError
        frameContours = Contours.draw_contours(Contours.contours)

        Contours.find_main_contour() # Может вызвать ContourNotFoundError
        frameMainContour = Contours.draw_contours(Contours.main_contour, (0, 255, 0))

        main_resized_corners = Contours.get_corners(Contours.main_contour)
        main_corners = Contours.processing_to_original_convert(main_resized_corners)
        frameWarped = Contours.warp_perspective(main_corners, Contours.frame)
        return frameContours, frameMainContour, frameWarped

    def is_similar_frames(self, previous_frame, current_frame, similarity_threshold=0.094, pixel_treshold=7):
        p_size = previous_frame.shape[:-1][::-1]  # (w, h)
        c_size = current_frame.shape[:-1][::-1]
        max_size = (max(p_size[0], c_size[0]), max(p_size[1], c_size[1]))
        previous_frame = cv2.resize(previous_frame, max_size)
        current_frame = cv2.resize(current_frame, max_size)

        contours1 = su.Contours(previous_frame, self.PROCESSING_SIZE)
        contours2 = su.Contours(current_frame, self.PROCESSING_SIZE)

        max_len = 0
        for contour, index in zip([contours1, contours2], [1, 2]):
            contour.preprocess_frame()
            contour.find_contours()
            contour_len = len(contour.contours)
            max_len = max(max_len, contour_len)
        delta = abs(len(contours1.contours) - len(contours2.contours))

        try:
            delta_ratio = delta / max_len
        except ZeroDivisionError:
            return False
        if delta_ratio > similarity_threshold:
            return False
        diff = cv2.absdiff(previous_frame, current_frame)
        mean_diff = np.mean(diff)
        return mean_diff < pixel_treshold

if __name__ == '__main__':
    CAM_FEED = False

    IMAGE_FOLDER_PATH: str = "TestImages"
    IMAGE_PATHS: list = slu.get_files_from_folder(IMAGE_FOLDER_PATH)
    COUNT_IMAGES: int = len(IMAGE_PATHS)

    SAVE_FOLDER_PATH: str = "ScannedImages"

    cap = cv2.VideoCapture(0)
    cap.set(10, 640)

    saver = slu.PCSaver(SAVE_FOLDER_PATH)
    scanner = Scanner()

    index_of_test_image = 0
    previous_frame = None
    while True:
        if CAM_FEED:
            success, frame = cap.read()
        else:
            test_image_path = IMAGE_PATHS[index_of_test_image % COUNT_IMAGES]
            frame = cv2.imread(test_image_path)

        try:
            fContours, fMainContour, fWarped = scanner.scan_process_frame(frame)
        except su.ContourNotFoundError as e:
            print(e)
            if not CAM_FEED:
                index_of_test_image -= 1
                print('Image skipped')
            continue

        cv2.imshow("Original", frame)
        cv2.imshow("Contours", fContours)
        cv2.imshow("Main Contour", fMainContour)
        cv2.imshow("Warped", fWarped)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break
        if key == ord("s"):
            saver.save_image(fWarped)
        if key == ord("p"):
            previous_frame = fWarped
            print("Previous Frame saved")
        if key == ord("c"):
            is_similar = Scanner.is_similar_frames(previous_frame, fWarped)
            if is_similar: print("Similar frames")
            else: print("Diff")

        if not CAM_FEED:
            if key == ord("d"):
                index_of_test_image += 1
            elif key == ord("a"):
                index_of_test_image -= 1
    cap.release()
    cv2.destroyAllWindows()