from kivy.app import App
from kivy.uix.widget import Widget


class PaintWidget(Widget):
    pass


class MyPaintApp(App):
    def build(self):
        return PaintWidget()


if __name__ == '__main__':
    MyPaintApp().run()