from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class ExamSheetRenderer:
    def draw_cube(self, w, h, d):
        glPushMatrix()
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

    def render(self, desk_transform, state):
        if not state.is_visible:
            return

        glPushMatrix()
        # Move to desk position
        glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)
        glRotatef(desk_transform.yaw, 0, 0, 1)

        # Local offset to sit on the desk
        glColor3f(1.0, 1.0, 1.0)  # White paper
        glTranslatef(10, -5, 41.1)
        self.draw_cube(20, 26, 0.1)
        glPopMatrix()
