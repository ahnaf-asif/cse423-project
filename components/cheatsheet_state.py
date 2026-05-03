from core.component import Component


class CheatsheetState(Component):
    def __init__(self):
        self.is_visible = False
        self.is_being_inspected = False
        self.content_type = "Math Formulas"  # Example attribute
