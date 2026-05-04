from core.component import Component

from .collider import Collider


class ChairState(Component):
    def __init__(self):
        self.is_occupied = False
        self.collider = Collider(width=26, depth=26)

    def get_collider(self):
        return self.collider

    def toggle_sit(self):
        """Swaps the chair between empty and occupied."""
        self.is_occupied = not self.is_occupied
