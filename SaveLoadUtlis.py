import os
import cv2

def get_files_from_folder(folder_path):
    total_paths = []
    for file_path in os.listdir(folder_path):
        total_file_path = os.path.join(folder_path, file_path)
        total_paths.append(total_file_path)
    return total_paths

class Saver:
    image_index = 1
    def __init__(self):
        pass
    def save_image(self, image):
        pass

class PCSaver(Saver):
    def __init__(self, save_folder_path):
        self.SAVE_FOLDER_PATH = save_folder_path

    def save_image(self, image):
        cv2.imwrite(f'{self.SAVE_FOLDER_PATH}/{self.image_index}.jpg', image)
        self.image_index += 1