from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class SmartphoneRenderer:
    def draw_cube(self, w, h, d):
        glPushMatrix()
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

    def draw_text(self, text, scale, weight):
        """Helper to draw 3D stroke text."""
        glPushMatrix()
        glScalef(scale, scale, scale)
        glLineWidth(weight)
        for char in text:
            glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))
        glPopMatrix()

    def _draw_phone_model(self):
        """Pure geometry of the phone. Used by both Desk and Inspection views."""
        # --- Base Casing ---
        glColor3f(0.2, 0.2, 0.2)  # Neutral dark casing
        self.draw_cube(7.5, 14.5, 0.6)

        # --- The Cheating Screen ---
        glColor3f(0.1, 0.4, 0.2)
        glPushMatrix()
        glTranslatef(0, 0, 0.3)
        self.draw_cube(6.8, 13.8, 0.1)
        glPopMatrix()

        # --- ChatGPT Title ---
        glColor3f(0.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(-2.9, 4.5, 0.38)
        self.draw_text("ChatGPT", 0.008, 3.0)
        glPopMatrix()

        # --- Generated Essay Blocks ---
        glColor3f(0.05, 0.25, 0.1)
        glPushMatrix()
        glTranslatef(0, 1.5, 0.38)
        self.draw_cube(5.5, 3.0, 0.05)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -2.5, 0.38)
        self.draw_cube(5.5, 4.0, 0.05)
        glPopMatrix()

    def _render_on_desk(self, desk_transform):
        glPushMatrix()
        glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)
        glRotatef(desk_transform.yaw, 0, 0, 1)

        glTranslatef(-22, 10, 41.3)
        glRotatef(-15, 0, 0, 1)  

        self._draw_phone_model()
        glPopMatrix()

    def _render_inspection_hud(self):
        """Draws a simpler, scaled-down inspection overlay."""
        glPushMatrix()
        glLoadIdentity()  

        #  Full-Screen Dark Overlay 
        glDisable(GL_DEPTH_TEST) 
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(0.0, 0.0, 0.0, 0.8)  # 80% Black
        glBegin(GL_QUADS)
        glVertex3f(-50, -50, -5)
        glVertex3f(50, -50, -5)
        glVertex3f(50, 50, -5)
        glVertex3f(-50, 50, -5)
        glEnd()

        glEnable(GL_DEPTH_TEST)  

        #  Left Side: Evidence Text
        glColor3f(1.0, 1.0, 1.0)  # White
        glPushMatrix()

        glTranslatef(-2.8, 1.5, -4.9)

        self.draw_text("EVIDENCE LOG", 0.0015, 1.5)

        glTranslatef(0, -0.5, 0)
        glColor3f(0.9, 0.2, 0.2)  # Muted red

        self.draw_text("STATUS: UNAUTHORIZED DEVICE", 0.0009, 1.0)

        glTranslatef(0, -0.3, 0)
        glColor3f(0.8, 0.8, 0.8)  # Grey
        self.draw_text("Active Application: ChatGPT", 0.0009, 1.0)

        glTranslatef(0, -0.3, 0)
        self.draw_text("Action: Press [ESC] to Return", 0.0009, 1.0)
        glPopMatrix()

        # Right Side: Scaled-Down Phone
        glPushMatrix()
        glTranslatef(2.0, 0.0, -4.0)
        glRotatef(-10, 1, 0, 0)
        glRotatef(-10, 0, 1, 0)

        glScalef(0.1, 0.1, 0.1)
        self._draw_phone_model()
        glPopMatrix()

        glDisable(GL_BLEND)
        glPopMatrix()

    def render(self, desk_transform, state):
        """Main routing logic."""
        if not state.is_visible:
            return

        if state.is_being_inspected:
            self._render_inspection_hud()
        else:
            self._render_on_desk(desk_transform)
