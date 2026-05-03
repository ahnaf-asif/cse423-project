from components.laptop_state import LaptopState
from components.timer_state import TimerState
from core.component import Component


class TeacherDeskState(Component):
    def __init__(self):
        # Initialize the nested states for the teacher's items
        self.laptop = LaptopState()
        self.timer = TimerState()

    def update(self, dt):
        # Pass the delta time down to the timer so its internal clock keeps running
        if hasattr(self.timer, "update"):
            self.timer.update(dt)

        # Pass update to laptop if it has an active screen or animations
        if hasattr(self.laptop, "update"):
            self.laptop.update(dt)
