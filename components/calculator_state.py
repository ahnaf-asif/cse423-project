from core.component import Component


class CalculatorState(Component):
    def __init__(self):
        self.is_visible = False
        self.is_being_inspected = False
