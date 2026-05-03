class Entity:
    """A blank container that holds components."""

    def __init__(self, entity_id):
        self.id = entity_id
        self.components = {}

    def add_component(self, name, component):
        self.components[name] = component

    def get_component(self, name):
        return self.components.get(name)

    def get_collider(self):
        """Helper to find a collider in any of the entity's components."""
        for comp in self.components.values():
            if hasattr(comp, "get_collider"):
                return comp.get_collider()
            if hasattr(comp, "collider"):
                return comp.collider
        return None
