from game.chair_renderer import ChairRenderer
from game.laptop_renderer import LaptopRenderer
from game.timer_renderer import TimerRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class TeacherDeskRenderer:
    def __init__(self):
        self.laptop_renderer = LaptopRenderer()
        self.timer_renderer = TimerRenderer()
        self.chair_renderer = ChairRenderer()

    def _draw_desk_geometry(self):
        # Table Top (Darker mahogany-style wood)
        glColor3f(0.4, 0.25, 0.15)
        glPushMatrix()
        glTranslatef(0, 0, 40)
        glScalef(80, 50, 2)  # Slightly larger than a standard desk
        glutSolidCube(1.0)
        glPopMatrix()

        # Table Legs (darker wood/metal)
        glColor3f(0.2, 0.1, 0.05)
        for dx in [-36, 36]:
            for dy in [-21, 21]:
                glPushMatrix()
                glTranslatef(dx, dy, 19.5)
                glScalef(4, 4, 39)
                glutSolidCube(1.0)
                glPopMatrix()

    def render(self, desk_transform, state):
        # Render the main desk physical structure
        glPushMatrix()
        glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)
        glRotatef(desk_transform.yaw, 0, 0, 1)
        self._draw_desk_geometry()

        # Render the chair behind the teacher desk
        glPushMatrix()
        glTranslatef(0, -30, 0)
        self.chair_renderer._draw_chair()
        glPopMatrix()

        glPopMatrix()

        if hasattr(state, "laptop"):
            self.laptop_renderer.render(desk_transform, state.laptop)

        if hasattr(state, "timer"):
            self.timer_renderer.render(desk_transform, state.timer)
