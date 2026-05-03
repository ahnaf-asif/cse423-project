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

        # Room dimensions (Bounding Box) - ENLARGED
        self.room_width = 1000
        self.room_depth = 1200
        self.wall_height = 200

        # Instantiate Renderers
        self.student_renderer = StudentRenderer()
        self.student_desk_renderer = StudentDeskRenderer()

        # The "main" student we control
        self.test_student = None

    def add_entity(self, entity):
        self.entities.append(entity)
        if entity.id == "Student_Main":
            self.test_student = entity

    def setup_classroom(self):
        # --- 1. Create the Main Student ---
        student = Entity("Student_Main")
        student.add_component("Transform", Transform(0, -400, 40))
        student.add_component("AnimState", StudentAnimState())
        self.add_entity(student)

        # --- 2. Create 4x4 Student Desks --- MORE SPACIOUS
        start_x, start_y = -300, -200
        spacing_x, spacing_y = 200, 180

        for row in range(4):
            for col in range(4):
                desk = Entity(f"StudentDesk_{row}_{col}")
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                desk.add_component("Transform", Transform(x, y, 0))
                desk.add_component("StudentDeskState", StudentDeskState())
                self.add_entity(desk)

        # --- 3. Create Teacher's Desk ---
        teacher_desk = Entity("TeacherDesk")
        teacher_desk.add_component("Transform", Transform(0, 450, 0))
        teacher_desk.add_component("StudentDeskState", StudentDeskState())
        self.add_entity(teacher_desk)

    def toggle_state(self, state_name):
        if not self.test_student:
            return
        anim = self.test_student.get_component("AnimState")
        if not anim:
            return

        current_val = getattr(anim, state_name)
        setattr(anim, state_name, not current_val)

        if state_name == "is_sitting" and anim.is_sitting:
            anim.is_walking = False
        if state_name == "is_walking" and anim.is_walking:
            anim.is_sitting = False

    def update(self, dt, keys):
        self.frame_count += dt * 60.0

        if not self.test_student:
            return

        transform = self.test_student.get_component("Transform")
        anim = self.test_student.get_component("AnimState")

        if transform and anim:
            if anim.is_sitting:
                anim.is_walking = False
            else:
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

            # --- Enforce Bounding Box (Room Boundaries) ---
            margin = 20
            half_w = self.room_width / 2 - margin
            half_d = self.room_depth / 2 - margin

            if transform.x < -half_w: transform.x = -half_w
            if transform.x > half_w: transform.x = half_w
            if transform.y < -half_d: transform.y = -half_d
            if transform.y > half_d: transform.y = half_d

    def render(self):
        # Draw Floor
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-self.room_width/2, self.room_depth/2, 0)
        glVertex3f(self.room_width/2, self.room_depth/2, 0)
        glVertex3f(self.room_width/2, -self.room_depth/2, 0)
        glVertex3f(-self.room_width/2, -self.room_depth/2, 0)
        glEnd()

        # Draw Walls
        glColor3f(0.55, 0.55, 0.6)  # Light blueish gray
        half_w = self.room_width / 2
        half_d = self.room_depth / 2
        h = self.wall_height

        glBegin(GL_QUADS)
        # Front Wall
        glVertex3f(-half_w, half_d, 0); glVertex3f(half_w, half_d, 0)
        glVertex3f(half_w, half_d, h); glVertex3f(-half_w, half_d, h)
        # Back Wall
        glVertex3f(-half_w, -half_d, 0); glVertex3f(half_w, -half_d, 0)
        glVertex3f(half_w, -half_d, h); glVertex3f(-half_w, -half_d, h)
        # Left Wall
        glVertex3f(-half_w, -half_d, 0); glVertex3f(-half_w, half_d, 0)
        glVertex3f(-half_w, half_d, h); glVertex3f(-half_w, -half_d, h)
        # Right Wall
        glVertex3f(half_w, -half_d, 0); glVertex3f(half_w, half_d, 0)
        glVertex3f(half_w, half_d, h); glVertex3f(half_w, -half_d, h)
        glEnd()

        # Corner Shadows (Dark lines at the intersections)
        glColor3f(0.1, 0.1, 0.1)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        for x in [-half_w, half_w]:
            for y in [-half_d, half_d]:
                glVertex3f(x, y, 0)
                glVertex3f(x, y, h)
        glEnd()

        # Draw Board (on Front Wall)
        glColor3f(0.1, 0.15, 0.1)  # Darker green
        glBegin(GL_QUADS)
        glVertex3f(-250, half_d - 1, 50)
        glVertex3f(250, half_d - 1, 50)
        glVertex3f(250, half_d - 1, 150)
        glVertex3f(-250, half_d - 1, 150)
        glEnd()

        # Draw Grid (Optional, keep it small)
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_LINES)
        for i in range(int(-half_w), int(half_w) + 1, 50):
            glVertex3f(i, -half_d, 0.5)
            glVertex3f(i, half_d, 0.5)
        for i in range(int(-half_d), int(half_d) + 1, 50):
            glVertex3f(-half_w, i, 0.5)
            glVertex3f(half_w, i, 0.5)
        glEnd()

        # --- ROUTE ENTITIES TO THEIR PROPER RENDERERS ---
        for entity in self.entities:
            transform = entity.get_component("Transform")
            anim = entity.get_component("AnimState")
            student_desk = entity.get_component("StudentDeskState")

            if transform and anim:
                self.student_renderer.render(transform, anim, self.frame_count)
            elif transform and student_desk:
                self.student_desk_renderer.render(transform, student_desk)
