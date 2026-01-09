import cv2

import ScannerUtlis as su
import SaveLoadUtlis as slu
from Scanner import Scanner

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window

Window.size = (2340//2, 1080//2)
IMAGE_BY_DEFAULT_PATH = 'image_not_found.jpg'
FONT_SIZE_BY_DEFAULT = 16

def convert_cv2_frame_to_kivy_texture(frame):
    buf1 = cv2.flip(frame, 0)
    buf = buf1.tostring()
    image_texture = Texture.create(
        size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
    image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
    return image_texture

class LastSavedImage(BoxLayout):
    def __init__(self, texture = IMAGE_BY_DEFAULT_PATH, **kwargs):
        super(LastSavedImage, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.image = Image(source= texture)
        self.label = Label(text=f'Last saved', font_size= FONT_SIZE_BY_DEFAULT)

        self.add_widget(self.image)
        self.add_widget(self.label)

    @property
    def texture(self):
        return self.image.texture

    @texture.setter
    def texture(self, texture):
        self.image.texture = texture

class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.allow_stretch = True
        self.fit_mode = 'fill'
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        success, frame = self.capture.read()
        if success: self.texture = convert_cv2_frame_to_kivy_texture(frame)

class ScannerApp(App):
    def draw_process_toggle(self, checkbox):
        if checkbox.active:
            for frame_image in self.frame_images_list[1:]:
                self.frames_layout.add_widget(frame_image)
        else:
            for frame_image in self.frame_images_list[1:]:
                self.frames_layout.remove_widget(frame_image)

    def on_start_button(self, instance):
        print(f'button {instance} released')

    def _update_image_textures(self):
        for frame, index in zip([self.contours_frame, self.main_contour_frame, self.result_frame], range(1, 4)):
            try:
                self.frame_images_list[index].texture = convert_cv2_frame_to_kivy_texture(frame)
            except Exception:
                self.frame_images_list[index].texture = Texture(source= IMAGE_BY_DEFAULT_PATH)

    def init_widgets_and_layouts(self):
        self.main_layout = BoxLayout(orientation='vertical')
        self.top_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, None), height=50)  # стата всякая
        self.bottom_layout = BoxLayout(orientation='horizontal')  # два следующих
        self.frames_layout = GridLayout(cols=2)  # вид с камеры, контуры и финальная картинка
        self.right_panel_layout = AnchorLayout(anchor_x='center', anchor_y='center',
                                               size_hint=(None, 1.0), width=250)  # центрирование для кнопок и тд
        self.right_center_layout = BoxLayout(orientation='vertical', padding=10)  # кнопки

        self.top_label = Label(text=f'Process: {self.current_process_state}', font_size= FONT_SIZE_BY_DEFAULT)

        self.frame_images_list = [KivyCamera(capture=self.capture, fps=20)]  # [0] - camera frame
        for i in range(3): self.frame_images_list.append(Image(source= IMAGE_BY_DEFAULT_PATH, fit_mode= 'fill'))

        self.draw_process_checkbox = CheckBox(on_release=self.draw_process_toggle)
        self.start_button = Button(text=" START\nSAVING", font_size= FONT_SIZE_BY_DEFAULT, on_release=self.on_start_button)
        self.last_saved_image_widget = LastSavedImage()

        self.main_layout.add_widget(self.top_layout)
        self.main_layout.add_widget(self.bottom_layout)
        self.top_layout.add_widget(self.top_label)
        self.bottom_layout.add_widget(self.frames_layout)
        self.bottom_layout.add_widget(self.right_panel_layout)
        self.frames_layout.add_widget(self.frame_images_list[0])
        self.right_panel_layout.add_widget(self.right_center_layout)
        self.right_center_layout.add_widget(self.draw_process_checkbox)
        self.right_center_layout.add_widget(self.start_button)
        self.right_center_layout.add_widget(self.last_saved_image_widget)

    def update(self, delta):
        print('update called')
        success, self.frame = self.capture.read()
        if success:
            try:
                self.contours_frame, self.main_contour_frame, self.result_frame = self.scanner.scan_process_frame(self.frame)
            except su.ContourNotFoundError as e:
                SECOND_TRY_TIMEOUT = 1 # in sec's
                print(e, f'Try again in {SECOND_TRY_TIMEOUT} seconds')
                Clock.schedule_once(self.update, SECOND_TRY_TIMEOUT)

            try:
                is_similar = self.scanner.is_similar_frames(self.previous_frame, self.result_frame)
                if is_similar:
                    print('Similar frames')
                else:
                    self.saver.save_image(self.result_frame)

                    self.last_saved_image_widget.texture = convert_cv2_frame_to_kivy_texture(self.result_frame)
                    print('Frame saved')
            except Exception as e:
                print(e)

            self.previous_frame = self.result_frame

        self._update_image_textures()

    def build(self):
        UPDATE_TIMEOUT: int = 5 # in sec's
        self.current_process_state = 'Nothing'

        self.capture = cv2.VideoCapture(0)
        self.capture.set(10, 640)
        self.saver = slu.PCSaver("ScannedImages")
        self.scanner = Scanner()
        self.previous_frame = None

        IMAGE_BY_DEFAULT = cv2.imread(IMAGE_BY_DEFAULT_PATH)
        self.contours_frame = IMAGE_BY_DEFAULT
        self.main_contour_frame = IMAGE_BY_DEFAULT
        self.result_frame = IMAGE_BY_DEFAULT

        self.init_widgets_and_layouts()

        Clock.schedule_interval(self.update, UPDATE_TIMEOUT)
        self.update(delta= 1)

        return self.main_layout

    def on_stop(self):
        self.capture.release()

if __name__ == "__main__":
    ScannerApp().run()