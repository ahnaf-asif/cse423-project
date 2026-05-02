from core.component import Component


class SmartphoneState(Component):
    def __init__(self):
        self.is_visible = True
        self.is_being_inspected = False
