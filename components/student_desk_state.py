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

        self.collider = Collider(width=70, depth=58, offset_x=0, offset_y=-9)

    def get_collider(self):
        return self.collider
