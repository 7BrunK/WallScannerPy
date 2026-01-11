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

class TestApp(App):
    def build(self):
        MAIN = BoxLayout(orientation='vertical')
        button = Button(text='MAIN')
        MAIN.add_widget(button)

        main = BoxLayout(orientation='vertical')
        button1 = Button(text='1')
        button2 = Button(text='2')
        main.add_widget(button1)
        main.add_widget(button2)
        MAIN.add_widget(main)
        return MAIN

if __name__ == "__main__":
    TestApp().run()