import cv2

import ScannerUtlis as su
import SaveLoadUtlis as slu
from Scanner import Scanner

from typing import Callable
from kivy import platform
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.core.window import Window

#from pythonforandroid.recipes.android.src.android import permissions

Window.size = (2340//2, 1080//2)
IMAGE_BY_DEFAULT_PATH = 'image_not_found.jpg'
FONT_SIZE_BY_DEFAULT = 16

class BooleanObject(object):
    def __init__(self, state: bool, on_changed_callback: Callable = None):
        super(BooleanObject, self).__init__()
        self._state: bool = state
        self._callback = on_changed_callback

    def _get_state_(self):
        return self._state
    def _set_state_(self, state: bool):
        self._state = state
        if self._callback != None: self._callback(self._state)
    state = property(_get_state_, _set_state_)

class ReportLabel(Label):
    def __init__(self, **kwargs):
        super(ReportLabel, self).__init__(**kwargs)
        self.background_color = [1, 1, 0, 1]

    def update(self, saving_is_active: bool):
        self.text = f'Saving is active: {saving_is_active}'

class ColoredToggleButton(ToggleButton):
    ## Функции определяются в наследниках
    _on_down_action: Callable
    _on_normal_action: Callable

    def __init__(self, down_text = 'Enabled', normal_text = 'Disabled', **kwargs):
        super(ColoredToggleButton, self).__init__(**kwargs)
        self.down_color = [0, 1, 0, 1]
        self.normal_color = [1, 0, 0, 1]
        self.down_text = down_text
        self.normal_text = normal_text

        self.on_release()

    def on_release(self):
        if self.state == 'down':
            self.background_color = self.down_color
            self.text = self.down_text
            self._on_down_action()
        else:
            self.background_color = self.normal_color
            self.text = self.normal_text
            self._on_normal_action()

class ToggleDisplayProcessButton(ColoredToggleButton):
    def __init__(self, frame_images: list, frames_layout, **kwargs):
        self.frame_images = frame_images
        self.frames_layout = frames_layout
        super(ToggleDisplayProcessButton, self).__init__(down_text = 'DRAW PROCESS\nIS ENABLED',
                                                         normal_text = 'DRAW PROCESS\nIS DISABLED', **kwargs)
    def _on_down_action(self):
        for frame_image in self.frame_images[1:]:
            self.frames_layout.add_widget(frame_image)
    def _on_normal_action(self):
        for frame_image in self.frame_images[1:]:
            self.frames_layout.remove_widget(frame_image)

class ToggleSavingButton(ColoredToggleButton):
    def __init__(self, saving_is_active: BooleanObject, **kwargs):
        self.saving_is_active = saving_is_active
        super(ToggleSavingButton, self).__init__(down_text = 'SAVING IS\nACTIVE',
                                                 normal_text = 'SAVING IS\nPAUSED', **kwargs)
    def _on_down_action(self): self.saving_is_active.state = True
    def _on_normal_action(self): self.saving_is_active.state = False

class LastSavedImage(BoxLayout):
    def __init__(self, start_texture = IMAGE_BY_DEFAULT_PATH, **kwargs):
        super(LastSavedImage, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.image = Image(
            source= start_texture,
            fit_mode= 'scale-down',
            size_hint= (1.0, None),
            pos_hint= {'top': 1.0, 'center_x': 0.5})
        self.label = Label(
            text=f'Last saved',
            font_size= FONT_SIZE_BY_DEFAULT,
            text_size= self.size,
            valign= 'top',
            halign= 'center',
            size_hint= (None, None),
            pos_hint= {'top': 0.0, 'center_x': 0.5})
        self.add_widget(self.image)
        self.add_widget(self.label)

    ## LastSavedImage не является наследником класса Image, но содержит экземпляр Image,
    ## это мостик, чтобы обращаться напрямую к свойству texture дочернего Image объекта
    @property
    def texture(self):
        return self.image.texture
    @texture.setter
    def texture(self, texture):
        self.image.texture = texture

# class InterfaceManager(BoxLayout):
#     def __init__(self, **kwargs):
#         super(InterfaceManager, self).__init__(**kwargs)
#         self.interfaces = {}
#
# class Interface(BoxLayout):
#     def __init__(self, **kwargs):
#         super(Interface, self).__init__(**kwargs)
#
#     def on_enter(self):
#         pass
#
#     def on_exit(self):
#         pass

class ScannerApp(App):
    def _update_image_textures(self):
        for frame, index in zip([self.contours_frame, self.main_contour_frame, self.result_frame], range(1, 4)):
            try:
                self.frame_images_list[index].texture = slu.convert_cv2_frame_to_kivy_texture(frame)
            except Exception:
                self.frame_images_list[index].texture = Texture(source= IMAGE_BY_DEFAULT_PATH)

    def init_widgets_and_layouts(self):
        self.vbox_layout = BoxLayout(orientation='vertical')
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

        self.camera = Camera(play= True)
        self.frame_images_list = [self.camera]  # [0] - camera frame
        for i in range(3): self.frame_images_list.append(Image(source= IMAGE_BY_DEFAULT_PATH, fit_mode= 'fill'))

        self.toggle_display_process_button = ToggleDisplayProcessButton(frame_images=self.frame_images_list,
                                                                        frames_layout=self.frames_layout,
                                                                        font_size=FONT_SIZE_BY_DEFAULT)
        self.toggle_saving_button = ToggleSavingButton(saving_is_active=self.saving_is_active,
                                                       font_size=FONT_SIZE_BY_DEFAULT)
        self.last_saved_image_widget = LastSavedImage(pos_hint= {'center_x': 0.5, 'bottom': 0.0})

        self.vbox_layout.add_widget(self.top_layout)
        self.vbox_layout.add_widget(self.bottom_layout)
        self.top_layout.add_widget(self.top_label)
        self.bottom_layout.add_widget(self.frames_layout)
        self.bottom_layout.add_widget(self.right_panel_layout)
        self.frames_layout.add_widget(self.frame_images_list[0])
        self.right_panel_layout.add_widget(self.toggle_display_process_button)
        self.right_panel_layout.add_widget(self.toggle_saving_button)
        self.right_panel_layout.add_widget(self.last_saved_image_widget)

    def _save_request(self, frame):
        if self.saving_is_active.state:
            try:
                self.saver.save_image(self.result_frame)
            except Exception as e:
                print('Saving failed with error: ', e)
            else:
                print('Saving is successful')
            self.last_saved_image_widget.texture = slu.convert_cv2_frame_to_kivy_texture(self.result_frame)
            self.previous_frame = self.result_frame
        else:
            print('An attempt was made to save, but saving is paused')

    second_try_to_find_contours = None
    def update(self, delta):
        if not self.camera.texture:
            print('Camera image is not available')
            return

        self.frame = slu.convert_kivy_texture_to_cv2_frame(self.camera.texture)

        try:
            (self.contours_frame,
             self.main_contour_frame,
             self.result_frame) = self.scanner.scan_process_frame(self.frame)
        except su.ContourNotFoundError as e:
            SECOND_TRY_TIMEOUT: int = 3 # in sec's
            print(e, f'Try again in {SECOND_TRY_TIMEOUT} seconds, delta {round(delta)} seconds')
            if self.second_try_to_find_contours == None:
                self.second_try_to_find_contours = Clock.schedule_once(self.update, SECOND_TRY_TIMEOUT)
            else: self.second_try_to_find_contours()
        else:
            if self.previous_frame is None:
                self._save_request(self.result_frame)
            else:
                is_similar = self.scanner.is_similar_frames(self.previous_frame, self.result_frame)
                if is_similar:
                    print('Similar frames')
                else:
                    self._save_request(self.result_frame)
        self._update_image_textures()

    # def on_start(self): # Вызывается после build()
    #     if permissions.check_permission('camera') != 'granted':
    #         permissions.request_permission('camera')
    #     if permissions.check_permission('write_external_storage') != 'granted':
    #         permissions.request_permission('write_external_storage')

    def build(self): # Вызывается в САМОМ НАЧАЛЕ
        if platform == "win":
            self.saver = slu.PCSaver("ScannedImages")
        else:
            self.saver = slu.AndroidSaver()
        self.scanner = Scanner()
        self.previous_frame = None

        IMAGE_BY_DEFAULT = cv2.imread(IMAGE_BY_DEFAULT_PATH)
        self.contours_frame = IMAGE_BY_DEFAULT
        self.main_contour_frame = IMAGE_BY_DEFAULT
        self.result_frame = IMAGE_BY_DEFAULT
        self.saving_is_active = BooleanObject(state=False)

        self.init_widgets_and_layouts()
        self.saving_is_active._callback = self.top_label.update

        UPDATE_TIMEOUT: int = 5  # in sec's
        Clock.schedule_interval(self.update, UPDATE_TIMEOUT)
        self.update(delta= 1)

        return self.vbox_layout

if __name__ == "__main__":
    ScannerApp().run()