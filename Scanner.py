import cv2
import numpy as np
import ScannerUtlis as su
import SaveLoadUtlis as slu

## Class Scanner: ##

CAM_FEED = False
IMAGE_FOLDER_PATH = "TestImages"
IMAGE_PATHS = slu.get_files_from_folder(IMAGE_FOLDER_PATH)
COUNT_IMAGES = len(IMAGE_PATHS)

SAVE_FOLDER_PATH = "ScannedImages"
Saver: slu.Saver = slu.PCSaver(SAVE_FOLDER_PATH)

PROCESSING_SIZE: tuple = (640, 480) # (width, height)

cap = cv2.VideoCapture(0)
cap.set(10, 640)

def scan_process_frame(frame):
    Contours = su.Contours(frame, PROCESSING_SIZE)
    Contours.preprocess_frame()

    Contours.find_contours()
    frameContours = Contours.draw_contours(Contours.contours)

    Contours.find_main_contour()
    frameMainContour = Contours.draw_contours(Contours.main_contour, (0, 255, 0))

    main_resized_corners = Contours.get_corners(Contours.main_contour)
    main_corners = Contours.processing_to_original_convert(main_resized_corners)
    frameWarped = Contours.warp_perspective(main_corners, Contours.frame)
    return frameContours, frameMainContour, frameWarped

def save_frame_request(frame):
    Saver.save_image(frame)

## End class Scanner ##


index_of_test_image = 0
while True:
    if CAM_FEED:
        success, frame = cap.read()
    else:
        test_image_path = IMAGE_PATHS[index_of_test_image % COUNT_IMAGES]
        frame = cv2.imread(test_image_path)

    try:
        fContours, fMainContour, fWarped = scan_process_frame(frame)
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
        save_frame_request(fWarped)

    if not CAM_FEED:
        if key == ord("d"):
            index_of_test_image += 1
        elif key == ord("a"):
            index_of_test_image -= 1
cap.release()
cv2.destroyAllWindows()