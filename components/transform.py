import math

from core.component import Component


class Transform(Component):
    def __init__(self, x=0, y=0, z=0, radius=20.0):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.yaw = 0
        self.pitch = 0

    def distance_to(self, other_x, other_y):
        """Calculates 2D distance to a point."""
        return math.hypot(self.x - other_x, self.y - other_y)

    def set_position(self, x, y, z=None):
        self.x = x
        self.y = y
        if z is not None:
            self.z = z
