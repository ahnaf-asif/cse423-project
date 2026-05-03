from core.component import Component


class ExamSheetState(Component):
    def __init__(self, extra_logs=None):
        self.is_visible = True
        self.is_being_inspected = False
        # Store the custom list of strings, default to empty list if none provided
        self.extra_logs = extra_logs if extra_logs else []

    def update(self, dt):
        pass

    def inspect(self):
        self.is_being_inspected = True

    def release(self):
        self.is_being_inspected = False
