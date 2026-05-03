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
        """Helper to check if a specific desk differs from the baseline."""
        if entity.id not in self.snapshot:
            return False
            
        snap = self.snapshot[entity.id]
        current_anim = entity.get_component("AnimState")
        
        # 1. Occupancy check
        if (snap["anim_state"] is None) != (current_anim is None):
            return True
            
        # 2. Student Identity check
        if snap["anim_state"] and current_anim:
            if snap["anim_state"].name != current_anim.name: return True
            if snap["anim_state"].id_number != current_anim.id_number: return True
            if snap["anim_state"].cloth_color != current_anim.cloth_color: return True
            if snap["anim_state"].pen_color != current_anim.pen_color: return True
            if snap["anim_state"].is_alien != current_anim.is_alien: return True
            if snap["anim_state"].is_ghost != current_anim.is_ghost: return True
            if snap["anim_state"].is_dancing != current_anim.is_dancing: return True
            
        # 3. Desk Items check
        current_desk = entity.get_component("StudentDeskState")
        snap_desk = snap["desk_state"]
        if snap_desk.calculator.is_visible != current_desk.calculator.is_visible: return True
        if snap_desk.smartphone.is_visible != current_desk.smartphone.is_visible: return True
        if snap_desk.cheatsheet.is_visible != current_desk.cheatsheet.is_visible: return True
        
        # Check Exam Sheet Logs
        if snap_desk.exam_sheet.extra_logs != current_desk.exam_sheet.extra_logs: return True
        
        return False
