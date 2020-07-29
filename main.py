from random import random
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivymd.uix.button import MDRectangleFlatButton
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line, InstructionGroup
from kivy.core.window import Window
from kivy.properties import ObjectProperty, NumericProperty
from kivymd.app import MDApp
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.colorpicker import ColorPicker
from kivymd.uix.button import MDRoundFlatButton, MDIconButton
from kivymd.uix.slider import MDSlider
from kivy.clock import Clock
import math
Window.size = (540,960)


def set_bg(dt=None, bg=(0,0,0,1)):
    '''make canvas black'''
    Window.clearcolor = bg
Clock.schedule_once(set_bg, 1)


class MyPopup(Popup):
    pass


class CustomDropDownDrawingMode(DropDown):
    pass


class CustomDropDownNumberOfLines(DropDown):
    VALUE = NumericProperty()
    def __init__(self, value, paint, **kwargs):
        super().__init__(**kwargs)
        self.VALUE = value
        self.paint = paint
    
    def slider_setattr(self, value):
        self.paint.set_number_of_lines(value)


class CustomDropDownLineWidth(DropDown):
    VALUE = NumericProperty()
    def __init__(self, value, paint, **kwargs):
        super().__init__(**kwargs)
        self.VALUE = value
        self.paint = paint
    
    def slider_setattr(self, value):
        self.paint.set_line_width(value)


class Container(FloatLayout):
    pass


