import kivy
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from main import BooleanObject

def smt(state):
    print(state)

saving = BooleanObject(state=False, on_changed_callback=smt)
print(saving.state)
saving.state = True
saving.state = False