from core.component import Component


class CheatsheetState(Component):
    def __init__(self):
        self.is_visible = True
        self.is_being_inspected = False

    def update(self, dt):
        pass

    def inspect(self):
        self.is_being_inspected = True

    def release(self):
        self.is_being_inspected = False
