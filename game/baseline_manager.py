import copy

class BaselineManager:
    def __init__(self):
        # A dictionary mapping desk_id to its component data snapshots
        self.snapshot = {}

    def capture_classroom(self, entities):
        """Snapshots the 16 desks and their contents."""
        self.snapshot = {}
        for entity in entities:
            if "StudentDesk" in entity.id:
                data = {
                    "transform": copy.deepcopy(entity.get_component("Transform")),
                    "desk_state": copy.deepcopy(entity.get_component("StudentDeskState")),
                    "anim_state": copy.deepcopy(entity.get_component("AnimState")) # Might be None
                }
                self.snapshot[entity.id] = data

    def restore_classroom(self, entities):
        """Overwrites current entity components with the snapshot data."""
        for entity in entities:
            if entity.id in self.snapshot:
                snap = self.snapshot[entity.id]
                
                # Restore Transform
                t = entity.get_component("Transform")
                t.x, t.y, t.z = snap["transform"].x, snap["transform"].y, snap["transform"].z
                t.yaw, t.pitch = snap["transform"].yaw, snap["transform"].pitch
                
                # Restore Desk State (Calculator, etc.)
                entity.add_component("StudentDeskState", copy.deepcopy(snap["desk_state"]))
                
                # Restore Student State
                if snap["anim_state"]:
                    entity.add_component("AnimState", copy.deepcopy(snap["anim_state"]))
                elif entity.get_component("AnimState"):
                    # If the desk was empty in baseline but has a student now, remove the student
                    del entity.components["AnimState"]

    def is_desk_anomalous(self, entity):
        """Fundamental check: Does this entity differ from its fair baseline?"""
        if entity.id not in self.snapshot:
            return False
            
        snap = self.snapshot[entity.id]
        current_anim = entity.get_component("AnimState")
        current_desk = entity.get_component("StudentDeskState")
        
        # 1. Presence / Occupancy check
        if (snap["anim_state"] is None) != (current_anim is None):
            print(f"[Trace] {entity.id}: Occupancy mismatch. Baseline: {snap['anim_state'] is not None}, Current: {current_anim is not None}")
            return True
            
        # 2. Identity & State flags (If both have students)
        if snap["anim_state"] and current_anim:
            s = snap["anim_state"]
            c = current_anim
            if s.name != c.name: 
                print(f"[Trace] {entity.id}: Name mismatch. Baseline: {s.name}, Current: {c.name}"); return True
            if s.id_number != c.id_number: 
                print(f"[Trace] {entity.id}: ID mismatch. Baseline: {s.id_number}, Current: {c.id_number}"); return True
            if s.cloth_color != c.cloth_color: 
                print(f"[Trace] {entity.id}: Cloth mismatch. Baseline: {s.cloth_color}, Current: {c.cloth_color}"); return True
            if s.pen_color != c.pen_color: 
                print(f"[Trace] {entity.id}: Pen mismatch. Baseline: {s.pen_color}, Current: {c.pen_color}"); return True
            if s.is_alien != c.is_alien: 
                print(f"[Trace] {entity.id}: Alien flag mismatch. Baseline: {s.is_alien}, Current: {c.is_alien}"); return True
            if s.is_dancing != c.is_dancing: 
                print(f"[Trace] {entity.id}: Dancing flag mismatch. Baseline: {s.is_dancing}, Current: {c.is_dancing}"); return True
            if s.is_ghost != c.is_ghost: 
                print(f"[Trace] {entity.id}: Ghost flag mismatch. Baseline: {s.is_ghost}, Current: {c.is_ghost}"); return True
            
        # 3. Item Configuration
        if snap["desk_state"] and current_desk:
            s_d = snap["desk_state"]
            c_d = current_desk
            if s_d.calculator.is_visible != c_d.calculator.is_visible: 
                print(f"[Trace] {entity.id}: Calc visibility mismatch."); return True
            if s_d.smartphone.is_visible != c_d.smartphone.is_visible: 
                print(f"[Trace] {entity.id}: Phone visibility mismatch."); return True
            if s_d.cheatsheet.is_visible != c_d.cheatsheet.is_visible: 
                print(f"[Trace] {entity.id}: Cheatsheet visibility mismatch."); return True
            if s_d.exam_sheet.extra_logs != c_d.exam_sheet.extra_logs: 
                print(f"[Trace] {entity.id}: Exam sheet logs mismatch."); return True
        
        return False
