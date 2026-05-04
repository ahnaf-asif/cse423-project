from components.chair_state import ChairState
from components.collider import Collider
from components.laptop_state import LaptopState
from components.timer_state import TimerState
from core.component import Component


class TeacherDeskState(Component):
    def __init__(self):
        self.laptop = LaptopState()
        self.timer = TimerState()
        self.chair = ChairState()
        self.collider = Collider(width=80, depth=68, offset_x=0, offset_y=-9)

    def get_collider(self):
        return self.collider

    def update(self, dt):
        # Pass the delta time down to the timer so its internal clock keeps running
        if hasattr(self.timer, "update"):
            self.timer.update(dt)

        # Pass update to laptop if it has an active screen or animations
        if hasattr(self.laptop, "update"):
            self.laptop.update(dt)
