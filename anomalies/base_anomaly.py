import random

class BaseAnomaly:
    def __init__(self, name):
        self.name = name

    def get_eligible_entities(self, entities):
        """Returns a list of entities that this anomaly can be applied to."""
        raise NotImplementedError

    def apply(self, entities):
        """Applies the anomaly logic to selected entities. Returns affected entities."""
        raise NotImplementedError
