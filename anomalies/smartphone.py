import random
from anomalies.base_anomaly import BaseAnomaly

class SmartphoneAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("Smartphone")

    def get_eligible_entities(self, entities):
        """Eligible entities are desks with students who HAVE a calculator."""
        eligible = []
        for e in entities:
            anim = e.get_component("AnimState")
            desk_state = e.get_component("StudentDeskState")
            if anim and desk_state and desk_state.calculator.is_visible:
                eligible.append(e)
        return eligible

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)
        
        if not eligible:
            return []

        # Affect at most 1 student
        target_desk = random.choice(eligible)
        desk_state = target_desk.get_component("StudentDeskState")
        student_state = target_desk.get_component("AnimState")
        
        print(f"[Anomaly] SMARTPHONE SWAP: {student_state.name}'s calculator turned into a SMARTPHONE at {target_desk.id}")
        
        # Transformation: Replace calculator with smartphone
        desk_state.calculator.is_visible = False
        desk_state.smartphone.is_visible = True

        return [target_desk]
