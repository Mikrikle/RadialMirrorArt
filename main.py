from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Line, SmoothLine
from kivy.core.window import Window
from kivy.properties import ObjectProperty


class Container(FloatLayout):
    
    paint = ObjectProperty()
        
    def clear_canvas(self):
        self.paint.canvas.clear()


class MyPaintWidget(Widget):

    def on_touch_down(self, touch):
        color = (random(), 1, 1)
        with self.canvas:
            Color(*color, mode='hsv')
            touch.ud['userline'] = Line(points=(), width=3, cap='round', joint='round', close=False)
            touch.ud['mirroredline'] = Line(points=(), width=3, cap='round', joint='round', close=False)


    def on_touch_move(self, touch):
        touch.ud['userline'].points += [touch.x, touch.y]
        touch.ud['mirroredline'].points += [Window.size[0] - touch.x, touch.y]



class MyPaintApp(App):

    def build(self):
        return Container()




if __name__ == '__main__':
    MyPaintApp().run()