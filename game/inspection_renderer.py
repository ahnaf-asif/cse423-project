from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

from game.calculator_renderer import CalculatorRenderer
from game.smartphone_renderer import SmartphoneRenderer
from game.cheatsheet_renderer import CheatsheetRenderer
from game.exam_sheet_renderer import ExamSheetRenderer

class MockState:
    def __init__(self, is_visible=True, is_being_inspected=True):
        self.is_visible = is_visible
        self.is_being_inspected = is_being_inspected
        self.extra_logs = []

class InspectionRenderer:
    def __init__(self):
        # We'll map display names to internal identifiers
        self.available_items = [] # List of (display_name, internal_id)
        self.renderers = {
            "exam_sheet": ExamSheetRenderer(),
            "calculator": CalculatorRenderer(),
            "smartphone": SmartphoneRenderer(),
            "cheatsheet": CheatsheetRenderer()
        }

    def _prepare_menu(self, desk_state):
        """Populates the menu items based on what's visible on the desk."""
        self.available_items = []
        
        # Exam sheet is always there for students
        if desk_state.exam_sheet.is_visible:
            self.available_items.append(("Exam Sheet", "exam_sheet"))
        
        # Consolidate devices
        if desk_state.calculator.is_visible:
            self.available_items.append(("Device", "calculator"))
        elif desk_state.smartphone.is_visible:
            self.available_items.append(("Device", "smartphone"))
            
        if desk_state.cheatsheet.is_visible:
            self.available_items.append(("Additional Sheet", "cheatsheet"))

    def render_menu(self, width, height, selected_index, desk_state):
        """Renders a simple overlay menu for items to inspect."""
        self._prepare_menu(desk_state)
        
        # Simple overlay
        self._setup_2d(width, height)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.6)
        
        # Adjust box size based on item count
        menu_h = len(self.available_items) * 40 + 60
        glBegin(GL_QUADS)
        glVertex2f(width * 0.35, height/2 - menu_h/2)
        glVertex2f(width * 0.65, height/2 - menu_h/2)
        glVertex2f(width * 0.65, height/2 + menu_h/2)
        glVertex2f(width * 0.35, height/2 + menu_h/2)
        glEnd()
        glDisable(GL_BLEND)

        # Draw Menu Items
        for i, (display_name, internal_id) in enumerate(self.available_items):
            if i == selected_index:
                glColor3f(1, 1, 0)
                prefix = "> "
            else:
                glColor3f(1, 1, 1)
                prefix = "  "
            
            self._draw_text(width * 0.4, height/2 + menu_h/2 - 40 - i * 40, prefix + display_name, GLUT_BITMAP_HELVETICA_18)

        self._draw_text(width * 0.38, height/2 - menu_h/2 + 15, "[UP/DOWN] Nav  [ENTER] Inspect  [ESC] Exit", GLUT_BITMAP_HELVETICA_12)
        self._pop_2d()

    def render_item_inspection(self, width, height, item_index, desk_state):
        """Renders the existing entity-specific inspection HUD."""
        if item_index >= len(self.available_items):
            return

        display_name, internal_id = self.available_items[item_index]
        
        # Clear again because we are doing a full-screen takeover with a different FOV
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, width / height, 0.1, 1000)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        renderer = self.renderers[internal_id]
        # Get the actual state from the desk
        state = getattr(desk_state, internal_id)
        
        # Temporarily set inspected flag for the renderer to trigger HUD
        original_inspected = state.is_being_inspected
        state.is_being_inspected = True
        renderer.render(None, state)
        state.is_being_inspected = original_inspected

    def _setup_2d(self, w, h):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

    def _pop_2d(self):
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def _draw_text(self, x, y, text, font):
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(font, ord(char))
