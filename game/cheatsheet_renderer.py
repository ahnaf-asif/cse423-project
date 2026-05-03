from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class CheatsheetRenderer:
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

    def _draw_paper_model(self):
        """Pure geometry of the cheat sheet paper."""
        # --- Base Paper ---
        glColor3f(0.95, 0.95, 0.9)  # Off-white / cream paper color
        self.draw_cube(5.0, 7.0, 0.1)

        # --- Hand-written Lines / Formulas (simulated) ---
        glColor3f(0.1, 0.1, 0.4)  # Dark blue ink

        # Draw a few staggered lines to look like scribbled notes
        line_data = [
            (0, 2.0, 4.0),
            (-0.5, 1.0, 3.0),
            (0.5, 0.0, 3.5),
            (0, -1.0, 4.2),
            (-0.2, -2.0, 3.8),
        ]

        for x_offset, y_pos, width in line_data:
            glPushMatrix()
            glTranslatef(x_offset, y_pos, 0.06)  # Slightly above the paper surface
            self.draw_cube(width, 0.15, 0.05)
            glPopMatrix()

    def _render_on_desk(self, desk_transform):
        """Draws the cheat sheet resting on the desk."""
        glPushMatrix()
        glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)
        glRotatef(desk_transform.yaw, 0, 0, 1)

        # Placed slightly to the side of the calculator (-20, 10)
        # Sitting completely flush with the table (Z=41.05)
        glTranslatef(-12, 12, 41.05)
        glRotatef(-25, 0, 0, 1)  # Angled casually

        self._draw_paper_model()
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
        self.draw_text("ADDITIONAL DOCUMENT", 0.0015, 1.5)

        glTranslatef(0, -0.5, 0)
        # --- AMBIGUOUS STATUS UPDATE ---
        glColor3f(0.9, 0.6, 0.2)  # Suspicious Orange/Yellow instead of Warning Red
        self.draw_text("STATUS: UNVERIFIED MATERIAL", 0.0009, 1.0)

        glTranslatef(0, -0.3, 0)
        glColor3f(0.8, 0.8, 0.8)
        # --- AMBIGUOUS NOTES UPDATE ---
        self.draw_text("Notes: Non-standard sheet detected.", 0.0009, 1.0)

        glTranslatef(0, -0.3, 0)
        # --- ACTION UPDATE ---
        self.draw_text("Action: Press [ESC] to Return", 0.0009, 1.0)
        glPopMatrix()

        # 3. Right Side: Scaled-Down Paper
        glPushMatrix()
        # Position it to the right and angle it towards the camera so it reads well
        glTranslatef(2.0, 0.0, -4.0)
        glRotatef(-15, 1, 0, 0)
        glRotatef(-15, 0, 1, 0)

        glScalef(0.2, 0.2, 0.2)
        self._draw_paper_model()
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
