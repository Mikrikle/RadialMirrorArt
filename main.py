from random import random
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line, InstructionGroup
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
import math
Window.size = (540,960)


def set_bg(dt=None, bg=(0,0,0,1)):
    '''make canvas black'''
    Window.clearcolor = bg
Clock.schedule_once(set_bg, 1)


class CustomDropDown(DropDown):
    pass

class Container(FloatLayout):
    pass


class MyPaintWidget(Widget):
    drawing_mode_select_btn = ObjectProperty()
    undolist = [] # list of cancelled lines
    lineslist = [] # list of drawing lines
    drawing = False
    
    DRAWING_MODE = 'radian'
    NUMBER_OF_LINES = 10
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint=None,None
        self.create_drawing_mode_dropdown()
        
    #--------------------#
    #-DROPDOWN FUNCTIONS-#
    #--------------------#
    def create_drawing_mode_dropdown(self):
        '''creating a menu for switching drawing modes'''
        self.dropdown_drawing_mode = CustomDropDown()
        self.dropdown_drawing_mode.bind(on_select=lambda instance, x: self.drawing_mode_custom_setattr(x[0], x[1]) )


    def drawing_mode_custom_setattr(self, mode, icon):
        '''setting the current drawing mode and icon'''
        setattr(self.drawing_mode_select_btn, 'icon', icon)
        self.DRAWING_MODE = mode


    def dropdown_drawing_mode_open_menu(self, btn):
        '''open dropdoen menu'''
        self.dropdown_drawing_mode.open(btn)

    #-------------------#
    #-DRAWING FUNCTIONS-#
    #-------------------#
    def on_touch_up(self, touch):
        '''disabling drawing'''
        self.drawing = False


    def draw_square_lines(self, pos, coeff):
        self.obj.children[-1 - coeff].points += pos
        self.obj.children[-3 - coeff].points += (pos[0], Window.size[1] - pos[1])
        self.obj.children[-5 - coeff].points += (Window.size[0] - pos[0], pos[1])
        self.obj.children[-7 - coeff].points += (Window.size[0] - pos[0], Window.size[1] - pos[1])
    
    def on_touch_move(self, touch):
        '''drawing'''
        
        def vector_length(coords, center):
            return math.sqrt( (coords[0]-center[0])**2 + (coords[1]-center[1])**2 )
        
        if self.drawing:
            # Continue drawing line
            if self.DRAWING_MODE == 'simple':
                self.obj.children[-1].points += touch.pos
            elif self.DRAWING_MODE == 'symmetric':
                self.obj.children[-1].points += touch.pos
                self.obj.children[-3].points += (Window.size[0] - touch.pos[0], touch.pos[1])
            elif self.DRAWING_MODE == 'square':
                self.draw_square_lines(touch.pos, 0)
            elif self.DRAWING_MODE == 'radian' or  self.DRAWING_MODE == 'radian-symmetric':
                center = (Window.size[0]//2, Window.size[1]//2)
                angle = 360/self.NUMBER_OF_LINES
                dx = touch.pos[0] - center[0]
                dy = touch.pos[1] - center[1]
                l = vector_length(touch.pos, center)
                if dx != 0:
                    alpha_radian = math.atan( dy / dx )
                    alpha_degree = alpha_radian*180/math.pi 
                    
                    if dx < 0 :
                        alpha_degree = 180+alpha_degree

                    self.obj.children[-1].points += touch.pos
                    line_number = -3
                    for i in range(1, self.NUMBER_OF_LINES):
                        self.obj.children[line_number].points += ( center[0]+l*math.cos(math.radians(alpha_degree+(angle*i))), center[1]+l*math.sin(math.radians(alpha_degree+(angle*i))))
                        line_number -= 2
                    if self.DRAWING_MODE == 'radian-symmetric':
                        for i in range(0, self.NUMBER_OF_LINES):
                            self.obj.children[line_number].points += ( center[0]-l*math.cos(math.radians(alpha_degree+(angle*i-45))), center[1]+l*math.sin(math.radians(alpha_degree+(angle*i-45))))
                            line_number -= 2
        else:
            # Start drawing line
            self.drawing = True
            self.obj = InstructionGroup()
            self.obj.add(Color(random(),1,1, mode='hsv'))
            if self.DRAWING_MODE == 'simple':
                self.obj.add(Line())
            elif self.DRAWING_MODE == 'symmetric':
                for _ in range(2):
                    self.obj.add(Line())
            elif self.DRAWING_MODE == 'square':
                for _ in range(4):
                    self.obj.add(Line())
            elif self.DRAWING_MODE == 'radian':
                for _ in range(self.NUMBER_OF_LINES):
                    self.obj.add(Line())
            elif self.DRAWING_MODE == 'radian-symmetric':
                for _ in range(self.NUMBER_OF_LINES*2):
                    self.obj.add(Line())
        
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