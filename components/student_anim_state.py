from core.component import Component


class StudentAnimState(Component):
    def __init__(self):
        self.is_idle = True
        self.is_walking = False
        self.is_sitting = False
        self.is_dancing = False
        self.is_writing = False

        self.is_alien = False
        self.is_ghost = False
