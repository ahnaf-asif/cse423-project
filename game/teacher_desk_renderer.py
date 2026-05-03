from game.laptop_renderer import LaptopRenderer
from game.timer_renderer import TimerRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class TeacherDeskRenderer:
    def __init__(self):
        self.laptop_renderer = LaptopRenderer()
        self.timer_renderer = TimerRenderer()

    def _draw_desk_geometry(self):
        # Table Top (Darker mahogany-style wood)
        glColor3f(0.4, 0.25, 0.15)
        glPushMatrix()
        glTranslatef(0, 0, 40)
        glScalef(80, 50, 2)  # Slightly larger than a standard desk
        glutSolidCube(1.0)
        glPopMatrix()

        # Table Legs (Even darker wood/metal)
        glColor3f(0.2, 0.1, 0.05)
        for dx in [-36, 36]:
            for dy in [-21, 21]:
                glPushMatrix()
                glTranslatef(dx, dy, 19.5)
                glScalef(4, 4, 39)
                glutSolidCube(1.0)
                glPopMatrix()

    def render(self, desk_transform, state):
        # 1. Render the main desk physical structure
        glPushMatrix()
        glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)
        glRotatef(desk_transform.yaw, 0, 0, 1)
        self._draw_desk_geometry()
        glPopMatrix()

        # 2. Render the items on top
        # Because the TimerRenderer (and presumably LaptopRenderer) handle their own
        # offsets relative to the base desk transform, we pass the base transform directly to them.
        if hasattr(state, "laptop"):
            self.laptop_renderer.render(desk_transform, state.laptop)

        if hasattr(state, "timer"):
            self.timer_renderer.render(desk_transform, state.timer)
