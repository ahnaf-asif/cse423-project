from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class ChairRenderer:
    def draw_cube(self, w, h, d):
        glPushMatrix()
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

    def _draw_chair(self):
        # 4 Legs (Dark Grey Metal)
        glColor3f(0.25, 0.25, 0.25)
        leg_positions = [(-10.5, -10.5), (10.5, -10.5), (-10.5, 10.5), (10.5, 10.5)]
        for x, y in leg_positions:
            glPushMatrix()
            glTranslatef(x, y, 14)
            self.draw_cube(2.5, 2.5, 28)
            glPopMatrix()

        # Seat Cushion (Brown)
        glColor3f(0.55, 0.4, 0.2)
        glPushMatrix()

        glTranslatef(0, 0, 29)
        self.draw_cube(26, 26, 2.5)
        glPopMatrix()

        # Backrest (Wood)
        glColor3f(0.4, 0.2, 0.1)
        glPushMatrix()

        glTranslatef(0, -11.5, 43)
        self.draw_cube(26, 2.5, 26)
        glPopMatrix()

    def render(self, transform, state):
        glPushMatrix()
        glTranslatef(transform.x, transform.y, transform.z)
        glRotatef(transform.yaw, 0, 0, 1)

        self._draw_chair()

        glPopMatrix()
