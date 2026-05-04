import random
from anomalies.base_anomaly import BaseAnomaly

class CheatSheetAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("CheatSheet")

    def get_eligible_entities(self, entities):
        eligible = []
        for e in entities:
            anim = e.get_component("AnimState")
            desk_state = e.get_component("StudentDeskState")
            if anim and desk_state and not desk_state.cheatsheet.is_visible:
                eligible.append(e)
        return eligible

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)
        
        if not eligible:
            return []

        target_desk = random.choice(eligible)
        desk_state = target_desk.get_component("StudentDeskState")
        student_state = target_desk.get_component("AnimState")
        
        print(f"[Anomaly] Cheat Sheet appeared for {student_state.name} at {target_desk.id}")
        desk_state.cheatsheet.is_visible = True

        return [target_desk]
