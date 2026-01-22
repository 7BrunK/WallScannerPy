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
from kivy import platform
from main import KivyCamera
import cv2

class TestApp(App):
    def build(self):
        MAIN = BoxLayout(orientation='vertical')
        camera = KivyCamera(capture= cv2.VideoCapture(0), fps=20)
        MAIN.add_widget(camera)
        return MAIN

if __name__ == "__main__":
    TestApp().run()