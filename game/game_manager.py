import math

from components.student_anim_state import StudentAnimState
from components.student_desk_state import StudentDeskState  # UPDATED IMPORT
from components.transform import Transform
from core.entity import Entity
from game.student_desk_renderer import StudentDeskRenderer  # UPDATED IMPORT
from game.student_renderer import StudentRenderer
from OpenGL.GL import *
from OpenGL.GLUT import *


class GameManager:
    def __init__(self):
        self.entities = []
        self.frame_count = 0.0

        # Instantiate Renderers
        self.student_renderer = StudentRenderer()
        self.student_desk_renderer = StudentDeskRenderer()  # UPDATED RENDERER

        # --- 1. Create the Test Student ---
        self.test_student = Entity("Student_01")
        self.test_student.add_component("Transform", Transform(0, 0, 40))

        anim = StudentAnimState()
        anim.is_idle = True
        self.test_student.add_component("AnimState", anim)
        self.entities.append(self.test_student)

        # --- 2. Create the Test Student Desk ---
        self.test_desk = Entity("StudentDesk_01")  # UPDATED ID
        # Position the desk directly in front of the student (+20 on the Y axis)
        self.test_desk.add_component("Transform", Transform(0, 30, 0))
        self.test_desk.add_component(
            "StudentDeskState", StudentDeskState()
        )  # UPDATED KEY

        desk_state = self.test_desk.get_component("StudentDeskState")
        desk_state.calculator.is_visible = False
        desk_state.smartphone.is_visible = True

        self.entities.append(self.test_desk)

    def toggle_state(self, state_name):
        anim = self.test_student.get_component("AnimState")

        current_val = getattr(anim, state_name)
        setattr(anim, state_name, not current_val)

        if state_name == "is_sitting" and anim.is_sitting:
            anim.is_walking = False
        if state_name == "is_walking" and anim.is_walking:
            anim.is_sitting = False

    def update(self, dt, keys):
        self.frame_count += dt * 60.0

        transform = self.test_student.get_component("Transform")
        anim = self.test_student.get_component("AnimState")

        if transform and anim:
            if anim.is_sitting:
                anim.is_walking = False
                return

            dx, dy = 0.0, 0.0
            if keys[b"w"]:
                dy += 1
            if keys[b"s"]:
                dy -= 1
            if keys[b"a"]:
                dx -= 1
            if keys[b"d"]:
                dx += 1

            if dx != 0 or dy != 0:
                length = math.hypot(dx, dy)
                dx /= length
                dy /= length

                speed = 150.0
                transform.x += dx * speed * dt
                transform.y += dy * speed * dt

                target_yaw = math.degrees(math.atan2(dx, dy))
                transform.yaw = -target_yaw

                anim.is_walking = True
            else:
                anim.is_walking = False

    def render(self):
        # Draw Floor
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-500, 500, 0)
        glVertex3f(500, 500, 0)
        glVertex3f(500, -500, 0)
        glVertex3f(-500, -500, 0)
        glEnd()

        # Draw Grid
        glColor3f(0.1, 0.1, 0.1)
        glBegin(GL_LINES)
        for i in range(-500, 500, 50):
            glVertex3f(i, -500, 1)
            glVertex3f(i, 500, 1)
            glVertex3f(-500, i, 1)
            glVertex3f(500, i, 1)
        glEnd()

        # --- ROUTE ENTITIES TO THEIR PROPER RENDERERS ---
        for entity in self.entities:
            transform = entity.get_component("Transform")

            # Extract data components
            anim = entity.get_component("AnimState")
            student_desk = entity.get_component("StudentDeskState")  # UPDATED KEY

            if transform and anim:
                self.student_renderer.render(transform, anim, self.frame_count)
            elif transform and student_desk:
                self.student_desk_renderer.render(
                    transform, student_desk
                )  # UPDATED CALL