class MyPaintWidget(Widget):
    drawing_mode_select_btn = ObjectProperty()
    down_current_color_label = ObjectProperty()
    down_current_line_width = ObjectProperty()
    down_current_nums_of_lines = ObjectProperty()
    down_current_icon = ObjectProperty()
    undolist = [] # list of cancelled lines
    lineslist = [] # list of drawing lines
    drawing = False
    
    DRAWING_MODE = 'radian'
    NUMBER_OF_LINES = 10
    LINE_WIDTH = 2
    COLOR = (1,0,0,1)
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint=None,None
        self.create_color_popup()
        self.create_settings_popup()
        self.create_number_of_lines_dropdown()
        self.create_drawing_mode_dropdown()
        self.create_lines_width_dropdown()


    #-----------------------#
    #-Settings Popup window-#
    #-----------------------#
    
    def create_settings_popup(self):
        '''Creating a drawing settings window'''
        bxl = BoxLayout()
        self.settings_popup = Popup()
        bxl.add_widget(MDRectangleFlatButton(text="Close", size_hint=(1,.5), on_release=lambda btn: self.settings_popup.dismiss()))
        self.settings_popup.add_widget(bxl)


    def open_settings_popup(self):
        '''open popup window'''
        self.settings_popup.open()


    #---------------------#
    #------DropDowns------#
    #---------------------#

    def create_drawing_mode_dropdown(self):
        '''creating a menu for switching drawing modes'''
        self.dropdown_drawing_mode = CustomDropDownDrawingMode()
        self.dropdown_drawing_mode.bind(on_select=lambda instance, x: self.drawing_mode_custom_setattr(x[0], x[1]))
        
    def create_number_of_lines_dropdown(self):
        self.number_of_lines_dropdown = CustomDropDownNumberOfLines(self.NUMBER_OF_LINES, self)
    
    def create_lines_width_dropdown(self):
        self.line_width_dropdown = CustomDropDownLineWidth(self.LINE_WIDTH, self)
    
    # set down values
    def set_line_width(self, value):
        self.LINE_WIDTH = value
        self.down_current_line_width.text = f'Width\n{value}'

    def set_number_of_lines(self, value):
        self.NUMBER_OF_LINES = value
        self.down_current_nums_of_lines.text = f'Lines\n{value}'

    def drawing_mode_custom_setattr(self, mode, icon):
        '''setting the current drawing mode and icon'''
        setattr(self.down_current_icon, 'icon', icon)
        self.DRAWING_MODE = mode


    #--------------------#
    #-Color Popup window-#
    #--------------------#
    def create_color_popup(self):
        self.color_popup = MyPopup()
        self.color_popup.title = 'Colors'
        bxl = BoxLayout(orientation='vertical', padding=25)
        clr_picker = ColorPicker(color=self.COLOR)
        clr_picker.bind(color=self.on_color)
        bxl.add_widget(clr_picker)
        bxl.add_widget(MDRectangleFlatButton(text="Close", size_hint=(1,.1), on_release=lambda btn: self.color_popup.dismiss()))
        self.color_popup.add_widget(bxl)
    
    def open_color_popup(self):
        self.color_popup.open()
    
    def on_color(self, instance, value):
        self.COLOR = value
        self.down_current_color_label.canvas.children[3] = Color(*value)


    #-------------------#
    #-DRAWING FUNCTIONS-#
    #-------------------#
    def on_touch_up(self, touch):
        '''disabling drawing'''
        self.drawing = False
    
    def on_touch_move(self, touch):
        '''drawing'''
        
        def vector_length(coords, center):
            return math.sqrt((coords[0]-center[0])**2 + (coords[1]-center[1])**2)
        
        if self.drawing:
            # Continue drawing line
            if self.DRAWING_MODE == 'simple':
                self.obj.children[-1].points += touch.pos
            elif self.DRAWING_MODE == 'symmetric':
                self.obj.children[-1].points += touch.pos
                self.obj.children[-3].points += (Window.size[0] - touch.pos[0], touch.pos[1])
            elif self.DRAWING_MODE == 'square':
                self.obj.children[-1].points += touch.pos
                self.obj.children[-3].points += (touch.pos[0], Window.size[1] - touch.pos[1])
                self.obj.children[-5].points += (Window.size[0] - touch.pos[0], touch.pos[1])
                self.obj.children[-7].points += (Window.size[0] - touch.pos[0], Window.size[1] - touch.pos[1])
            elif self.DRAWING_MODE == 'radian' or  self.DRAWING_MODE == 'radian-symmetric':
                center = (Window.size[0]//2, Window.size[1]//2)
                dx = touch.pos[0] - center[0]
                dy = touch.pos[1] - center[1]
                if dx != 0:
                    vector = vector_length(touch.pos, center)
                    angle = 360/self.NUMBER_OF_LINES
                    alpha_radian = math.atan(dy / dx)
                    alpha_degree = alpha_radian*180/math.pi 
                    if dx < 0 :
                        alpha_degree = 180+alpha_degree
                    self.obj.children[-1].points += touch.pos
                    line_number = -3
                    for i in range(1, self.NUMBER_OF_LINES):
                        self.obj.children[line_number].points += (center[0]+vector*math.cos(math.radians(alpha_degree+(angle*i))), center[1]+vector*math.sin(math.radians(alpha_degree+(angle*i))))
                        line_number -= 2
                    if self.DRAWING_MODE == 'radian-symmetric':
                        for i in range(0, self.NUMBER_OF_LINES):
                            self.obj.children[line_number].points += (center[0]-vector*math.cos(math.radians(alpha_degree+(angle*i-45))), center[1]+vector*math.sin(math.radians(alpha_degree+(angle*i-45))))
                            line_number -= 2
        else:
            # Start drawing line
            self.drawing = True
            self.obj = InstructionGroup()
            self.obj.add(Color(*self.COLOR))
            if self.DRAWING_MODE == 'simple':
                self.obj.add(Line(width=self.LINE_WIDTH))
            elif self.DRAWING_MODE == 'symmetric':
                for _ in range(2):
                    self.obj.add(Line(width=self.LINE_WIDTH))
            elif self.DRAWING_MODE == 'square':
                for _ in range(4):
                    self.obj.add(Line(width=self.LINE_WIDTH))
            elif self.DRAWING_MODE == 'radian':
                for _ in range(self.NUMBER_OF_LINES):
                    self.obj.add(Line(width=self.LINE_WIDTH))
            elif self.DRAWING_MODE == 'radian-symmetric':
                for _ in range(self.NUMBER_OF_LINES*2):
                    self.obj.add(Line(width=self.LINE_WIDTH))
        
            self.lineslist.append(self.obj)
            self.canvas.add(self.obj)


    #------------------#
    #-SYSTEM FUNCTIONS-#
    #------------------#
    def undo(self):
        '''delete last line'''
        if self.lineslist:
            item = self.lineslist.pop(-1)
            self.undolist.append(item)
            self.canvas.remove(item)

    def redo(self):
        '''return last line'''
        if self.undolist:
            item = self.undolist.pop(-1)
            self.lineslist.append(item)
            self.canvas.add(item)
        
    def clear_canvas(self):
        self.canvas.clear()
        self.undolist = []
        self.lineslist = []


class MyPaintApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.primary_hue = "200"
        return Container()



if __name__ == '__main__':
    MyPaintApp().run()