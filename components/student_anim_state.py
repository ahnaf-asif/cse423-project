from core.component import Component


class StudentAnimState(Component):
    def __init__(self, name="Student", id_number="000-000", cloth_color=(0.5, 0.5, 0.5)):
        # Identity
        self.name = name
        self.id_number = id_number
        self.cloth_color = cloth_color
        self.pen_color = (1.0, 0.0, 0.0) # Default Red

        self.is_idle = True
        self.is_walking = False
        self.is_sitting = False
        self.is_dancing = False
        self.is_writing = False

        self.is_alien = False
        self.is_ghost = False
