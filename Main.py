import cv2
from kivy.uix.togglebutton import ToggleButton
from pygments.styles.dracula import background

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

class ReportLabel(Label):
    def __init__(self, **kwargs):
        super(ReportLabel, self).__init__(**kwargs)
        self.background_color = [1, 1, 0, 1]

    def update(self, saving_is_active: bool):
        self.text = f'Saving is active: {saving_is_active}'

class DrawProcessCheckBox(BoxLayout):
    def __init__(self, owner_app: App, **kwargs):
        super(DrawProcessCheckBox, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.owner_app = owner_app

        self.label = Label(text= 'Draw process - ',
                           font_size=FONT_SIZE_BY_DEFAULT,
                           halign='right',
                           valign='center',
                           size_hint=(1, None),
                           pos_hint={'right': 1.0, 'center_y': 0.5})
        self.checkbox = CheckBox(on_release= self.on_checkbox_release,
                                 size_hint=(1, None),
                                 pos_hint={'center_x': 1.0, 'center_y': 0.5})
        self.add_widget(self.label)
        self.add_widget(self.checkbox)

    def on_checkbox_release(self, checkbox):
        if self.checkbox.active:
            for frame_image in self.owner_app.frame_images_list[1:]:
                self.owner_app.frames_layout.add_widget(frame_image)
        else:
            for frame_image in self.owner_app.frame_images_list[1:]:
                self.owner_app.frames_layout.remove_widget(frame_image)

class ToggleSavingButton(ToggleButton):
    def __init__(self, owner_app: App, **kwargs):
        super(ToggleSavingButton, self).__init__(**kwargs)
        self.owner_app = owner_app
        self.normal_state()

    def on_release(self):
        if self.state == 'down': self.down_state()
        else: self.normal_state()

    def normal_state(self):
        self.background_color = [1, 0, 0, 1]
        self.text = 'SAVING IS\nPAUSED'
        self.owner_app.saving_is_active = False

    def down_state(self):
        self.background_color = [0, 1, 0, 1]
        self.text = 'SAVING IS\nACTIVE'
        self.owner_app.saving_is_active = True

class LastSavedImage(BoxLayout):
    def __init__(self, texture = IMAGE_BY_DEFAULT_PATH, **kwargs):
        super(LastSavedImage, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.image = Image(
            source= texture)
        self.label = Label(
            text=f'Last saved',
            font_size= FONT_SIZE_BY_DEFAULT)

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
    _saving_is_active: bool = False
    def _get_saving_is_active_(self):
        return self._saving_is_active
    def _set_saving_is_active_(self, state):
        self._saving_is_active = state
        self.top_label.update(self._saving_is_active)
    saving_is_active = property(_get_saving_is_active_, _set_saving_is_active_)

    def _update_image_textures(self):
        for frame, index in zip([self.contours_frame, self.main_contour_frame, self.result_frame], range(1, 4)):
            try:
                self.frame_images_list[index].texture = convert_cv2_frame_to_kivy_texture(frame)
            except Exception:
                self.frame_images_list[index].texture = Texture(source= IMAGE_BY_DEFAULT_PATH)

    def init_widgets_and_layouts(self):
        self.main_layout = BoxLayout(orientation='vertical')
        self.top_layout = BoxLayout(orientation='horizontal',
                                    size_hint=(1.0, None),
                                    height=FONT_SIZE_BY_DEFAULT)
        self.bottom_layout = BoxLayout(orientation='horizontal')
        self.frames_layout = GridLayout(cols=2)
        self.right_panel_layout = BoxLayout(orientation='vertical',
                                             size_hint=(0.2, 1.0),
                                             padding=20,
                                             spacing=20)

        self.top_label = ReportLabel(font_size=FONT_SIZE_BY_DEFAULT)

        self.frame_images_list = [KivyCamera(capture=self.capture, fps=20)]  # [0] - camera frame
        for i in range(3): self.frame_images_list.append(Image(source= IMAGE_BY_DEFAULT_PATH, fit_mode= 'fill'))

        self.draw_process_checkbox = DrawProcessCheckBox(owner_app=self)
        self.toggle_saving_button = ToggleSavingButton(owner_app=self, font_size=FONT_SIZE_BY_DEFAULT)
        self.last_saved_image_widget = LastSavedImage()

        self.main_layout.add_widget(self.top_layout)
        self.main_layout.add_widget(self.bottom_layout)
        self.top_layout.add_widget(self.top_label)
        self.bottom_layout.add_widget(self.frames_layout)
        self.bottom_layout.add_widget(self.right_panel_layout)
        self.frames_layout.add_widget(self.frame_images_list[0])
        self.right_panel_layout.add_widget(self.draw_process_checkbox)
        self.right_panel_layout.add_widget(self.toggle_saving_button)
        self.right_panel_layout.add_widget(self.last_saved_image_widget)

    def save_request(self, frame):
        if self.saving_is_active:
            try:
                self.saver.save_image(self.result_frame)
            except Exception as e:
                print('Saving failed with error: ', e)
            else:
                print('Saving is successful')
            self.last_saved_image_widget.texture = convert_cv2_frame_to_kivy_texture(self.result_frame)
            self.previous_frame = self.result_frame
        else:
            print('An attempt was made to save, but saving is paused')

    def update(self, delta):
        success, self.frame = self.capture.read()
        if success:
            try:
                self.contours_frame, self.main_contour_frame, self.result_frame = self.scanner.scan_process_frame(self.frame)
            except su.ContourNotFoundError as e:
                SECOND_TRY_TIMEOUT = 3 # in sec's
                print(e, f'Try again in {SECOND_TRY_TIMEOUT} seconds')
                Clock.schedule_once(self.update, SECOND_TRY_TIMEOUT)
            else:
                if self.previous_frame is None:
                    self.save_request(self.result_frame)
                else:
                    is_similar = self.scanner.is_similar_frames(self.previous_frame, self.result_frame)
                    if is_similar:
                        print('Similar frames')
                    else:
                        self.save_request(self.result_frame)
        self._update_image_textures()

    def build(self):
        UPDATE_TIMEOUT: int = 3 # in sec's

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
        self.saving_is_active = False

        Clock.schedule_interval(self.update, UPDATE_TIMEOUT)
        self.update(delta= 1)

        return self.main_layout

    def on_stop(self):
        self.capture.release()

if __name__ == "__main__":
    ScannerApp().run()