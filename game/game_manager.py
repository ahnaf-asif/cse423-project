import math
import os

from components.laptop_state import LaptopState
from components.student_anim_state import StudentAnimState
from components.student_desk_state import StudentDeskState
from components.transform import Transform
from core.entity import Entity
from game.laptop_renderer import LaptopRenderer
from game.student_desk_renderer import StudentDeskRenderer
from game.student_renderer import StudentRenderer
from game.ui_renderer import UIRenderer
from OpenGL.GL import *
from OpenGL.GLUT import *


class GameManager:
    # State Constants
    STATE_MENU = 0
    STATE_RULES = 1
    STATE_PLAYING = 2
    STATE_PAUSE = 3

    def __init__(self):
        self.entities = []
        self.frame_count = 0.0
        self.state = self.STATE_MENU
        self.previous_state = self.STATE_MENU
        
        # UI Renderer
        self.ui_renderer = UIRenderer()
        
        # Rules content based on GDD
        self.rules_pages = [
            [
                "PAGE 1: THE MISSION",
                "",
                "Welcome, Invigilator. Your duty is to oversee the final exam.",
                "",
                "• BALANCE YOUR WORK: You must complete tasks on your laptop.",
                "• WATCH THE ROOM: When working, your view is blocked. This is when students strike.",
                "• CATCH CHEATERS: Look for 'Anomalies'—anything that differs from the starting state of the room.",
                "• GOAL: Successfully manage the room until the 60-minute timer reaches 0."
            ],
            [
                "PAGE 2: THE ENVIRONMENT",
                "",
                "The classroom has a 4x4 grid of desks containing 12 students and 4 empty desks.",
                "",
                "STUDENT PROFILES:",
                "• Identity: Each student has a unique Name and ID Card.",
                "• Appearance: Pay attention to clothing colors.",
                "• Equipment: Standard items include a Pen, Exam Sheet, and sometimes a Calculator.",
                "• Memory is Key: Study the room at the start."
            ],
            [
                "PAGE 3: SPOTTING ANOMALIES",
                "",
                "Cheating manifests as physical or supernatural anomalies. Watch for:",
                "",
                "• POSITIONS: Students swapping seats or moving to empty desks.",
                "• ITEMS: Appearance of cheat sheets, missing pens, or swapped exam papers.",
                "• BIZARRE EVENTS: Keep an eye out for supernatural shifts in the environment.",
                "• LINGERERS: Disqualified students should be gone. Them reappearing is anamoly.",
                "• Or anything else that wasn't there at the start.", 
                "• NOTE: All ananomalies are considered 'Cheating' and must be disqualified."
            ],
            [
                "PAGE 4: THE GAMEPLAY LOOP",
                "",
                "1. INSPECT: Study the students carefully before starting the exam.",
                "2. WORK: Sit at the Teacher's Desk to begin. Your vision will be obscured.",
                "3. INVESTIGATE: Step away from the laptop to scan for changes.",
                "4. JUDGE: Disqualify those you suspect of cheating. If the room looks 'Clean,' take no action.",
                "5. REPEAT: Return to work and progress the clock."
            ],
            [
                "PAGE 5: DISCIPLINE & WIN CONDITIONS",
                "",
                "Your performance determines the timer:",
                "",
                "• SUCCESS: Identifying all cheaters correctly (and ignoring the innocent)",
                " On success, the timer counts down by 10 minutes",
                "• FAILURE: Falsely accusing a student or missing a cheater resets the clock to 60 minutes.",
                "• TOTAL RESET: On failure, all disqualified students return. The exam starts over. (Total Restart)",
                "• VICTORY: Reach 0 minutes to successfully complete your invigilation duty."
            ]
        ]
        self.current_rules_page = 0

        # Room dimensions (Bounding Box) - ENLARGED
        self.room_width = 1000
        self.room_depth = 1200
        self.wall_height = 200

        # Instantiate Renderers
        self.student_renderer = StudentRenderer()
        self.student_desk_renderer = StudentDeskRenderer()
        self.laptop_renderer = LaptopRenderer()

        # Player (Invigilator) - Start at front facing students
        self.player = Entity("Player")
        # Positioned in front of teacher's desk (y=450), facing students
        start_transform = Transform(0, 320, 100)
        start_transform.yaw = 180
        self.player.add_component("Transform", start_transform)
        self.add_entity(self.player)

    def add_entity(self, entity):
        self.entities.append(entity)

    def setup_classroom(self):
        # --- 1. Create 4x4 Student Desks ---
        # Shifted back so front row is at y=190
        start_x, start_y = -300, -350
        spacing_x, spacing_y = 200, 180

        for row in range(4):
            for col in range(4):
                desk = Entity(f"StudentDesk_{row}_{col}")
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                desk.add_component("Transform", Transform(x, y, 0))
                desk.add_component("StudentDeskState", StudentDeskState())
                self.add_entity(desk)

        # --- 2. Create Teacher's Desk ---
        teacher_desk = Entity("TeacherDesk")
        teacher_desk.add_component("Transform", Transform(0, 480, 0))
        teacher_desk.add_component("StudentDeskState", StudentDeskState())
        teacher_desk.add_component("LaptopState", LaptopState())
        self.add_entity(teacher_desk)

    def handle_mouse_click(self, button, state, x, y, width, height):
        if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
            return

        # UI Y is bottom-up, mouse Y is top-down
        ui_y = height - y

        if self.state == self.STATE_MENU:
            # Start Game Button: Center
            btn_w, btn_h = 200, 50
            if (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 <= ui_y <= height/2 + btn_h):
                self.previous_state = self.STATE_MENU
                self.state = self.STATE_RULES
                self.current_rules_page = 0
            # Exit Button
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 70 <= ui_y <= height/2 - 70 + btn_h):
                os._exit(0)

        elif self.state == self.STATE_PAUSE:
            btn_w, btn_h = 200, 50
            # Resume
            if (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 + 60 <= ui_y <= height/2 + 60 + btn_h):
                self.state = self.STATE_PLAYING
            # Show Rules
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 10 <= ui_y <= height/2 - 10 + btn_h):
                self.previous_state = self.STATE_PAUSE
                self.state = self.STATE_RULES
                self.current_rules_page = 0
            # Restart
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 80 <= ui_y <= height/2 - 80 + btn_h):
                self.state = self.STATE_MENU
            # Quit
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 150 <= ui_y <= height/2 - 150 + btn_h):
                os._exit(0)

        elif self.state == self.STATE_RULES:
            margin = 50
            btn_w, btn_h = 120, 40
            
            # Back Button
            if (margin <= x <= margin + btn_w) and (margin <= ui_y <= margin + btn_h):
                if self.current_rules_page > 0: self.current_rules_page -= 1
                else:
                    self.state = self.previous_state
            
            # Next Button
            elif (width - margin - btn_w <= x <= width - margin) and (margin <= ui_y <= margin + btn_h):
                if self.current_rules_page < len(self.rules_pages) - 1:
                    self.current_rules_page += 1
            
            # Start/Resume Button (Always clickable)
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (margin <= ui_y <= margin + btn_h):
                self.state = self.STATE_PLAYING

    def interact(self):
        if self.state != self.STATE_PLAYING:
            return
        
        # Check proximity to Teacher's Desk for laptop
        player_transform = self.player.get_component("Transform")
        for entity in self.entities:
            laptop_state = entity.get_component("LaptopState")
            if laptop_state:
                desk_transform = entity.get_component("Transform")
                dist = math.hypot(player_transform.x - desk_transform.x, player_transform.y - desk_transform.y)
                if dist < 100.0: # INTERACT_RANGE
                    laptop_state.start_work()
                    return

    def dismiss_laptop(self):
        if self.state != self.STATE_PLAYING:
            return
        
        for entity in self.entities:
            laptop_state = entity.get_component("LaptopState")
            if laptop_state and laptop_state.is_being_used and laptop_state.is_work_done:
                laptop_state.finish()
                return

    def update(self, dt, keys):
        if self.state != self.STATE_PLAYING:
            return

        self.frame_count += dt * 60.0

        # Update all entities (like laptop timer)
        for entity in self.entities:
            laptop_state = entity.get_component("LaptopState")
            if laptop_state:
                laptop_state.update(dt)

        # Player Movement
        player_transform = self.player.get_component("Transform")
        
        # Check if any laptop is being used - if so, freeze movement
        is_using_laptop = any(e.get_component("LaptopState").is_being_used 
                             for e in self.entities if e.get_component("LaptopState"))

        if not is_using_laptop:
            # First Person Movement
            MOVE_SPEED = 200.0
            ROTATE_SPEED = 120.0
            
            yaw_r = math.radians(player_transform.yaw)
            fwd_x = math.sin(yaw_r)
            fwd_y = math.cos(yaw_r)
            right_x = math.cos(yaw_r)
            right_y = -math.sin(yaw_r)

            if keys.get(b"w"):
                player_transform.x += fwd_x * MOVE_SPEED * dt
                player_transform.y += fwd_y * MOVE_SPEED * dt
            if keys.get(b"s"):
                player_transform.x -= fwd_x * MOVE_SPEED * dt
                player_transform.y -= fwd_y * MOVE_SPEED * dt
            if keys.get(b"a"):
                player_transform.x -= right_x * MOVE_SPEED * dt
                player_transform.y -= right_y * MOVE_SPEED * dt
            if keys.get(b"d"):
                player_transform.x += right_x * MOVE_SPEED * dt
                player_transform.y += right_y * MOVE_SPEED * dt

            if keys.get("left"):
                player_transform.yaw -= ROTATE_SPEED * dt
            if keys.get("right"):
                player_transform.yaw += ROTATE_SPEED * dt
            if keys.get("up"):
                player_transform.pitch = min(player_transform.pitch + ROTATE_SPEED * dt, 80.0)
            if keys.get("down"):
                player_transform.pitch = max(player_transform.pitch - ROTATE_SPEED * dt, -80.0)

            # --- Enforce Bounding Box (Room Boundaries) ---
            margin = 30
            half_w = self.room_width / 2 - margin
            half_d = self.room_depth / 2 - margin

            if player_transform.x < -half_w: player_transform.x = -half_w
            if player_transform.x > half_w: player_transform.x = half_w
            if player_transform.y < -half_d: player_transform.y = -half_d
            if player_transform.y > half_d: player_transform.y = half_d

    def render(self, width, height):
        if self.state == self.STATE_MENU:
            self.ui_renderer.render_menu(width, height)
        elif self.state == self.STATE_RULES:
            label = "Resume" if self.previous_state == self.STATE_PAUSE else "Start"
            self.ui_renderer.render_rules(width, height, self.rules_pages[self.current_rules_page], self.current_rules_page, len(self.rules_pages), label)
        elif self.state == self.STATE_PAUSE:
            self._render_3d_scene()
            self.ui_renderer.render_pause_menu(width, height)
        elif self.state == self.STATE_PLAYING:
            self._render_3d_scene()
            self._render_hud(width, height)

    def _render_hud(self, width, height):
        player_transform = self.player.get_component("Transform")
        
        # Check for interaction prompts
        for entity in self.entities:
            laptop_state = entity.get_component("LaptopState")
            if laptop_state:
                if laptop_state.is_being_used:
                    # The laptop renderer handles its own full-screen HUD
                    self.laptop_renderer.render(entity.get_component("Transform"), laptop_state)
                else:
                    desk_transform = entity.get_component("Transform")
                    dist = math.hypot(player_transform.x - desk_transform.x, player_transform.y - desk_transform.y)
                    if dist < 100.0:
                        self._draw_prompt(width, height, "[E] Use Laptop")

    def _draw_prompt(self, w, h, text):
        # Set up 2D overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

        # Draw a simple box and text for the prompt
        glColor4f(0, 0, 0, 0.6)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        bw, bh = 200, 40
        bx, by = w/2 - bw/2, 50
        glBegin(GL_QUADS)
        glVertex2f(bx, by); glVertex2f(bx + bw, by)
        glVertex2f(bx + bw, by + bh); glVertex2f(bx, by + bh)
        glEnd()
        glDisable(GL_BLEND)

        glColor3f(1, 1, 1)
        # Use simpler bitmap text for the prompt
        glRasterPos2f(bx + 40, by + 15)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def _render_3d_scene(self):
        # Draw Floor
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-self.room_width/2, self.room_depth/2, 0)
        glVertex3f(self.room_width/2, self.room_depth/2, 0)
        glVertex3f(self.room_width/2, -self.room_depth/2, 0)
        glVertex3f(-self.room_width/2, -self.room_depth/2, 0)
        glEnd()

        # Draw Roof
        glColor3f(0.4, 0.4, 0.4)
        glBegin(GL_QUADS)
        glVertex3f(-self.room_width/2, self.room_depth/2, self.wall_height)
        glVertex3f(self.room_width/2, self.room_depth/2, self.wall_height)
        glVertex3f(self.room_width/2, -self.room_depth/2, self.wall_height)
        glVertex3f(-self.room_width/2, -self.room_depth/2, self.wall_height)
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

        # Corner Shadows
        glColor3f(0.1, 0.1, 0.1)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        for x in [-half_w, half_w]:
            for y in [-half_d, half_d]:
                glVertex3f(x, y, 0)
                glVertex3f(x, y, h)
        glEnd()

        # Draw Board
        glColor3f(0.1, 0.15, 0.1)
        glBegin(GL_QUADS)
        glVertex3f(-250, half_d - 1, 50)
        glVertex3f(250, half_d - 1, 50)
        glVertex3f(250, half_d - 1, 150)
        glVertex3f(-250, half_d - 1, 150)
        glEnd()

        # Draw Grid
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_LINES)
        for i in range(int(-half_w), int(half_w) + 1, 50):
            glVertex3f(i, -half_d, 0.5)
            glVertex3f(i, half_d, 0.5)
        for i in range(int(-half_d), int(half_d) + 1, 50):
            glVertex3f(-half_w, i, 0.5)
            glVertex3f(half_w, i, 0.5)
        glEnd()

        # Route Entities
        for entity in self.entities:
            if entity.id == "Player":
                continue

            transform = entity.get_component("Transform")
            anim = entity.get_component("AnimState")
            student_desk = entity.get_component("StudentDeskState")
            laptop = entity.get_component("LaptopState")

            if transform and anim:
                self.student_renderer.render(transform, anim, self.frame_count)
            elif transform and student_desk:
                self.student_desk_renderer.render(transform, student_desk)
            
            # Draw laptop on desk if present
            if transform and laptop:
                self.laptop_renderer.render(transform, laptop)
