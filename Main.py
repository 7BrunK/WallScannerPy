from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget

from kivy.core.camera import Camera
from kivy.core.image import Image
from kivy.uix.image import Image

from kivy.core.window import Window

class ScannerApp(App):
    def on_button_pressed(self, *args):
        print("ScannerApp")

    def build(self):
        pass

if __name__ == "__main__":
    ScannerApp().run()