from components.laptop_state import TYPING_TEXT
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class LaptopRenderer:

    def draw_cube(self, w, h, d):
        glPushMatrix()
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

    def draw_box(self, x0, y0, z0, x1, y1, z1):
        glBegin(GL_QUADS)
        # Bottom
        glVertex3f(x0, y0, z0)
        glVertex3f(x1, y0, z0)
        glVertex3f(x1, y1, z0)
        glVertex3f(x0, y1, z0)
        # Top
        glVertex3f(x0, y0, z1)
        glVertex3f(x1, y0, z1)
        glVertex3f(x1, y1, z1)
        glVertex3f(x0, y1, z1)
        # Front
        glVertex3f(x0, y0, z0)
        glVertex3f(x1, y0, z0)
        glVertex3f(x1, y0, z1)
        glVertex3f(x0, y0, z1)
        # Back
        glVertex3f(x0, y1, z0)
        glVertex3f(x1, y1, z0)
        glVertex3f(x1, y1, z1)
        glVertex3f(x0, y1, z1)
        # Left
        glVertex3f(x0, y0, z0)
        glVertex3f(x0, y1, z0)
        glVertex3f(x0, y1, z1)
        glVertex3f(x0, y0, z1)
        # Right
        glVertex3f(x1, y0, z0)
        glVertex3f(x1, y1, z0)
        glVertex3f(x1, y1, z1)
        glVertex3f(x1, y0, z1)
        glEnd()

    def draw_face(self, x0, y, z0, x1, z1):
        """Single quad on a fixed Y plane. Each screen layer gets a
        slightly different Y so they never share the same depth."""
        glBegin(GL_QUADS)
        glVertex3f(x0, y, z0)
        glVertex3f(x1, y, z0)
        glVertex3f(x1, y, z1)
        glVertex3f(x0, y, z1)
        glEnd()

    def _draw_laptop_model(self):
        # ── Base ─────────────────────────────────────────────────────
        glColor3f(0.20, 0.20, 0.20)
        self.draw_box(-10, -7, 0, 10, 7, 1.6)

        # Keyboard recess
        glColor3f(0.10, 0.10, 0.10)
        self.draw_box(-7.5, -2.5, 1.6, 7.5, 5.2, 1.75)

        # Trackpad
        glColor3f(0.15, 0.15, 0.15)
        self.draw_box(-2.8, -5.8, 1.6, 2.8, -3.2, 1.75)

        # Hinge bar
        glColor3f(0.30, 0.30, 0.30)
        self.draw_box(-10, 6.0, 1.4, 10, 7.2, 2.2)

        # ── Lid ──────────────────────────────────────────────────────
        LID_Y0 = 6.2
        LID_Y1 = 7.2
        LID_Z0 = 1.8
        LID_Z1 = 13.5

        glColor3f(0.20, 0.20, 0.20)
        self.draw_box(-10, LID_Y0, LID_Z0, 10, LID_Y1, LID_Z1)

        # ── Screen layers — each at a strictly different Y ────────────
        # Step 0.04 units forward per layer so no two quads share a plane.

        # 1. Outer bezel
        glColor3f(0.08, 0.08, 0.08)
        self.draw_face(-9.2, LID_Y0 - 0.04, LID_Z0 + 0.3, 9.2, LID_Z1 - 0.3)

        # 2. Screen border (grey ring)
        glColor3f(0.22, 0.22, 0.24)
        self.draw_face(-8.6, LID_Y0 - 0.08, LID_Z0 + 0.7, 8.6, LID_Z1 - 0.55)

        # 3. Screen face (near-black)
        glColor3f(0.04, 0.04, 0.06)
        self.draw_face(-8.0, LID_Y0 - 0.12, LID_Z0 + 1.0, 8.0, LID_Z1 - 0.9)

        # 4. Screen glow (dim green tint — reads as "on")
        glColor3f(0.05, 0.18, 0.08)
        self.draw_face(-7.8, LID_Y0 - 0.16, LID_Z0 + 1.15, 7.8, LID_Z1 - 1.05)

    def _render_on_desk(self, desk_transform):
        glPushMatrix()
        glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)
        glRotatef(desk_transform.yaw, 0, 0, 1)
        glTranslatef(-10.0, -10.0, 41.0)
        self._draw_laptop_model()
        glPopMatrix()

    # ------------------------------------------------------------------
    # Interaction HUD
    # ------------------------------------------------------------------
    def _render_work_hud(self, state):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, 800, 0, 600, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Full black background
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(800, 0)
        glVertex2f(800, 600)
        glVertex2f(0, 600)
        glEnd()

        # Outer bezel
        glColor3f(0.10, 0.10, 0.10)
        glBegin(GL_QUADS)
        glVertex2f(80, 60)
        glVertex2f(720, 60)
        glVertex2f(720, 540)
        glVertex2f(80, 540)
        glEnd()

        # Screen border
        glColor3f(0.20, 0.20, 0.22)
        glBegin(GL_QUADS)
        glVertex2f(90, 70)
        glVertex2f(710, 70)
        glVertex2f(710, 530)
        glVertex2f(90, 530)
        glEnd()

        # Screen face (near-black)
        glColor3f(0.03, 0.03, 0.05)
        glBegin(GL_QUADS)
        glVertex2f(100, 80)
        glVertex2f(700, 80)
        glVertex2f(700, 520)
        glVertex2f(100, 520)
        glEnd()

        glDisable(GL_BLEND)

        # ── Typing text ──
        TEXT_SCALE = 0.11
        LINE_HEIGHT = 17
        MARGIN_X = 112
        START_Y = 505

        visible = TYPING_TEXT[: state.typed_chars]
        lines = visible.split("\n")

        glColor3f(0.18, 0.93, 0.38)
        glLineWidth(1.2)

        for i, line in enumerate(lines):
            y = START_Y - i * LINE_HEIGHT
            if y < 88:
                break
            if not line:
                continue
            glPushMatrix()
            glTranslatef(float(MARGIN_X), float(y), 0.0)
            glScalef(TEXT_SCALE, TEXT_SCALE, 1.0)
            for ch in line:
                if ch.isprintable():
                    glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
            glPopMatrix()

        # Blinking cursor
        import math
        import time as _t

        if not state.is_work_done and math.sin(_t.time() * 6) > 0:
            last = lines[-1] if lines else ""
            row = len(lines) - 1
            cx = MARGIN_X + int(len(last) * 104.76 * TEXT_SCALE)
            cy = START_Y - row * LINE_HEIGHT
            if 88 <= cy <= 520:
                glPushMatrix()
                glTranslatef(float(cx), float(cy), 0.0)
                glScalef(TEXT_SCALE, TEXT_SCALE, 1.0)
                glutStrokeCharacter(GLUT_STROKE_ROMAN, ord("|"))
                glPopMatrix()

        # Status line
        if state.is_work_done:
            glColor3f(0.18, 0.93, 0.38)
            glPushMatrix()
            glTranslatef(float(MARGIN_X), 84.0, 0.0)
            glScalef(TEXT_SCALE, TEXT_SCALE, 1.0)
            for ch in "Work saved.  Press [SPACE] to return.":
                glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
            glPopMatrix()

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def render(self, desk_transform, state):
        if not state.is_visible:
            return
        if state.is_being_used:
            self._render_work_hud(state)
        else:
            self._render_on_desk(desk_transform)
