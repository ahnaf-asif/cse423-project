from core.component import Component


class ChairState(Component):
    def __init__(self):
        self.is_occupied = False

    def update(self, dt):
        # The chair doesn't have a running clock or animation (yet),
        # so we just pass. But we keep the method for architectural consistency.
        pass

    def toggle_sit(self):
        """Swaps the chair between empty and occupied."""
        self.is_occupied = not self.is_occupied
