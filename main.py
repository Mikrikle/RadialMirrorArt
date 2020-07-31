try:
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                         Permission.READ_EXTERNAL_STORAGE])
    ANDROID = True
except:
    ANDROID = False

import math
import random
import datetime
import os

from gradient import GRADIENT_DATA_BRIGHTER, GRADIENT_DATA_DARKER

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, Line, InstructionGroup, Rectangle
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, NumericProperty, ListProperty

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.stencilview import StencilView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.colorpicker import ColorPicker
from kivymd.uix.button import MDRoundFlatButton, MDIconButton, MDRectangleFlatButton
from kivymd.uix.slider import MDSlider
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.snackbar import Snackbar


def set_bg(dt=None, bg=(0,0,0,1)):
    '''make canvas black'''
    Window.clearcolor = bg
Clock.schedule_once(set_bg, 1)


class MyPopup(Popup):
    pass


class CustomDropDownDrawingMode(DropDown):
    pass


class Container(FloatLayout):
    pass


class SettingsPopup(Popup):
    VALUE = NumericProperty()
    def __init__(self, paint, **kwargs):
        super().__init__(**kwargs)
        self.paint = paint
        self.color_popup = ColorPopup('Colors', self.paint)
        
    def set_effects(self, value):
        self.paint.BLUUR_SIZE = value

    def save_canvas(self):
        self.paint.save_canvas()


class ColorPopup(Popup):
    colorbox = ObjectProperty()
    no_bg_switch = ObjectProperty()

    def __init__(self, title, paint, **kwargs):
        super().__init__(**kwargs)
        self.paint = paint
        self.title = title
        self.colorpicker = ColorPicker(color=self.paint.BACKGROUND_COLOR)
        self.colorbox.add_widget(self.colorpicker)
        self.colorbox.add_widget(MDRectangleFlatButton(size_hint=(1,.1), text='Close', on_release=lambda btn:self.dismiss()))
        
    def set_bg(self):
        if self.no_bg_switch.active:
            Window.clearcolor = list(self.colorpicker.color)
            sself.paint.canvas.before.get_group('background')[0].a = 0
        else:
            current_bg = self.paint.canvas.before.get_group('background')[0]
            current_bg.r = self.colorpicker.color[0]
            current_bg.g = self.colorpicker.color[1]
            current_bg.b =self.colorpicker.color[2]
            current_bg.a = self.colorpicker.color[3]
            self.paint.BACKGROUND_COLOR = self.colorpicker.color
    
    def set_center(self):
        current_center = self.paint.canvas.before.get_group('center')[0]
        current_center.r = self.colorpicker.color[0]
        current_center.g = self.colorpicker.color[1]
        current_center.b =self.colorpicker.color[2]
        current_center.a = self.colorpicker.color[3]
        self.paint.CENTER_COLOR = self.colorpicker.color

    
    def disable_bg(self):
        if self.no_bg_switch.active:
            Window.clearcolor = list(self.paint.BACKGROUND_COLOR)
            self.paint.canvas.before.get_group('background')[0].a = 0
        else:
            Window.clearcolor = (0,0,0,1)
            self.paint.canvas.before.get_group('background')[0].a = 1


