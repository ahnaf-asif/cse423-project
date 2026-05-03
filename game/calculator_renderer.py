from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class CalculatorRenderer:
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

    def _draw_calculator_model(self):
        """Pure geometry of the calculator."""
        # --- Base Calculator Body ---
        glColor3f(0.2, 0.2, 0.2)
        self.draw_cube(6.0, 9.0, 1.0)

        # --- LCD Screen ---
        glColor3f(0.6, 0.7, 0.6)
        glPushMatrix()
        glTranslatef(0, 2.5, 0.55)
        self.draw_cube(4.5, 2.0, 0.2)
        glPopMatrix()

        # --- Chunky, Readable Buttons ---
        for row in range(4):
            for col in range(4):
                bx = -1.8 + col * 1.2
                by = 0.5 - row * 1.3

                if col == 3 and row == 0:
                    glColor3f(0.8, 0.3, 0.2)  # Orange/Red 'Clear' button
                elif col == 3:
                    glColor3f(0.4, 0.4, 0.4)  # Dark grey operators
                else:
                    glColor3f(0.85, 0.85, 0.85)  # Light grey numbers

                glPushMatrix()
                glTranslatef(bx, by, 0.55)
                self.draw_cube(1.0, 1.0, 0.2)
                glPopMatrix()

    def _render_on_desk(self, desk_transform):
        """Draws the calculator resting on the desk."""
        glPushMatrix()
        glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)
        glRotatef(desk_transform.yaw, 0, 0, 1)

        glTranslatef(-20, 10, 41.5)
        glRotatef(15, 0, 0, 1)

        self._draw_calculator_model()
        glPopMatrix()

    def _render_inspection_hud(self):
        """Draws the scaled-down inspection overlay."""
        glPushMatrix()
        glLoadIdentity()

        # 1. Full-Screen Dark Overlay
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(0.0, 0.0, 0.0, 0.8)
        glBegin(GL_QUADS)
        glVertex3f(-50, -50, -5)
        glVertex3f(50, -50, -5)
        glVertex3f(50, 50, -5)
        glVertex3f(-50, 50, -5)
        glEnd()

        glEnable(GL_DEPTH_TEST)

        # 2. Left Side: Evidence Text
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(-2.8, 1.5, -4.9)
        self.draw_text("EVIDENCE LOG", 0.0015, 1.5)

        glTranslatef(0, -0.5, 0)
        # --- SAFE STATUS UPDATE ---
        glColor3f(0.2, 0.9, 0.3)  # Bright, safe green
        self.draw_text("STATUS: AUTHORIZED DEVICE", 0.0009, 1.0)

        glTranslatef(0, -0.3, 0)
        glColor3f(0.8, 0.8, 0.8)
        # --- SAFE NOTES UPDATE ---
        self.draw_text("Notes: Standard Non-Programmable Model", 0.0009, 1.0)

        glTranslatef(0, -0.3, 0)
        # --- SAFE ACTION UPDATE ---
        self.draw_text("Action: Press [ESC] to Return", 0.0009, 1.0)
        glPopMatrix()

        # 3. Right Side: Scaled-Down Calculator
        glPushMatrix()
        glTranslatef(2.0, 0.0, -4.0)
        glRotatef(-10, 1, 0, 0)
        glRotatef(-10, 0, 1, 0)

        glScalef(0.15, 0.15, 0.15)
        self._draw_calculator_model()
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
