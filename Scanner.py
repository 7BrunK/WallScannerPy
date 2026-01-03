import cv2
import numpy as np
import ScannerUtlis as su
import SaveLoadUtlis as slu

class Scanner:
    def __init__(self, saver: slu.Saver, processing_size_w_h: tuple = (640, 480)):
        self.SAVER = saver
        self.PROCESSING_SIZE = processing_size_w_h

    def scan_process_frame(self, frame):
        Contours = su.Contours(frame, self.PROCESSING_SIZE)
        Contours.preprocess_frame()

        Contours.find_contours()
        frameContours = Contours.draw_contours(Contours.contours)

        Contours.find_main_contour()
        frameMainContour = Contours.draw_contours(Contours.main_contour, (0, 255, 0))

        main_resized_corners = Contours.get_corners(Contours.main_contour)
        main_corners = Contours.processing_to_original_convert(main_resized_corners)
        frameWarped = Contours.warp_perspective(main_corners, Contours.frame)
        return frameContours, frameMainContour, frameWarped

    def save_frame_request(self, frame):
        self.SAVER.save_image(frame)

CAM_FEED = False

IMAGE_FOLDER_PATH: str = "TestImages"
IMAGE_PATHS: list = slu.get_files_from_folder(IMAGE_FOLDER_PATH)
COUNT_IMAGES: int = len(IMAGE_PATHS)

SAVE_FOLDER_PATH: str = "ScannedImages"

cap = cv2.VideoCapture(0)
cap.set(10, 640)

Saver = slu.PCSaver(SAVE_FOLDER_PATH)
Scanner = Scanner(Saver)

index_of_test_image = 0
while True:
    if CAM_FEED:
        success, frame = cap.read()
    else:
        test_image_path = IMAGE_PATHS[index_of_test_image % COUNT_IMAGES]
        frame = cv2.imread(test_image_path)

    try:
        fContours, fMainContour, fWarped = Scanner.scan_process_frame(frame)
    except su.ContourNotFoundError as e:
        print(f'{e} on image {test_image_path}')
        if not CAM_FEED:
            index_of_test_image += 1
            print('Image skipped')
        continue

    cv2.imshow("Original", frame)
    cv2.imshow("Contours", fContours)
    cv2.imshow("Main Contour", fMainContour)
    cv2.imshow("Warped", fWarped)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    elif key == ord("s"):
        Scanner.save_frame_request(fWarped)

    if not CAM_FEED:
        if key == ord("d"):
            index_of_test_image += 1
        elif key == ord("a"):
            index_of_test_image -= 1
cap.release()
cv2.destroyAllWindows()