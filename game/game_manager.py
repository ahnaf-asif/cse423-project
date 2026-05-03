import math
import os
import random
import sys

from components.laptop_state import LaptopState
from components.student_anim_state import StudentAnimState
from components.student_desk_state import StudentDeskState
from components.teacher_desk_state import TeacherDeskState
from components.transform import Transform
from core.entity import Entity
from game.anomaly_manager import AnomalyManager
from game.baseline_manager import BaselineManager
from game.laptop_renderer import LaptopRenderer
from game.student_desk_renderer import StudentDeskRenderer
from game.student_renderer import StudentRenderer
from game.teacher_desk_renderer import TeacherDeskRenderer
from game.ui_renderer import UIRenderer
from OpenGL.GL import *
from OpenGL.GLUT import *


class GameManager:
    # State Constants
    STATE_MENU = 0
    STATE_RULES = 1
    STATE_PLAYING = 2
    STATE_PAUSE = 3
    STATE_VICTORY = 4

    def __init__(self):
        self.entities = []
        self.frame_count = 0.0
        self.state = self.STATE_MENU
        self.previous_state = self.STATE_MENU
        
        # UI & Gameplay Managers
        self.ui_renderer = UIRenderer()
        self.baseline_manager = BaselineManager()
        self.anomaly_manager = AnomalyManager()
        
        self.target_student = None # The student the player is currently looking at
        self.target_desk_entity = None # Keep track of the desk for interaction
        
        self.objective_text = "OBJECTIVE: Start the exam at your desk."
        self.is_exam_started = False
        self.rounds_completed = 0 # Track actual gameplay rounds
        self.is_round_active = False # Tracks if an anomaly roll has occurred this session
        
        self.disqualified_students = [] # List of (desk_id, anim_state) tuples
        self.exam_time_left = 60 # Minutes
        
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
        self.teacher_desk_renderer = TeacherDeskRenderer()

        # Player (Invigilator) - Start at front facing students
        self.player = Entity("Player")
        # Positioned in the gap between teacher and students
        start_transform = Transform(0, 255, 100)
        start_transform.yaw = 180
        self.player.add_component("Transform", start_transform)
        self.add_entity(self.player)

    def add_entity(self, entity):
        self.entities.append(entity)

    def setup_classroom(self):
        # 1. Define Identity Pools
        names = [
            "Abul", "Kuddus", "Kashem", "Mokless", "Boltu", "Poltu",
            "Hablu", "Gablu", "Jobbar", "Motin", "Solim", "Kolim",
            "Sokina", "Jorina", " Morjina", "Kulsum"
        ]
        random.shuffle(names)

        colors = [
            (0.8, 0.2, 0.2), (0.2, 0.8, 0.2), (0.2, 0.2, 0.8), # R, G, B
            (0.8, 0.8, 0.2), (0.8, 0.2, 0.8), (0.2, 0.8, 0.8), # Y, M, C
            (0.5, 0.5, 0.5), (0.9, 0.5, 0.1), (0.5, 0.1, 0.9), # Grey, Orange, Purple
            (0.1, 0.9, 0.5), (0.4, 0.2, 0.1), (0.1, 0.4, 0.2)  # Teal, Brown, Forest
        ]
        random.shuffle(colors)

        # 2. Determine which desks are occupied (12 out of 16)
        desk_indices = list(range(16))
        occupied_indices = random.sample(desk_indices, 12)

        # 3. Create 4x4 Student Desks
        start_x, start_y = -300, -430
        spacing_x, spacing_y = 200, 180

        student_count = 0
        for i in range(16):
            row = i // 4
            col = i % 4

            desk_id = f"StudentDesk_{row}_{col}"
            desk = Entity(desk_id)
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            desk.add_component("Transform", Transform(x, y, 0))
            
            desk_state = StudentDeskState()
            desk.add_component("StudentDeskState", desk_state)

            if i in occupied_indices:
                name = names[student_count]
                id_num = f"22-4{random.randint(100, 999)}-3"
                color = colors[student_count % len(colors)]

                # Add Student to the desk
                student_state = StudentAnimState(name, id_num, color)
                student_state.is_sitting = True
                student_state.is_writing = False # Not writing yet
                desk.add_component("AnimState", student_state)
                
                # Randomize desk items for students
                desk_state.exam_sheet.is_visible = True
                desk_state.calculator.is_visible = random.choice([True, False])
                desk_state.smartphone.is_visible = False # Anomaly only
                
                student_count += 1
            else:
                # Clear items from empty desks
                desk_state.exam_sheet.is_visible = False
                desk_state.calculator.is_visible = False
                desk_state.smartphone.is_visible = False

            self.add_entity(desk)

        # --- 4. Create Teacher's Desk ---

        teacher_desk = Entity("TeacherDesk")
        # Positioned at y=400 to allow space for a chair against the wall (y=600)
        teacher_transform = Transform(0, 400, 0)
        teacher_transform.yaw = 180
        teacher_desk.add_component("Transform", teacher_transform)
        teacher_desk.add_component("TeacherDeskState", TeacherDeskState())
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

        elif self.state == self.STATE_VICTORY:
            btn_w, btn_h = 200, 50
            if (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 140 <= ui_y <= height/2 - 140 + btn_h):
                self.state = self.STATE_MENU
                # Reset for next game
                self.exam_time_left = 60
                self.rounds_completed = 0
                self.is_exam_started = False
                self._reset_classroom()

    def interact(self):
        if self.state != self.STATE_PLAYING:
            return
        
        # Check proximity to Teacher's Desk for laptop
        player_transform = self.player.get_component("Transform")
        for entity in self.entities:
            teacher_desk_state = entity.get_component("TeacherDeskState")
            if teacher_desk_state:
                desk_transform = entity.get_component("Transform")
                dist = math.hypot(player_transform.x - desk_transform.x, player_transform.y - desk_transform.y)
                if dist < 160.0: # INTERACT_RANGE
                    if not self.is_exam_started:
                        # First time using laptop -> Start Exam
                        self.baseline_manager.capture_classroom(self.entities)
                        self.is_exam_started = True
                        self.objective_text = "OBJECTIVE: Monitor the students. Catch any cheaters."
                        
                        # Everyone starts writing
                        for e in self.entities:
                            anim = e.get_component("AnimState")
                            if anim: anim.is_writing = True
                    
                    teacher_desk_state.laptop.start_work()
                    return

    def inspect_student(self):
        if not self.target_desk_entity:
            return
        print(f"[GameManager] Inspecting {self.target_student.name}")
        # TODO: Implement inspection logic

    def disqualify_student(self):
        if not self.target_desk_entity or not self.target_student:
            return
        
        print(f"[GameManager] Disqualifying {self.target_student.name} from {self.target_desk_entity.id}")
        
        # Store for history/restoration and remove from room
        self.disqualified_students.append((self.target_desk_entity.id, self.target_student))
        del self.target_desk_entity.components["AnimState"]
        
        self.target_student = None
        self.target_desk_entity = None

    def dismiss_laptop(self):
        if self.state != self.STATE_PLAYING:
            return
        
        for entity in self.entities:
            teacher_desk_state = entity.get_component("TeacherDeskState")
            if teacher_desk_state:
                laptop = teacher_desk_state.laptop
                if laptop.is_being_used and laptop.is_work_done:
                    # EVALUATION PHASE (Before dismissing)
                    if self.is_exam_started:
                        self._evaluate_round()

                    # Roll for NEXT round anomaly
                    self._trigger_round_roll()
                    
                    laptop.finish()
                    self.is_round_active = False # Reset for next session
                    return

    def update(self, dt, keys):
        if self.state != self.STATE_PLAYING:
            return

        self.frame_count += dt * 60.0

        # Update all entities (like timer and laptop in teacher desk)
        for entity in self.entities:
            teacher_desk_state = entity.get_component("TeacherDeskState")
            if teacher_desk_state:
                teacher_desk_state.update(dt)

        # Player Movement
        player_transform = self.player.get_component("Transform")
        
        # Check if laptop is being used - if so, freeze movement
        is_using_laptop = False
        for entity in self.entities:
            teacher_desk_state = entity.get_component("TeacherDeskState")
            if teacher_desk_state and teacher_desk_state.laptop.is_being_used:
                is_using_laptop = True
                break

        if not is_using_laptop:
            # First Person Movement
            MOVE_SPEED = 200.0
            ROTATE_SPEED = 120.0
            
            yaw_r = math.radians(player_transform.yaw)
            pitch_r = math.radians(player_transform.pitch)
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

            # --- Student Targeting Logic ---
            self.target_student = None
            self.target_desk_entity = None # Keep track of the desk for interaction
            best_dot = 0.95 # Slightly wider tolerance
            INTERACT_RANGE = 120.0
            
            # Look vector
            lx = math.sin(yaw_r) * math.cos(pitch_r)
            ly = math.cos(yaw_r) * math.cos(pitch_r)
            lz = math.sin(pitch_r)

            for entity in self.entities:
                anim = entity.get_component("AnimState")
                if anim:
                    et = entity.get_component("Transform")
                    # Check distance first
                    dist_to_desk = math.hypot(player_transform.x - et.x, player_transform.y - et.y)
                    if dist_to_desk < INTERACT_RANGE:
                        # Target the student's head
                        ex, ey, ez = et.x, et.y - 25, 80 
                        vx, vy, vz = ex - player_transform.x, ey - player_transform.y, ez - player_transform.z
                        dist_to_head = math.sqrt(vx*vx + vy*vy + vz*vz)
                        if dist_to_head > 0:
                            vx /= dist_to_head; vy /= dist_to_head; vz /= dist_to_head
                            dot = lx*vx + ly*vy + lz*vz
                            if dot > best_dot:
                                best_dot = dot
                                self.target_student = anim
                                self.target_desk_entity = entity

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
        elif self.state == self.STATE_VICTORY:
            self.ui_renderer.render_victory(width, height)

    def _render_hud(self, width, height):
        # 0. Render Objective
        self._draw_objective(width, height)

        player_transform = self.player.get_component("Transform")
        
        # 1. Render Student Info & Prompts if looking at one nearby
        if self.target_student:
            self._draw_name_tag(width, height, self.target_student)
            self._draw_prompt(width, height, "[Q] Inspect  [F] Disqualify", y_offset=180)

        # 2. Check for interaction prompts and laptop takeover
        for entity in self.entities:
            teacher_desk_state = entity.get_component("TeacherDeskState")
            if teacher_desk_state:
                laptop = teacher_desk_state.laptop
                if laptop.is_being_used:
                    # Render the full-screen laptop HUD
                    self.laptop_renderer.render(entity.get_component("Transform"), laptop, width, height)
                else:
                    # Check for "Use Laptop" prompt
                    desk_transform = entity.get_component("Transform")
                    dist = math.hypot(player_transform.x - desk_transform.x, player_transform.y - desk_transform.y)
                    if dist < 160.0:
                        self._draw_prompt(width, height, "[E] Use Laptop")

    def _draw_objective(self, w, h):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

        # Subtle dark background for readability
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.4)
        glBegin(GL_QUADS)
        glVertex2f(20, h - 60); glVertex2f(500, h - 60)
        glVertex2f(500, h - 20); glVertex2f(20, h - 20)
        glEnd()
        glDisable(GL_BLEND)

        # Draw objective text
        glColor3f(1, 1, 0) # Yellow for emphasis
        glRasterPos2f(30, h - 45)
        for char in self.objective_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def _draw_name_tag(self, w, h, student):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

        # Draw plate
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.7)
        pw, ph = 300, 60
        px, py = w/2 - pw/2, h - 100
        glBegin(GL_QUADS)
        glVertex2f(px, py); glVertex2f(px + pw, py)
        glVertex2f(px + pw, py + ph); glVertex2f(px, py + ph)
        glEnd()
        glDisable(GL_BLEND)

        # Draw Name and ID
        glColor3f(1, 1, 1)
        name_text = f"NAME: {student.name}"
        id_text = f"ID: {student.id_number}"
        
        glRasterPos2f(px + 20, py + 35)
        for char in name_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
            
        glRasterPos2f(px + 20, py + 12)
        for char in id_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def _draw_prompt(self, w, h, text, y_offset=50):
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
        
        bw, bh = 250 if "Q" in text else 200, 40
        bx, by = w/2 - bw/2, y_offset
        glBegin(GL_QUADS)
        glVertex2f(bx, by); glVertex2f(bx + bw, by)
        glVertex2f(bx + bw, by + bh); glVertex2f(bx, by + bh)
        glEnd()
        glDisable(GL_BLEND)

        glColor3f(1, 1, 1)
        # Use simpler bitmap text for the prompt
        glRasterPos2f(bx + 20, by + 15)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def _render_room(self):
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

    def _render_3d_scene(self):
        self._render_room()

        # Route Entities
        for entity in self.entities:
            if entity.id == "Player":
                continue

            transform = entity.get_component("Transform")
            anim = entity.get_component("AnimState")
            student_desk = entity.get_component("StudentDeskState")
            teacher_desk = entity.get_component("TeacherDeskState")

            if transform and student_desk:
                self.student_desk_renderer.render(transform, student_desk)
            
            if transform and anim:
                self.student_renderer.render(transform, anim, self.frame_count)
            
            if transform and teacher_desk:
                self.teacher_desk_renderer.render(transform, teacher_desk)

    def _trigger_round_roll(self):
        self.is_round_active = True
        print("\n" + "="*40)
        print("   NEW ROUND: ANOMALY ROLL")
        print("="*40)
        
        if random.random() < 0.5:
            # Anomaly Occurs
            # choice = self.anomaly_manager.pick_anomaly() # TEMPORARILY FORCING ANOMALIES
            choice = random.choice(["SeatSwap", "ForgedID"])
            print(f"\n[Game] ROLL: ANOMALY SELECTED -> {choice} (FORCED FOR TESTING)")
            affected = self.anomaly_manager.apply_anomaly(choice, self.entities)
            if not affected:
                print("[Game] Roll failed (No eligible students). Room stays NORMAL.")
            else:
                print(f"[Game] Applied {choice} to: {[e.id for e in affected]}")
        else:
            print("\n[Game] ROLL: NO ANOMALY. Room stays NORMAL.")

        self._log_room_state("BASELINE (NORMAL)", is_baseline=True)
        self._log_room_state("CURRENT STATE")
        print("\n" + "="*40 + "\n")

    def _log_room_state(self, header, is_baseline=False):
        print(f"\n--- {header} ---")
        # Log in a grid format for better readability
        for row in range(4):
            line = []
            for col in range(4):
                desk_id = f"StudentDesk_{row}_{col}"
                if is_baseline:
                    snap = self.baseline_manager.snapshot.get(desk_id)
                    student = snap["anim_state"] if snap else None
                else:
                    # Find entity by id
                    desk_entity = next((e for e in self.entities if e.id == desk_id), None)
                    student = desk_entity.get_component("AnimState") if desk_entity else None
                
                name = student.name[:5] if student else "EMPTY"
                line.append(f"{desk_id[-3:]}: {name:5}")
            print(" | ".join(line))

    def _evaluate_round(self):
        """Checks if the player correctly identified all anomalies."""
        # The very first interaction just "Starts" the exam, no evaluation yet
        if self.rounds_completed == 0:
            print("[Game] Exam Initialized. No evaluation for Round 0.")
            self.rounds_completed += 1
            return

        print("\n--- EVALUATING ROUND ---")
        
        is_failure = False
        
        # 1. Check for missed anomalies (False Negatives)
        # An anomaly is only "missed" if there's still a student in the room who shouldn't be there or is wrong.
        for entity in self.entities:
            if "StudentDesk" in entity.id:
                anim = entity.get_component("AnimState")
                if anim: # ONLY check desks that still have students
                    if self.baseline_manager.is_desk_anomalous(entity):
                        print(f"[Evaluation] MISSED ANOMALY: Student {anim.name} at {entity.id} is anomalous!")
                        is_failure = True
                        break

        # 2. Check for innocent students disqualified (False Positives)
        if not is_failure:
            for desk_id, student in self.disqualified_students:
                # Reconstruct a temp entity to check against baseline
                temp_entity = Entity(desk_id)
                temp_entity.add_component("AnimState", student)
                # Find the actual desk to get its baseline items (calculator, sheet)
                actual_desk = next(e for e in self.entities if e.id == desk_id)
                temp_entity.add_component("StudentDeskState", actual_desk.get_component("StudentDeskState"))
                
                if not self.baseline_manager.is_desk_anomalous(temp_entity):
                    print(f"[Evaluation] FALSE ACCUSATION! {student.name} was innocent at {desk_id}.")
                    is_failure = True
                    break

        if is_failure:
            print("[Evaluation] PHASE FAILED. Resetting to 60 minutes.")
            self.exam_time_left = 60
            self._reset_classroom()
            self.rounds_completed = 1 # Keep it at 1 so next round evaluated
        else:
            print("[Evaluation] PHASE SUCCESS! -10 Minutes.")
            self.exam_time_left = max(0, self.exam_time_left - 10)
            self.rounds_completed += 1
            if self.exam_time_left == 0:
                print("!!! VICTORY !!!")
                self.state = self.STATE_VICTORY
        
        # Update physical clock (TimerState uses total_seconds)
        for entity in self.entities:
            tds = entity.get_component("TeacherDeskState")
            if tds:
                tds.timer.total_seconds = float(self.exam_time_left * 60)

    def _reset_classroom(self):
        """Restores the room to baseline and returns disqualified students."""
        print("[Game] Resetting classroom to baseline...")
        self.baseline_manager.restore_classroom(self.entities)
        self.disqualified_students = []
        
        # Ensure they are all writing again
        for e in self.entities:
            anim = e.get_component("AnimState")
            if anim: anim.is_writing = True
