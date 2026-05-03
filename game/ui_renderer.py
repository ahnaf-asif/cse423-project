from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class UIRenderer:
    def __init__(self):
        pass

    def _set_ortho(self, w, h):
        glDisable(GL_DEPTH_TEST)  # Ensure UI is always on top
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(1, 1, 1) # Reset color to white

    def _unset_ortho(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST) # Re-enable for 3D

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(font, ord(char))

    def draw_button(self, x, y, w, h, text, is_disabled=False):
        if is_disabled:
            glColor3f(0.3, 0.3, 0.3)
        else:
            glColor3f(0.4, 0.4, 0.4)
            
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

        glColor3f(1, 1, 1)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

        # Center text in button
        text_w = len(text) * 9 # Rough estimation for Helvetica 18
        self.draw_text(x + (w - text_w) / 2, y + (h - 15) / 2, text)

    def render_menu(self, w, h):
        self._set_ortho(w, h)
        
        # Background
        glColor3f(0.1, 0.1, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(w, 0); glVertex2f(w, h); glVertex2f(0, h)
        glEnd()

        # Title
        glColor3f(1, 1, 1)
        title = "NOKOL AR HOBE NA!"
        self.draw_text(w/2 - 100, h * 0.7, title, GLUT_BITMAP_TIMES_ROMAN_24)

        # Buttons (Responsive: Centered)
        btn_w, btn_h = 200, 50
        self.draw_button(w/2 - btn_w/2, h/2, btn_w, btn_h, "Start Game")
        self.draw_button(w/2 - btn_w/2, h/2 - 70, btn_w, btn_h, "Exit")

        self._unset_ortho()

    def render_pause_menu(self, w, h):
        self._set_ortho(w, h)
        
        # Semi-transparent overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.6)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(w, 0); glVertex2f(w, h); glVertex2f(0, h)
        glEnd()
        glDisable(GL_BLEND)

        # Title
        glColor3f(1, 1, 1)
        self.draw_text(w/2 - 60, h * 0.7, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)

        # Buttons
        btn_w, btn_h = 200, 50
        self.draw_button(w/2 - btn_w/2, h/2 + 60, btn_w, btn_h, "Resume")
        self.draw_button(w/2 - btn_w/2, h/2 - 10, btn_w, btn_h, "Show Rules")
        self.draw_button(w/2 - btn_w/2, h/2 - 80, btn_w, btn_h, "Restart")
        self.draw_button(w/2 - btn_w/2, h/2 - 150, btn_w, btn_h, "Quit")

        self._unset_ortho()

    def render_rules(self, w, h, page_lines, page_idx, total_pages, start_button_label="Start"):
        self._set_ortho(w, h)
        
        # Background
        glColor3f(0.1, 0.1, 0.15)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(w, 0); glVertex2f(w, h); glVertex2f(0, h)
        glEnd()

        # Rules Box
        margin = 50
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(margin, margin + 80); glVertex2f(w - margin, margin + 80)
        glVertex2f(w - margin, h - margin); glVertex2f(margin, h - margin)
        glEnd()

        # Text lines
        glColor3f(1, 1, 1)
        y_start = h - margin - 50
        for i, line in enumerate(page_lines):
            self.draw_text(margin + 30, y_start - i * 30, line)

        # Bottom Buttons
        btn_w, btn_h = 120, 40
        margin = 50
        
        # Back Button (Left)
        self.draw_button(margin, margin, btn_w, btn_h, "Back")
        
        # Start/Resume Button (Center) - Always visible
        self.draw_button(w/2 - btn_w/2, margin, btn_w, btn_h, start_button_label)

        # Next Button (Right) - Only if not on last page
        if page_idx < total_pages - 1:
            self.draw_button(w - margin - btn_w, margin, btn_w, btn_h, "Next")

        self._unset_ortho()

    def render_victory(self, w, h):
        self._set_ortho(w, h)
        
        # Golden/Green Background
        glColor3f(0.1, 0.3, 0.1)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(w, 0); glVertex2f(w, h); glVertex2f(0, h)
        glEnd()

        # Victory Message
        glColor3f(1, 1, 0)
        self.draw_text(w/2 - 120, h/2 + 20, "CONGRATULATIONS!", GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(1, 1, 1)
        self.draw_text(w/2 - 150, h/2 - 20, "You successfully managed the exam!", GLUT_BITMAP_HELVETICA_18)
        self.draw_text(w/2 - 100, h/2 - 60, "Final Time: 00:00", GLUT_BITMAP_HELVETICA_18)

        # Main Menu Button
        btn_w, btn_h = 200, 50
        self.draw_button(w/2 - btn_w/2, h/2 - 140, btn_w, btn_h, "Main Menu")

        self._unset_ortho()
