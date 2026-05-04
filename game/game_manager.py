import copy
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
from game.inspection_renderer import InspectionRenderer
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
    STATE_INSPECTING = 5

    def __init__(self):
        self.entities = []
        self.frame_count = 0.0
        self.state = self.STATE_MENU
        self.previous_state = self.STATE_MENU
        
        # UI & Gameplay Managers
        self.ui_renderer = UIRenderer()
        self.baseline_manager = BaselineManager()
        self.anomaly_manager = AnomalyManager()
        self.inspection_renderer = InspectionRenderer()
        
        self.target_student = None 
        self.target_desk_entity = None 
        
        self.inspection_selected_index = 0
        self.is_viewing_item = False
        
        self.objective_text = "OBJECTIVE: Start the exam at your desk."
        self.is_exam_started = False
        self.rounds_completed = 0 
        self.is_round_active = False 
        self.consecutive_normals = 0 
        
        self.disqualified_students = [] 
        self.exam_time_left = 60 
        self.current_round_anomaly = None
        
        # Rules content based on GDD
        self.rules_pages = [
            ["PAGE 1: THE MISSION", "", "Welcome, Invigilator. Your duty is to oversee the final exam.", "", "• BALANCE YOUR WORK: You must complete tasks on your laptop.", "• WATCH THE ROOM: When working, your view is blocked. This is when students strike.", "• CATCH CHEATERS: Look for 'Anomalies'—anything that differs from the starting state of the room.", "• GOAL: Successfully manage the room until the 60-minute timer reaches 0."],
            ["PAGE 2: THE ENVIRONMENT", "", "The classroom has a 4x4 grid of desks containing 12 students and 4 empty desks.", "", "STUDENT PROFILES:", "• Identity: Each student has a unique Name and ID Card.", "• Appearance: Pay attention to clothing colors.", "• Equipment: Standard items include a Pen, Exam Sheet, and sometimes a Calculator.", "• Memory is Key: Study the room at the start."],
            ["PAGE 3: SPOTTING ANOMALIES", "", "Cheating manifests as physical or supernatural anomalies. Watch for:", "", "• POSITIONS: Students swapping seats or moving to empty desks.", "• ITEMS: Appearance of cheat sheets, missing pens, or swapped exam papers.", "• BIZARRE EVENTS: Keep an eye out for supernatural shifts in the environment.", "• LINGERERS: Disqualified students should be gone. Them reappearing is anamoly.", "• Or anything else that wasn't there at the start.", "• NOTE: All ananomalies are considered 'Cheating' and must be disqualified."],
            ["PAGE 4: THE GAMEPLAY LOOP", "", "1. INSPECT: Study the students carefully before starting the exam.", "2. WORK: Sit at the Teacher's Desk to begin. Your vision will be obscured.", "3. INVESTIGATE: Step away from the laptop to scan for changes.", "4. JUDGE: Disqualify those you suspect of cheating. If the room looks 'Clean,' take no action.", "5. REPEAT: Return to work and progress the clock."],
            ["PAGE 5: DISCIPLINE & WIN CONDITIONS", "", "Your performance determines the timer:", "", "• SUCCESS: Identifying all cheaters correctly (and ignoring the innocent)", " On success, the timer counts down by 10 minutes", "• FAILURE: Falsely accusing a student or missing a cheater resets the clock to 60 minutes.", "• TOTAL RESET: On failure, all disqualified students return. The exam starts over. (Total Restart)", "• VICTORY: Reach 0 minutes to successfully complete your invigilation duty."]
        ]
        self.current_rules_page = 0

        self.room_width, self.room_depth, self.wall_height = 1000, 1200, 200
        self.student_renderer = StudentRenderer()
        self.student_desk_renderer = StudentDeskRenderer()
        self.laptop_renderer = LaptopRenderer()
        self.teacher_desk_renderer = TeacherDeskRenderer()

        self.player = Entity("Player")
        start_transform = Transform(0, 255, 100)
        start_transform.yaw = 180
        start_transform.radius = 20.0
        self.player.add_component("Transform", start_transform)
        self.add_entity(self.player)

    def add_entity(self, entity):
        self.entities.append(entity)

    def setup_classroom(self):
        names = ["Abul", "Kuddus", "Kashem", "Mokless", "Boltu", "Poltu", "Hablu", "Gablu", "Jobbar", "Motin", "Solim", "Kolim", "Sokina", "Jorina", " Morjina", "Kulsum"]
        random.shuffle(names)
        colors = [(0.8, 0.2, 0.2), (0.2, 0.8, 0.2), (0.2, 0.2, 0.8), (0.8, 0.8, 0.2), (0.8, 0.2, 0.8), (0.2, 0.8, 0.8), (0.5, 0.5, 0.5), (0.9, 0.5, 0.1), (0.5, 0.1, 0.9), (0.1, 0.9, 0.5), (0.4, 0.2, 0.1), (0.1, 0.4, 0.2)]
        random.shuffle(colors)
        desk_indices = list(range(16))
        occupied_indices = random.sample(desk_indices, 12)
        start_x, start_y = -300, -430
        spacing_x, spacing_y = 200, 180
        student_count = 0
        for i in range(16):
            row, col = i // 4, i % 4
            desk = Entity(f"StudentDesk_{row}_{col}")
            desk.add_component("Transform", Transform(start_x + col * spacing_x, start_y + row * spacing_y, 0))
            desk_state = StudentDeskState()
            desk.add_component("StudentDeskState", desk_state)
            if i in occupied_indices:
                name = names[student_count]
                id_num = f"22-4{random.randint(100, 999)}-3"
                student_state = StudentAnimState(name, id_num, colors[student_count % len(colors)])
                student_state.is_sitting, student_state.is_writing = True, False
                desk.add_component("AnimState", student_state)
                desk_state.exam_sheet.is_visible = True
                desk_state.exam_sheet.extra_logs = [f"Name: {name}", f"ID: {id_num}"]
                desk_state.calculator.is_visible = random.choice([True, False])
                desk_state.smartphone.is_visible, desk_state.cheatsheet.is_visible = False, False
                student_count += 1
            else:
                desk_state.exam_sheet.is_visible, desk_state.calculator.is_visible, desk_state.smartphone.is_visible, desk_state.cheatsheet.is_visible = False, False, False, False
            self.add_entity(desk)
        teacher_desk = Entity("TeacherDesk")
        teacher_transform = Transform(0, 400, 0)
        teacher_transform.yaw = 180
        teacher_desk.add_component("Transform", teacher_transform)
        teacher_desk.add_component("TeacherDeskState", TeacherDeskState())
        self.add_entity(teacher_desk)

    def hard_reset(self):
        self.state, self.previous_state, self.frame_count = self.STATE_MENU, self.STATE_MENU, 0.0
        self.objective_text, self.is_exam_started, self.rounds_completed, self.is_round_active, self.consecutive_normals = "OBJECTIVE: Start the exam at your desk.", False, 0, False, 0
        self.disqualified_students, self.exam_time_left, self.current_rules_page = [], 60, 0
        self.target_student, self.target_desk_entity, self.inspection_selected_index, self.is_viewing_item = None, None, 0, False
        self.entities = []
        self.baseline_manager, self.anomaly_manager = BaselineManager(), AnomalyManager()
        self.player = Entity("Player")
        start_transform = Transform(0, 255, 100)
        start_transform.yaw = 180
        start_transform.radius = 20.0
        self.player.add_component("Transform", start_transform)
        self.add_entity(self.player)
        self.setup_classroom()
        for entity in self.entities:
            tds = entity.get_component("TeacherDeskState")
            if tds: tds.timer.total_seconds = float(self.exam_time_left * 60)

    def handle_mouse_click(self, button, state, x, y, width, height):
        if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN: return
        ui_y = height - y
        if self.state == self.STATE_MENU:
            btn_w, btn_h = 200, 50
            if (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 <= ui_y <= height/2 + btn_h):
                self.previous_state, self.state, self.current_rules_page = self.STATE_MENU, self.STATE_RULES, 0
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 70 <= ui_y <= height/2 - 70 + btn_h): os._exit(0)
        elif self.state == self.STATE_PAUSE:
            btn_w, btn_h = 200, 50
            if (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 + 60 <= ui_y <= height/2 + 60 + btn_h): self.state = self.STATE_PLAYING
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 10 <= ui_y <= height/2 - 10 + btn_h):
                self.previous_state, self.state, self.current_rules_page = self.STATE_PAUSE, self.STATE_RULES, 0
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 80 <= ui_y <= height/2 - 80 + btn_h):
                self.hard_reset(); self.state = self.STATE_PLAYING
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 150 <= ui_y <= height/2 - 150 + btn_h): os._exit(0)
        elif self.state == self.STATE_RULES:
            margin, btn_w, btn_h = 50, 120, 40
            if (margin <= x <= margin + btn_w) and (margin <= ui_y <= margin + btn_h):
                if self.current_rules_page > 0: self.current_rules_page -= 1
                else: self.state = self.previous_state
            elif (width - margin - btn_w <= x <= width - margin) and (margin <= ui_y <= margin + btn_h):
                if self.current_rules_page < len(self.rules_pages) - 1: self.current_rules_page += 1
            elif (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (margin <= ui_y <= margin + btn_h): self.state = self.STATE_PLAYING
        elif self.state == self.STATE_VICTORY:
            btn_w, btn_h = 200, 50
            if (width/2 - btn_w/2 <= x <= width/2 + btn_w/2) and (height/2 - 140 <= ui_y <= height/2 - 140 + btn_h): self.hard_reset()

    def handle_key(self, key):
        if self.state == self.STATE_INSPECTING:
            if key == b"\r": self.is_viewing_item = True
            elif key in [b"\x08", b"\x1b", b" "]:
                if self.is_viewing_item: self.is_viewing_item = False
                else: self.state = self.STATE_PLAYING
            elif key == b"q": self.state = self.STATE_PLAYING

    def handle_special_key(self, key):
        if self.state == self.STATE_INSPECTING and not self.is_viewing_item:
            menu_size = len(self.inspection_renderer.available_items)
            if menu_size > 0:
                if key == GLUT_KEY_UP: self.inspection_selected_index = (self.inspection_selected_index - 1) % menu_size
                elif key == GLUT_KEY_DOWN: self.inspection_selected_index = (self.inspection_selected_index + 1) % menu_size

    def is_laptop_active(self):
        for entity in self.entities:
            tds = entity.get_component("TeacherDeskState")
            if tds and tds.laptop.is_being_used: return True
        return False

    def interact(self):
        if self.state != self.STATE_PLAYING: return
        pt = self.player.get_component("Transform")
        for entity in self.entities:
            tds = entity.get_component("TeacherDeskState")
            if tds:
                dt = entity.get_component("Transform")
                if math.hypot(pt.x - dt.x, pt.y - dt.y) < 160.0:
                    if not self.is_exam_started:
                        for e in self.entities:
                            anim = e.get_component("AnimState")
                            if anim: anim.is_writing = True
                        self.baseline_manager.capture_classroom(self.entities)
                        self.is_exam_started = True
                        self.objective_text = "OBJECTIVE: Monitor the students. Catch any cheaters."
                    tds.laptop.start_work()
                    return

    def inspect_student(self):
        if not self.target_desk_entity or not self.target_student: return
        self.state, self.inspection_selected_index, self.is_viewing_item = self.STATE_INSPECTING, 0, False

    def disqualify_student(self):
        if not self.target_desk_entity or not self.target_student: return
        print(f"[GameManager] Disqualifying {self.target_student.name}")
        ds = self.target_desk_entity.get_component("StudentDeskState")
        self.disqualified_students.append((self.target_desk_entity.id, self.target_student, copy.deepcopy(ds)))
        del self.target_desk_entity.components["AnimState"]
        if ds: ds.exam_sheet.is_visible, ds.calculator.is_visible, ds.smartphone.is_visible, ds.cheatsheet.is_visible = False, False, False, False
        self.target_student, self.target_desk_entity = None, None

    def dismiss_laptop(self):
        if self.state != self.STATE_PLAYING: return
        for entity in self.entities:
            tds = entity.get_component("TeacherDeskState")
            if tds and tds.laptop.is_being_used and tds.laptop.is_work_done:
                if self.is_exam_started: self._evaluate_round()
                self._trigger_round_roll()
                tds.laptop.finish()
                self.is_round_active = False
                return

    def check_collision(self, next_x, next_y):
        """Simple box collision for desks."""
        for entity in self.entities:
            if "StudentDesk" in entity.id or "TeacherDesk" in entity.id:
                et = entity.get_component("Transform")
                # Student desks 70x40, Teacher desk 80x50. Using half-widths for AABB.
                w, d = (35 + 15, 20 + 15) if "Student" in entity.id else (40 + 15, 25 + 15)
                if (et.x - w < next_x < et.x + w) and (et.y - d < next_y < et.y + d):
                    return True
        return False

    def update(self, dt, keys):
        if self.state != self.STATE_PLAYING: return
        self.frame_count += dt * 60.0
        for entity in self.entities:
            tds = entity.get_component("TeacherDeskState")
            if tds: tds.update(dt)
        pt = self.player.get_component("Transform")
        if not self.is_laptop_active():
            MOVE_SPEED, ROTATE_SPEED = 200.0, 120.0
            yr, pr = math.radians(pt.yaw), math.radians(pt.pitch)
            fx, fy, rx, ry = math.sin(yr), math.cos(yr), math.cos(yr), -math.sin(yr)
            dx, dy = 0, 0
            if keys.get(b"w"): dx += fx * MOVE_SPEED * dt; dy += fy * MOVE_SPEED * dt
            if keys.get(b"s"): dx -= fx * MOVE_SPEED * dt; dy -= fy * MOVE_SPEED * dt
            if keys.get(b"a"): dx -= rx * MOVE_SPEED * dt; dy -= ry * MOVE_SPEED * dt
            if keys.get(b"d"): dx += rx * MOVE_SPEED * dt; dy += ry * MOVE_SPEED * dt
            
            # --- Collision Check with Sliding ---
            new_x, new_y = pt.x + dx, pt.y + dy
            if not self.check_collision(new_x, new_y):
                pt.x, pt.y = new_x, new_y
            else:
                # Try sliding on X
                if not self.check_collision(new_x, pt.y): pt.x = new_x
                # Try sliding on Y
                elif not self.check_collision(pt.x, new_y): pt.y = new_y

            if keys.get("left"): pt.yaw -= ROTATE_SPEED * dt
            if keys.get("right"): pt.yaw += ROTATE_SPEED * dt
            if keys.get("up"): pt.pitch = min(pt.pitch + ROTATE_SPEED * dt, 80.0)
            if keys.get("down"): pt.pitch = max(pt.pitch - ROTATE_SPEED * dt, -80.0)
            self.target_student, self.target_desk_entity = None, None
            bd, ir = 0.95, 120.0
            lx, ly, lz = math.sin(yr) * math.cos(pr), math.cos(yr) * math.cos(pr), math.sin(pr)
            for entity in self.entities:
                anim = entity.get_component("AnimState")
                if anim:
                    et = entity.get_component("Transform")
                    if math.hypot(pt.x - et.x, pt.y - et.y) < ir:
                        ex, ey, ez = et.x, et.y - 25, 80
                        vx, vy, vz = ex - pt.x, ey - pt.y, ez - pt.z
                        d = math.sqrt(vx*vx + vy*vy + vz*vz)
                        if d > 0:
                            vx/=d; vy/=d; vz/=d; dot = lx*vx + ly*vy + lz*vz
                            if dot > bd: bd, self.target_student, self.target_desk_entity = dot, anim, entity
            margin = 30; hw, hd = self.room_width/2 - margin, self.room_depth/2 - margin
            if pt.x < -hw: pt.x = -hw
            if pt.x > hw: pt.x = hw
            if pt.y < -hd: pt.y = -hd
            if pt.y > hd: pt.y = hd

    def render(self, width, height):
        if self.state == self.STATE_MENU: self.ui_renderer.render_menu(width, height)
        elif self.state == self.STATE_RULES:
            label = "Resume" if self.previous_state == self.STATE_PAUSE else "Start"
            self.ui_renderer.render_rules(width, height, self.rules_pages[self.current_rules_page], self.current_rules_page, len(self.rules_pages), label)
        elif self.state == self.STATE_PAUSE: self._render_3d_scene(); self.ui_renderer.render_pause_menu(width, height)
        elif self.state == self.STATE_PLAYING: self._render_3d_scene(); self._render_hud(width, height)
        elif self.state == self.STATE_VICTORY: self.ui_renderer.render_victory(width, height)
        elif self.state == self.STATE_INSPECTING:
            ds = self.target_desk_entity.get_component("StudentDeskState")
            if self.is_viewing_item: self.inspection_renderer.render_item_inspection(width, height, self.inspection_selected_index, ds)
            else: self._render_3d_scene(); self.inspection_renderer.render_menu(width, height, self.inspection_selected_index, ds)

    def _render_hud(self, width, height):
        self._draw_objective(width, height)
        pt = self.player.get_component("Transform")
        if self.target_student:
            self._draw_name_tag(width, height, self.target_student)
            p = "[Q] Inspect"
            if self.is_exam_started: p += "  [F] Disqualify"
            self._draw_prompt(width, height, p, y_offset=180)
        for entity in self.entities:
            tds = entity.get_component("TeacherDeskState")
            if tds:
                lp = tds.laptop
                if lp.is_being_used: self.laptop_renderer.render(entity.get_component("Transform"), lp, width, height)
                else:
                    dt = entity.get_component("Transform")
                    if math.hypot(pt.x - dt.x, pt.y - dt.y) < 160.0: self._draw_prompt(width, height, "[E] Use Laptop")

    def _draw_objective(self, w, h):
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); glOrtho(0, w, 0, h, -1, 1); glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity(); glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glColor4f(0, 0, 0, 0.4); glBegin(GL_QUADS); glVertex2f(20, h - 60); glVertex2f(500, h - 60); glVertex2f(500, h - 20); glVertex2f(20, h - 20); glEnd(); glDisable(GL_BLEND); glColor3f(1, 1, 0); glRasterPos2f(30, h - 45)
        for char in self.objective_text: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glEnable(GL_DEPTH_TEST); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW); glPopMatrix()

    def _draw_name_tag(self, w, h, s):
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); glOrtho(0, w, 0, h, -1, 1); glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity(); glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glColor4f(0, 0, 0, 0.7); pw, ph = 300, 60; px, py = w/2 - pw/2, h - 100; glBegin(GL_QUADS); glVertex2f(px, py); glVertex2f(px + pw, py); glVertex2f(px + pw, py + ph); glVertex2f(px, py + ph); glEnd(); glDisable(GL_BLEND); glColor3f(1, 1, 1); nt, it = f"NAME: {s.name}", f"ID: {s.id_number}"; glRasterPos2f(px + 20, py + 35)
        for char in nt: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glRasterPos2f(px + 20, py + 12)
        for char in it: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        glEnable(GL_DEPTH_TEST); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW); glPopMatrix()

    def _draw_prompt(self, w, h, t, y_offset=50):
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); glOrtho(0, w, 0, h, -1, 1); glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity(); glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glColor4f(0, 0, 0, 0.6); bw, bh = 250 if "Q" in t else 200, 40; bx, by = w/2 - bw/2, y_offset; glBegin(GL_QUADS); glVertex2f(bx, by); glVertex2f(bx + bw, by); glVertex2f(bx + bw, by + bh); glVertex2f(bx, by + bh); glEnd(); glDisable(GL_BLEND); glColor3f(1, 1, 1); glRasterPos2f(bx + 20, by + 15)
        for char in t: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glEnable(GL_DEPTH_TEST); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW); glPopMatrix()

    def _render_room(self):
        glColor3f(0.3, 0.3, 0.3); glBegin(GL_QUADS); glVertex3f(-self.room_width/2, self.room_depth/2, 0); glVertex3f(self.room_width/2, self.room_depth/2, 0); glVertex3f(self.room_width/2, -self.room_depth/2, 0); glVertex3f(-self.room_width/2, -self.room_depth/2, 0); glEnd(); glColor3f(0.4, 0.4, 0.4); glBegin(GL_QUADS); glVertex3f(-self.room_width/2, self.room_depth/2, self.wall_height); glVertex3f(self.room_width/2, self.room_depth/2, self.wall_height); glVertex3f(self.room_width/2, -self.room_depth/2, self.wall_height); glVertex3f(-self.room_width/2, -self.room_depth/2, self.wall_height); glEnd(); glColor3f(0.55, 0.55, 0.6); hw, hd, wh = self.room_width / 2, self.room_depth / 2, self.wall_height
        glBegin(GL_QUADS); glVertex3f(-hw, hd, 0); glVertex3f(hw, hd, 0); glVertex3f(hw, hd, wh); glVertex3f(-hw, hd, wh); glVertex3f(-hw, -hd, 0); glVertex3f(hw, -hd, 0); glVertex3f(hw, -hd, wh); glVertex3f(-hw, -hd, wh); glVertex3f(-hw, -hd, 0); glVertex3f(-hw, hd, 0); glVertex3f(-hw, hd, wh); glVertex3f(-hw, -hd, wh); glVertex3f(hw, -hd, 0); glVertex3f(hw, hd, 0); glVertex3f(hw, hd, wh); glVertex3f(hw, -hd, wh); glEnd(); glColor3f(0.1, 0.1, 0.1); glLineWidth(3.0); glBegin(GL_LINES)
        for x in [-hw, hw]:
            for y in [-hd, hd]: glVertex3f(x, y, 0); glVertex3f(x, y, wh)
        glEnd(); glColor3f(0.1, 0.15, 0.1); glBegin(GL_QUADS); glVertex3f(-250, hd - 1, 50); glVertex3f(250, hd - 1, 50); glVertex3f(250, hd - 1, 150); glVertex3f(-250, hd - 1, 150); glEnd(); glColor3f(0.2, 0.2, 0.2); glBegin(GL_LINES)
        for i in range(int(-hw), int(hw) + 1, 50): glVertex3f(i, -hd, 0.5); glVertex3f(i, hd, 0.5)
        for i in range(int(-hd), int(hd) + 1, 50): glVertex3f(-hw, i, 0.5); glVertex3f(hw, i, 0.5)
        glEnd()

    def _render_3d_scene(self):
        self._render_room()
        for entity in self.entities:
            if entity.id == "Player": continue
            transform = entity.get_component("Transform")
            anim = entity.get_component("AnimState")
            sd = entity.get_component("StudentDeskState")
            td = entity.get_component("TeacherDeskState")
            if transform and sd: self.student_desk_renderer.render(transform, sd)
            if transform and anim: self.student_renderer.render(transform, anim, self.frame_count)
            if transform and td: self.teacher_desk_renderer.render(transform, td)

    def _trigger_round_roll(self):
        self.is_round_active = True
        print("\n" + "="*40 + "\n   NEW ROUND: ANOMALY ROLL\n" + "="*40)
        print(self.anomaly_manager.get_probability_string())
        self.current_round_anomaly, roll = None, random.random()
        if self.consecutive_normals >= 2: print("[Game] FORCING ANOMALY: Too many consecutive normal rounds."); roll = 0.0
        if roll < 0.60:
            self.consecutive_normals = 0
            choice = self.anomaly_manager.pick_anomaly()
            self.current_round_anomaly = choice
            print(f"\n[Game] ROLL: ANOMALY SELECTED -> {choice}")
            affected = self.anomaly_manager.apply_anomaly(choice, self.entities, self)
            if not affected: print("[Game] Roll failed (No eligible students). Room stays NORMAL."); self.current_round_anomaly, self.consecutive_normals = None, self.consecutive_normals + 1
            else: print(f"[Game] Applied {choice} to: {[e.id for e in affected]}")
        else: self.consecutive_normals += 1; print(f"\n[Game] ROLL: NO ANOMALY. Room stays NORMAL. (Consecutive: {self.consecutive_normals})")
        self._log_room_state("BASELINE (NORMAL)", is_baseline=True); self._log_room_state("CURRENT STATE"); print("\n" + "="*40 + "\n")

    def _log_room_state(self, header, is_baseline=False):
        print(f"\n--- {header} ---")
        for row in range(4):
            line = []
            for col in range(4):
                id = f"StudentDesk_{row}_{col}"
                if is_baseline:
                    snap = self.baseline_manager.snapshot.get(id)
                    s = snap["anim_state"] if snap else None
                else:
                    e = next((ent for ent in self.entities if ent.id == id), None)
                    s = e.get_component("AnimState") if e else None
                name = s.name[:5] if s else "EMPTY"
                line.append(f"{id[-3:]}: {name:5}")
            print(" | ".join(line))

    def _evaluate_round(self):
        if self.rounds_completed == 0:
            print("[Game] Exam Initialized. No evaluation for Round 0."); self.rounds_completed += 1; return
        print("\n--- EVALUATING ROUND ---"); is_failure = False
        for entity in self.entities:
            if "StudentDesk" in entity.id:
                anim = entity.get_component("AnimState")
                if anim and self.baseline_manager.is_desk_anomalous(entity): print(f"[Evaluation] MISSED ANOMALY: Student {anim.name} at {entity.id} is anomalous!"); is_failure = True; break
        if not is_failure:
            for desk_id, student, evidence in self.disqualified_students:
                temp = Entity(desk_id)
                temp.add_component("AnimState", student); temp.add_component("StudentDeskState", evidence)
                if not self.baseline_manager.is_desk_anomalous(temp): print(f"[Evaluation] FALSE ACCUSATION! {student.name} was innocent at {desk_id}."); is_failure = True; break
        if is_failure:
            print("[Evaluation] PHASE FAILED. Resetting to 60 minutes."); self.exam_time_left, self.rounds_completed = 60, 1; self._reset_classroom()
        else:
            print("[Evaluation] PHASE SUCCESS! -10 Minutes."); self.exam_time_left, self.rounds_completed = max(0, self.exam_time_left - 10), self.rounds_completed + 1
            if self.current_round_anomaly: self.anomaly_manager.scale_probabilities(self.current_round_anomaly); print(f"[Game] Scaling probabilities: {self.current_round_anomaly} reduced to 2%.")
            if self.exam_time_left == 0: print("!!! VICTORY !!!"); self.state = self.STATE_VICTORY
        self.disqualified_students = []
        for entity in self.entities:
            tds = entity.get_component("TeacherDeskState")
            if tds: tds.timer.total_seconds = float(self.exam_time_left * 60)

    def _reset_classroom(self):
        print("[Game] Resetting classroom to baseline...")
        self.baseline_manager.restore_classroom(self.entities); self.disqualified_students = []
        for e in self.entities:
            anim = e.get_component("AnimState")
            if anim: anim.is_writing = True
