import os
import cv2
from kivy import platform
from kivy.core.image import Image
from kivy.graphics.texture import Texture

def get_files_from_folder(folder_path):
    total_paths = []
    for file_path in os.listdir(folder_path):
        total_file_path = os.path.join(folder_path, file_path)
        total_paths.append(total_file_path)
    return total_paths

def convert_cv2_frame_to_kivy_texture(frame):
    buf1 = cv2.flip(frame, 0)
    #buf = buf1.tostring()
    buf = buf1.tobytes()
    image_texture = Texture.create(
        size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
    image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
    return image_texture

class fake_camera():
    def __init__(self):
        self.IMAGE_FOLDER_PATH: str = "TestImages"
        self.IMAGE_PATHS: list = get_files_from_folder(self.IMAGE_FOLDER_PATH)
        self.COUNT_IMAGES: int = len(self.IMAGE_PATHS)

        self.index_of_test_image = 0
        self.test_image_path = self.IMAGE_PATHS[self.index_of_test_image % self.COUNT_IMAGES]

    def update(self):
        key = cv2.waitKey(1)
        if key == ord("d"):
            self.index_of_test_image += 1
        elif key == ord("a"):
            self.index_of_test_image -= 1

    def read(self):
        test_image_path = self.IMAGE_PATHS[self.index_of_test_image % self.COUNT_IMAGES]
        return cv2.imread(test_image_path)

class Saver:
    image_index = 1
    def __init__(self):
        pass
    def save_image(self, frame):
        pass

class PCSaver(Saver):
    def __init__(self, save_folder_path):
        self.SAVE_FOLDER_PATH = save_folder_path

    def save_image(self, frame):
        cv2.imwrite(f'{self.SAVE_FOLDER_PATH}/{self.image_index}.jpg', frame)
        self.image_index += 1

class AndroidSaver(Saver):
    def __init__(self):
        pass

    def save_image(self, frame):
        try:
            image = Image(convert_cv2_frame_to_kivy_texture(frame))
            image.save(f'/sdcard/DCIM/scanned_{self.image_index}.jpg')
        except Exception as e:
            print(e)
        else:
            self.image_index += 1
