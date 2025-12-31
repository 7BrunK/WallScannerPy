import cv2
import numpy as np
import ScannerUtlis as su
import PathUtlis as pu

CAM_FEED = False
IMAGE_FOLDER_PATH = "TestImages"
IMAGE_PATHS = pu.get_files_from_folder(IMAGE_FOLDER_PATH)
COUNT_IMAGES = len(IMAGE_PATHS)

cap = cv2.VideoCapture(0)
cap.set(10, 640)
HEIGHT, WIDTH = 640, 480

index_of_image = 0

while True:
    if CAM_FEED:
        success, frame = cap.read()
    else:
        frame = cv2.imread(IMAGE_PATHS[index_of_image % COUNT_IMAGES])

    frameResized = cv2.resize(frame, (HEIGHT, WIDTH))

    Contours = su.Contours(frameResized)
    Contours.process_frame()
    cv2.imshow("Original", frameResized)
    cv2.imshow("Contours", Contours.draw_contours())

    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    elif key == ord("d"):
        index_of_image += 1
