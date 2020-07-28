from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line, InstructionGroup
from kivy.core.window import Window
from kivy.properties import ObjectProperty
import math
Window.size = (540,960)


if Window.size[0]//9 == Window.size[1]//16 or Window.size[0]//16 == Window.size[1]//9:
    Win_coef = 2.55
elif Window.size[0] == Window.size[1]:
    Win_coef = 150
elif  Window.size[0]//1.5 == Window.size[1] or Window.size[0] == Window.size[1]//1.5:
    Win_coef = 4
else:
    Win_coef = 4

class Container(FloatLayout):
    pass


class MyPaintWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint=None,None
        if Window.size[0] > Window.size[1]:
            self.SIZE = Window.size[1]
        else:
             self.SIZE = Window.size[0]
    
    undolist = [] # list of cancelled lines
    lineslist = [] # list of drawing lines
    drawing = False
    


    # simple symmetric square eight hexagon none axis
    DRAWING_MODE = 'axis'
    def change_drawing_mode(self, mode):
        self.DRAWING_MODE = mode
    
    def on_touch_up(self, touch):
        '''disabling drawing'''
        self.drawing = False

    
    
    def draw_square_lines(self, pos, coeff):
        self.obj.children[-1 - coeff].points += pos
        self.obj.children[-3 - coeff].points += (pos[0], Window.size[1] - pos[1])
        self.obj.children[-5 - coeff].points += (self.SIZE - pos[0], pos[1])
        self.obj.children[-7 - coeff].points += (self.SIZE - pos[0], Window.size[1] - pos[1])
    
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
                self.obj.children[-3].points += (self.SIZE - touch.pos[0], touch.pos[1])
            elif self.DRAWING_MODE == 'square':
                self.draw_square_lines(touch.pos, 0)
            elif self.DRAWING_MODE == 'eight':
                self.draw_square_lines(touch.pos, 0)
                self.draw_square_lines( (self.SIZE - touch.pos[1] + self.SIZE//Win_coef,self.SIZE- touch.pos[0]+ self.SIZE//Win_coef), 8)
            elif self.DRAWING_MODE == 'new_symmetry':
                center = (Window.size[0]//2, Window.size[1]//2)
                dx = touch.pos[0] - center[0]
                dy = touch.pos[1] - center[1]
                self.obj.children[-1].points += touch.pos
                self.obj.children[-3].points += (center[0]-dx, Window.size[1]-(center[1]-dy))
            elif self.DRAWING_MODE == 'axis':
                center = (Window.size[0]//2, Window.size[1]//2)
                number_of_lines = 10
                angle = 360/number_of_lines
                dx = touch.pos[0] - center[0] # расстояние от X точки до центра
                dy = touch.pos[1] - center[1] # расстояние от  Y точки до центра
                l = vector_length(touch.pos, center)
                if dx != 0:
                    alpha_radian = math.atan( dy / dx )
                    alpha_degree = alpha_radian*180/math.pi 
                    
                    if dx < 0 :
                        alpha_degree = 180+alpha_degree

                    self.obj.children[-1].points += touch.pos
                    line_number = -3
                    for i in range(1, number_of_lines):
                        if alpha_radian <= 0:
                            sign = -1
                        else:
                            sign = 1
                        self.obj.children[line_number].points += ( center[0]+l*math.cos(math.radians(alpha_degree+(angle*i))), center[1]+l*math.sin(math.radians(alpha_degree+(angle*i))))
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
            elif self.DRAWING_MODE == 'eight':
                for _ in range(8):
                    self.obj.add(Line())
            elif self.DRAWING_MODE == 'axis':
                for _ in range(100):
                    self.obj.add(Line())
                
                
            self.lineslist.append(self.obj)
            self.canvas.add(self.obj)


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



class MyPaintApp(App):

    def build(self):
        return Container()




if __name__ == '__main__':
    MyPaintApp().run()