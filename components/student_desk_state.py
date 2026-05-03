from core.component import Component

from .calculator_state import CalculatorState
from .chair_state import ChairState
from .exam_sheet_state import ExamSheetState
from .smartphone_state import SmartphoneState


class StudentDeskState(Component):
    def __init__(self):
        self.exam_sheet = ExamSheetState()
        self.calculator = CalculatorState()
        self.smartphone = SmartphoneState()
        self.chair = ChairState()
