class Entity:
    """A blank container that holds components."""

    def __init__(self, entity_id):
        self.id = entity_id
        self.components = {}

    def add_component(self, name, component):
        self.components[name] = component

    def get_component(self, name):
        return self.components.get(name)
