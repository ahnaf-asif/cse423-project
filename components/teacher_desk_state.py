from components.chair_state import ChairState
from components.collider import Collider
from components.laptop_state import LaptopState
from components.timer_state import TimerState
from core.component import Component


class TeacherDeskState(Component):
    def __init__(self):
        # Initialize the nested states for the teacher's items
        self.laptop = LaptopState()
        self.timer = TimerState()
        self.chair = ChairState()

        # Teacher desk is 80x50. Chair is 26x26 at (0, -30).
        # Bounds: Min Y = -43, Max Y = 25.
        # Total depth = 68. Center Y = (25-43)/2 = -9.
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
