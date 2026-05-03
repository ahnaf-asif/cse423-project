from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Segment definitions for a 7-segment display.
# Each digit is a list of 7 booleans: [top, top-left, top-right, middle, bot-left, bot-right, bottom]
SEGMENTS = {
    0: [True, True, True, False, True, True, True],
    1: [False, False, True, False, False, True, False],
    2: [True, False, True, True, True, False, True],
    3: [True, False, True, True, False, True, True],
    4: [False, True, True, True, False, True, False],
    5: [True, True, False, True, False, True, True],
    6: [True, True, False, True, True, True, True],
    7: [True, False, True, False, False, True, False],
    8: [True, True, True, True, True, True, True],
    9: [True, True, True, True, False, True, True],
}

# Segment geometry: each entry is (x0, y0, x1, y1) in local digit space.
# Digit bounding box is 0..6 wide, 0..10 tall.
SEG_THICKNESS = 0.8


def _seg_quads():
    t = SEG_THICKNESS
    return [
        # top
        (t, 10 - t, 6 - t, 10),
        # top-left
        (0, 5 + t, t, 10 - t),
        # top-right
        (6 - t, 5 + t, 6, 10 - t),
        # middle
        (t, 5 - t, 6 - t, 5 + t),
        # bot-left
        (0, t, t, 5 - t),
        # bot-right
        (6 - t, t, 6, 5 - t),
        # bottom
        (t, 0, 6 - t, t),
    ]


SEG_QUADS = _seg_quads()


class TimerRenderer:
    def draw_cube(self, w, h, d):
        glPushMatrix()
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

    def _draw_digit(self, digit, scale, on_color, off_color):
        """Draw a single 7-segment digit at the current matrix origin."""
        segs = SEGMENTS.get(digit, SEGMENTS[8])
        glPushMatrix()
        glScalef(scale, scale, 1.0)
        for i, (x0, y0, x1, y1) in enumerate(SEG_QUADS):
            if segs[i]:
                glColor3f(*on_color)
            else:
                glColor3f(*off_color)
            glBegin(GL_QUADS)
            glVertex3f(x0, y0, 0)
            glVertex3f(x1, y0, 0)
            glVertex3f(x1, y1, 0)
            glVertex3f(x0, y1, 0)
            glEnd()
        glPopMatrix()

    def _draw_colon(self, scale, color):
        """Draw the two dots of a colon separator."""
        glColor3f(*color)
        s = scale * SEG_THICKNESS * 1.4
        glPushMatrix()
        glScalef(scale, scale, 1.0)
        # Top dot
        glPushMatrix()
        glTranslatef(1.0, 7.0, 0)
        glScalef(s, s, 1)
        glutSolidCube(1.0)
        glPopMatrix()
        # Bottom dot
        glPushMatrix()
        glTranslatef(1.0, 3.0, 0)
        glScalef(s, s, 1)
        glutSolidCube(1.0)
        glPopMatrix()
        glPopMatrix()

    def _draw_display(self, h, m, s, blink_colon):
        """
        Draws HH:MM:SS in 7-segment style.
        All geometry is in a local flat XY plane (Z=0).
        Caller positions via glTranslatef before calling this.
        """
        DIGIT_SCALE = 1.0  # each digit cell is 6*scale wide, 10*scale tall
        DIGIT_W = 6.0  # width of one digit in local units
        COLON_W = 3.0  # width reserved for colon
        GAP = 0.6  # gap between digits in a pair
        PAIR_GAP = COLON_W  # gap between pairs (occupied by colon)

        on_color = (0.15, 0.95, 0.35)  # bright green
        off_color = (0.04, 0.14, 0.06)  # very dim green (ghost segments)
        col_color = on_color if blink_colon else off_color

        digits = [h // 10, h % 10, m // 10, m % 10, s // 10, s % 10]

        # Layout: d0 d1 : d2 d3 : d4 d5
        # X positions of each digit's left edge
        x_positions = []
        x = 0.0
        for pair in range(3):
            x_positions.append(x)
            x += DIGIT_W + GAP
            x_positions.append(x)
            x += DIGIT_W
            if pair < 2:
                x += PAIR_GAP  # room for colon

        for i, digit in enumerate(digits):
            glPushMatrix()
            glTranslatef(x_positions[i], 0, 0)
            self._draw_digit(digit, DIGIT_SCALE, on_color, off_color)
            glPopMatrix()

        # Colons at the gaps between pairs
        colon_x1 = x_positions[1] + DIGIT_W + GAP * 0.5
        colon_x2 = x_positions[3] + DIGIT_W + GAP * 0.5
        for cx in [colon_x1, colon_x2]:
            glPushMatrix()
            glTranslatef(cx, 0, 0)
            self._draw_colon(DIGIT_SCALE, col_color)
            glPopMatrix()

    def _draw_casing(self):
        """
        Black casing box behind the display.
        Total display width is ~43.8, so casing needs to be wider (48.0)
        and centered at X = 21.9 to prevent digits from spilling over.
        """
        # Back panel
        glColor3f(0.06, 0.06, 0.06)
        glPushMatrix()
        glTranslatef(21.9, 5.0, -0.5)
        self.draw_cube(48.0, 14.0, 1.2)
        glPopMatrix()

        # Red LED power dot (top right corner of casing)
        glColor3f(0.9, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(44.0, 10.8, 0.1)
        self.draw_cube(1.0, 1.0, 0.4)
        glPopMatrix()

    def render(self, desk_transform, state):
        if not getattr(state, "is_visible", True):
            return

        import math
        import time as _t

        h, m, s = state.get_display()

        # Colon blinks once per second while timer is running
        blink_colon = state.is_running and (int(_t.time()) % 2 == 0)

        glPushMatrix()
        glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)
        glRotatef(desk_transform.yaw, 0, 0, 1)

        # Shifted left (X=14 instead of 22)
        # Shifted slightly down the desk toward the player (Y=-15 instead of -10)
        # Calculated exact Z placement to sit perfectly flush with the desk (Z=41.8)
        glTranslatef(14, -10, 42)
        glRotatef(90, 1, 0, 0)  # lay flat → stand upright, face toward -Y

        # Scaled down a little bit more
        glScalef(0.4, 0.4, 0.4)

        self._draw_casing()

        # Shift origin so display is centred inside the casing
        glTranslatef(0.5, 0.5, 0.2)
        self._draw_display(h, m, s, blink_colon)

        glPopMatrix()
