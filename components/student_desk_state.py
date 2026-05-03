from core.component import Component

from .calculator_state import CalculatorState
from .chair_state import ChairState
from .cheatsheet_state import CheatsheetState
from .collider import Collider
from .exam_sheet_state import ExamSheetState
from .smartphone_state import SmartphoneState


class StudentDeskState(Component):
    def __init__(self):
        self.exam_sheet = ExamSheetState()
        self.calculator = CalculatorState()
        self.smartphone = SmartphoneState()
        self.cheatsheet = CheatsheetState()
        self.chair = ChairState()

        # Desk is 70x40. Chair is 26x26 at (0, -25).
        # We can use two colliders or one that covers both.
        # For simplicity and performance, a single bounding box for the whole unit:
        # Min Y: -25 - 13 = -38
        # Max Y: 20
        # Total Depth = 58. Center Y = (20 - 38)/2 = -9.
        self.collider = Collider(width=70, depth=58, offset_x=0, offset_y=-9)

    def get_collider(self):
        return self.collider