class SliderDropDown(DropDown):
    '''Base class for fast line and color settings'''
    VALUE = NumericProperty()
    HEIGHT = NumericProperty(Window.size[1]//2)
    def __init__(self, value, paint, **kwargs):
        super().__init__(**kwargs)
        self.VALUE = value
        self.paint = paint

    def slider_setattr(self, value):
        pass


class CustomDropDownNumberOfLines(SliderDropDown):
    '''Slider dropdown for settings line'''
    def slider_setattr(self, value):
        self.paint.set_number_of_lines(value)
        
    def set_close_lines(self, value):
        self.paint.IS_LINE_CLOSE = value


class CustomDropDownLineWidth(SliderDropDown):
    '''Slider dropdown for settings width'''
    def slider_setattr(self, value):
        self.paint.set_line_width(value)


class MyPaintWidget(Widget):
    drawing_mode_select_btn = ObjectProperty()
    down_current_color_label = ObjectProperty()
    down_current_line_width = ObjectProperty()
    down_current_nums_of_lines = ObjectProperty()
    down_current_icon = ObjectProperty()
    top_toolbox = ObjectProperty()
    down_toolbox = ObjectProperty()
    minimize_btn = ObjectProperty()
    undolist = [] # list of cancelled lines
    lineslist = [] # list of drawing lines
    drawing = False

    DRAWING_MODE = 'radian'
    NUMBER_OF_LINES = 15
    LINE_WIDTH = 1
    COLOR = (1,0,0,1)
    BACKGROUND_COLOR = ListProperty([0, 0, 0, 1])
    CENTER_COLOR = ListProperty([.5,.5,.5,1])
    IS_LINE_CLOSE = False
    TEXTURE = GRADIENT_DATA_BRIGHTER
    BLUUR_SIZE = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size=Window.size
        self.size_hint=None,None
        self.create_color_popup()
        self.create_settings_popup()
        self.create_number_of_lines_dropdown()
        self.create_drawing_mode_dropdown()
        self.create_lines_width_dropdown()
        self.init_animations()
        self.create_snackbars()
        self.init_texture()

    def init_texture(self):
        self.tex = Texture.create(size=(1, 64), colorfmt='rgb', bufferfmt='ubyte')
        self.tex.blit_buffer(self.TEXTURE, colorfmt='rgb')

    def create_snackbars(self):
        '''Snackbars with saving info'''
        self.snackbar_success = Snackbar(text='Successful saving!')
        self.snackbar_error = Snackbar()

    def init_animations(self):
        self.minimize_btn_anim = Animation(pos_hint = {'x':.85, 'y':.01}, t='in_out_back', duration=.35)
        self.maximize_btn_anim = Animation(pos_hint = {'x':.85, 'y':.06}, t='in_out_back', duration=.35)
        self.maximize_top_toolbox_anim = Animation(pos_hint = {'x': 0, 'y': 0.9}, t='in_circ', duration=.3)
        self.minimize_top_tollbox_anim = Animation(pos_hint = {'x': 0, 'y': 1}, t='in_circ', duration=.3)
        self.maximize_down_tollbox_anim = Animation(pos_hint = {'x': 0, 'y': 0}, t='in_circ', duration=.3)
        self.minimize_down_tollbox_anim = Animation(pos_hint = {'x': 0, 'y': -0.1}, t='in_circ', duration=.3)

    def minimize_maximize_toolboxes(self, current):
        if current == 'arrow-down':
            # minimize
            self.minimize_top_tollbox_anim.start(self.top_toolbox)
            self.minimize_down_tollbox_anim.start(self.down_toolbox)
            self.minimize_btn.icon = 'arrow-up' 
            self.minimize_btn_anim.start(self.minimize_btn)
        elif current == 'arrow-up':
            # maximize
            self.maximize_top_toolbox_anim.start(self.top_toolbox)
            self.maximize_down_tollbox_anim.start(self.down_toolbox)
            self.minimize_btn.icon = 'arrow-down'
            self.maximize_btn_anim.start(self.minimize_btn)

    #-----------------------#
    #-Settings Popup window-#
    #-----------------------#
    
    def create_settings_popup(self):
        '''Creating a drawing settings window'''
        self.settings_popup = SettingsPopup(self)

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
        self.random_color_select = MDSwitch()
        radmcolrbx = BoxLayout(size_hint=(1,.15))
        radmcolrbx.add_widget(Label(text='Use random colors:'))
        radmcolrbx.add_widget(self.random_color_select)
        bxl.add_widget(radmcolrbx)
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
        
        # protection against memory overuse
        if len(self.undolist) > 5:
            self.undolist = self.undolist[len(self.undolist)-5:]
        if len(self.lineslist) > 5:
            self.lineslist = self.lineslist[len(self.lineslist)-5:]

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
                vector = vector_length(touch.pos, center)
                if dx != 0:
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
            
            if self.random_color_select.active:
                self.on_color(None, (random.random(),random.random(),random.random(),1))
            
            self.obj.add(Color(*self.COLOR))
            
            lines = {'simple':1,
                  'symmetric':2,
                  'square':4,
                  'radian':self.NUMBER_OF_LINES,
                  'radian-symmetric':self.NUMBER_OF_LINES*2}
            
            for _ in range(lines[self.DRAWING_MODE]):
                self.obj.add(Line(width=self.LINE_WIDTH, close=self.IS_LINE_CLOSE, texture=self.tex))
        
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
        
    def save_canvas(self):
        name = f'Art{datetime.date.today()}-{random.randint(1,100000)}.png'
        try:
            if ANDROID:
                directory = os.path.join('/sdcard','Pictures', 'RadianMirrorApp')
                if not os.path.exists(directory):
                    os.makedirs(directory)
                self.parent.export_to_png(os.path.join(directory, name))
            else:
                self.parent.export_to_png(name)
            self.snackbar_success.show()
        except Exception as err:
            self.snackbar_error.text = f'Error: "{err}"'
            self.snackbar_error.show()



class MyPaintApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.primary_hue = "200"
        return Container()



if __name__ == '__main__':
    MyPaintApp().run()