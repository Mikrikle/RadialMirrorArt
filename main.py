from random import random
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivymd.uix.button import MDRectangleFlatButton
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line, InstructionGroup
from kivy.core.window import Window
from kivy.properties import ObjectProperty
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

class CustomDropDown(DropDown):
    pass

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
        self.create_draw_popup()
    
    #---------------#
    #-Popup windows-#
    #---------------#
    

    
    def create_draw_popup(self):
        def create_slider(name, min_value, max_value, base_value, func):
            main_box = BoxLayout(orientation='vertical',size_hint=(1,.9))
            slider_box = BoxLayout()
            info_label = Label(text=name, size_hint=(1,.5))
            #
            slider_lbl = Label(text=str(base_value), size_hint=(.3,1))
            slider = MDSlider(min=min_value, max=max_value, value=base_value, on_touch_move=lambda this, touch : func(int(this.value)))
            #
            slider_box.add_widget(slider_lbl)
            slider_box.add_widget(slider)
            main_box.add_widget(info_label)
            main_box.add_widget(slider_box)
            return main_box, slider, slider_lbl
        self.create_drawing_mode_dropdown()
        self.draw_popup = MyPopup()
        self.draw_popup.title = 'Settings for drawing'
        bxl = BoxLayout(orientation='vertical', padding=15)
        # drawing mode
        dr_box = BoxLayout()
        self.curent_drawing_mode_icon = MDIconButton(icon='decagram-outline')
        self.drawing_mode_dropdown_open_btn = MDRoundFlatButton(text='drawing type' ,on_release=lambda instance: self.dropdown_drawing_mode.open(instance), size_hint=(.1,.6))
        dr_box.add_widget(self.drawing_mode_dropdown_open_btn)
        dr_box.add_widget(Widget(size_hint=(.03,1)))
        dr_box.add_widget(self.curent_drawing_mode_icon)
        bxl.add_widget(dr_box)
        bxl.add_widget(Widget())
        # sliders
        num_box, _, self.number_of_lines_lbl = create_slider('Lines', 2, 250, self.NUMBER_OF_LINES, self.set_number_of_lines)
        bxl.add_widget(num_box)
        bxl.add_widget(Widget())
        line_box, _, self.line_width_lbl = create_slider('Line width', 1, 25, self.LINE_WIDTH, self.set_line_width)
        bxl.add_widget(line_box)
        bxl.add_widget(Widget())
        
        # close
        bxl.add_widget(MDRectangleFlatButton(text="Close", size_hint=(1,.5), on_release=lambda btn: self.draw_popup.dismiss()))
        self.draw_popup.add_widget(bxl)

    def set_line_width(self, value):
        self.LINE_WIDTH = value
        self.line_width_lbl.text = str(value)
        self.down_current_line_width.text = f'Width\n{value}'

    def set_number_of_lines(self, value):
        self.NUMBER_OF_LINES = value
        self.number_of_lines_lbl.text = str(value)
        self.down_current_nums_of_lines.text = f'Lines\n{value}'
        
        
    
    def open_draw_popup(self):
        '''open popup window'''
        self.draw_popup.open()
    
    
    def drawing_mode_custom_setattr(self, mode, icon):
        '''setting the current drawing mode and icon'''
        setattr(self.curent_drawing_mode_icon, 'icon', icon)
        setattr(self.down_current_icon, 'icon', icon)
        self.DRAWING_MODE = mode
    
    
    def create_drawing_mode_dropdown(self):
        '''creating a menu for switching drawing modes'''
        self.dropdown_drawing_mode = CustomDropDown()
        self.dropdown_drawing_mode.bind(on_select=lambda instance, x: self.drawing_mode_custom_setattr(x[0], x[1]) )
        

    
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
        self.down_current_color_label.canvas.children[0] = Color(*value)


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