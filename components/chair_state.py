from core.component import Component

from .collider import Collider


class ChairState(Component):
    def __init__(self):
        self.is_occupied = False
        # Chair seat is 26x26. Backrest adds some visual depth but seat is the base.
        self.collider = Collider(width=26, depth=26)

    def get_collider(self):
        return self.collider

    def update(self, dt):
        # The chair doesn't have a running clock or animation (yet),
        # so we just pass. But we keep the method for architectural consistency.
        pass

    def toggle_sit(self):
        """Swaps the chair between empty and occupied."""
        self.is_occupied = not self.is_occupied
