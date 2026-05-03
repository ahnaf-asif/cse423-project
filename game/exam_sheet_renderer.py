from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class ExamSheetRenderer:
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
        """Geometry for the printed exam paper."""
        # --- Base Paper ---
        glColor3f(0.95, 0.95, 0.95)  # Bright white paper
        self.draw_cube(20, 26, 0.1)

        # --- Printed Text / Layout (simulated with thin cubes) ---
        glColor3f(0.1, 0.1, 0.1)  # Black ink

        # Exam Header (Title)
        glPushMatrix()
        glTranslatef(-4, 10, 0.06)
        self.draw_cube(10, 1.0, 0.05)
        glPopMatrix()

        # Name / Date lines
        glPushMatrix()
        glTranslatef(-2, 7.5, 0.06)
        self.draw_cube(14, 0.3, 0.05)
        glPopMatrix()

        # Question Blocks
        for y_pos in [3, 0, -3, -6, -9]:
            glPushMatrix()
            glTranslatef(0, y_pos, 0.06)
            self.draw_cube(16, 0.4, 0.05)  # Main question line
            glPopMatrix()

    def _render_on_desk(self, desk_transform):
        """Draws the exam paper resting on the desk."""
        glPushMatrix()
        glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)
        glRotatef(desk_transform.yaw, 0, 0, 1)

        # Centered / slightly off-center on the student desk
        glTranslatef(10, -5, 41.05)
        glRotatef(-5, 0, 0, 1)  # Slight casual rotation

        self._draw_paper_model()
        glPopMatrix()

    def _render_inspection_hud(self, state):
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

        # 2. Left Side: HUD Text
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(-2.8, 1.5, -4.9)
        self.draw_text("EXAMINATION DOCUMENT", 0.0015, 1.5)

        glTranslatef(0, -0.5, 0)
        # --- STATUS ---
        glColor3f(0.3, 0.7, 0.9)  # Informational Blue
        self.draw_text("STATUS: IN PROGRESS", 0.0009, 1.0)

        glTranslatef(0, -0.3, 0)
        glColor3f(0.8, 0.8, 0.8)
        # --- NOTES ---
        self.draw_text("Notes: Official standardized testing material.", 0.0009, 1.0)

        # --- DYNAMIC EXTRA LOGS ---
        if hasattr(state, "extra_logs"):
            for log_str in state.extra_logs:
                glTranslatef(0, -0.3, 0)
                # Drawing the custom strings passed from the state
                self.draw_text(log_str, 0.0009, 1.0)

        glTranslatef(0, -0.3, 0)
        # --- ACTION ---
        self.draw_text("Action: Press [ESC] to Return", 0.0009, 1.0)
        glPopMatrix()

        # 3. Right Side: Scaled-Down Paper
        glPushMatrix()
        glTranslatef(2.0, 0.0, -4.0)
        glRotatef(-15, 1, 0, 0)
        glRotatef(-10, 0, 1, 0)

        glScalef(0.12, 0.12, 0.12)  # Scale down to fit the screen
        self._draw_paper_model()
        glPopMatrix()

        glDisable(GL_BLEND)
        glPopMatrix()

    def render(self, desk_transform, state):
        if not state.is_visible:
            return

        if state.is_being_inspected:
            # Pass the state to the HUD method so it can access the extra strings
            self._render_inspection_hud(state)
        else:
            self._render_on_desk(desk_transform)
