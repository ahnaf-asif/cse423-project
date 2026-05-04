import random

class BaseAnomaly:
    def __init__(self, name):
        self.name = name

    def get_eligible_entities(self, entities):
        raise NotImplementedError

    def apply(self, entities):
        raise NotImplementedError
