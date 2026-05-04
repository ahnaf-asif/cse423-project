from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from .calculator_renderer import CalculatorRenderer
from .chair_renderer import ChairRenderer
from .cheatsheet_renderer import CheatsheetRenderer
from .exam_sheet_renderer import ExamSheetRenderer
from .smartphone_renderer import SmartphoneRenderer


class StudentDeskRenderer:
    def __init__(self):
        self.exam_sheet_renderer = ExamSheetRenderer()
        self.calculator_renderer = CalculatorRenderer()
        self.smartphone_renderer = SmartphoneRenderer()
        self.cheatsheet_renderer = CheatsheetRenderer()
        self.chair_renderer = ChairRenderer()

    def draw_cube(self, w, h, d):
        """Helper to draw scaled cubes (Rectangular Prisms)"""
        glPushMatrix()
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

    def render(self, transform, state):
        glPushMatrix()
        glTranslatef(transform.x, transform.y, transform.z)
        glRotatef(transform.yaw, 0, 0, 1)

        glColor3f(0.5, 0.35, 0.2)
        glPushMatrix()
        glTranslatef(0, 0, 40)
        self.draw_cube(70, 40, 2)
        glPopMatrix()

        glColor3f(0.3, 0.2, 0.1)
        for dx in [-32, 32]:
            for dy in [-17, 17]:
                glPushMatrix()
                glTranslatef(dx, dy, 19.5)
                self.draw_cube(4, 4, 39)
                glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -25, 0)
        self.chair_renderer._draw_chair()
        glPopMatrix()

        glPopMatrix()

        self.exam_sheet_renderer.render(transform, state.exam_sheet)
        self.calculator_renderer.render(transform, state.calculator)
        self.smartphone_renderer.render(transform, state.smartphone)
        self.cheatsheet_renderer.render(transform, state.cheatsheet)
